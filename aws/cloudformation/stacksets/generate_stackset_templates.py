#!/usr/bin/env python3
"""
Generate the Sedai StackSet IAM-role templates from this repo's policy includes.

The read-only vs read-write policy for each service is defined in
    aws/cloudformation/nested/sedai-integration-main.yml
under `Mappings.PolicyReadOnlyMap`, which points at per-service include files
    aws/cloudformation/nested/sedai-integration-include-<service>-<r|rw>.json
Those include files are the source of truth.

This script reads that mapping, resolves each entry to its local include file,
merges all statements for a mode into a single inline policy, and wraps it in a
self-contained StackSet role template:

    readonly  -> iam-role-template-ro.yaml   (SedaiReadOnly includes)
    readwrite -> iam-role-template-rw.yaml   (SedaiReadWrite includes)

The output is published to S3 by .github/workflows/update_s3.yml (it lives under
aws/cloudformation/, which the workflow mirrors to the onboarding bucket). The
templates are build artifacts -- they are generated in CI and are not committed.

Usage:
    generate_stackset_templates.py [--out DIR]

--out defaults to this script's directory (aws/cloudformation/stacksets/).
"""

import argparse
import json
import os
import sys

import yaml

# --- constants shared by every StackSet template -------------------------------
SEDAI_ACCOUNT_ID = "504216784688"
ROLE_NAME = "sedai-integration-service-role"
POLICY_NAME = "sedai-integration-service-policy"

# Order in which services are concatenated into the merged policy.
SERVICE_ORDER = [
    "Common", "Lambda", "ECS", "DynamoDB",
    "EC2Instance", "S3Storage", "EBSStorage", "RDS",
]

MODES = {
    "readonly": ("SedaiReadOnly", "iam-role-template-ro.yaml"),
    "readwrite": ("SedaiReadWrite", "iam-role-template-rw.yaml"),
}

# Paths resolved relative to this script: <root>/aws/cloudformation/stacksets/<this>
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NESTED_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "nested"))
MAIN_TEMPLATE = os.path.join(NESTED_DIR, "sedai-integration-main.yml")

# IAM aggregate inline-policy size limit for a role (whitespace excluded).
INLINE_POLICY_LIMIT = 10240


class _CfnLoader(yaml.SafeLoader):
    """SafeLoader that tolerates CloudFormation short-form tags (!Sub, !If, ...).

    We only read the plain-string Mappings section, so we don't need to
    interpret the intrinsics -- just avoid choking on them.
    """


def _ignore_cfn_tag(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


_CfnLoader.add_multi_constructor("!", _ignore_cfn_tag)


def load_mapping():
    if not os.path.isfile(MAIN_TEMPLATE):
        sys.exit(f"error: main template not found: {MAIN_TEMPLATE}")
    with open(MAIN_TEMPLATE) as fh:
        doc = yaml.load(fh, Loader=_CfnLoader)
    try:
        return doc["Mappings"]["PolicyReadOnlyMap"]
    except (KeyError, TypeError):
        sys.exit(f"error: PolicyReadOnlyMap not found in {MAIN_TEMPLATE}")


def include_path_for(url):
    """Resolve an S3/https include URL to its local file under nested/."""
    return os.path.join(NESTED_DIR, os.path.basename(url))


def ordered_services(mapping):
    """Every service in the mapping, ordered by SERVICE_ORDER first.

    Services present in the mapping but unknown to SERVICE_ORDER are appended
    (and flagged) rather than silently dropped -- so a new service added to
    PolicyReadOnlyMap still makes it into the templates.
    """
    known = [s for s in SERVICE_ORDER if s in mapping]
    extra = sorted(s for s in mapping if s not in SERVICE_ORDER)
    for s in extra:
        print(f"  ! service '{s}' is in PolicyReadOnlyMap but not in "
              f"SERVICE_ORDER -- appended; add it to SERVICE_ORDER to fix ordering")
    return known + extra


def merge_statements(mapping, mode_key):
    """Concatenate the Statement arrays of every service's include for a mode.

    Exact-duplicate statements are dropped. A Sid reused with differing content
    aborts the build (CloudFormation requires unique Sids per policy document).
    """
    statements = []
    seen = []           # list of serialized statements, for exact-dup detection
    sids = {}           # Sid -> serialized content, for collision detection
    for service in ordered_services(mapping):
        entry = mapping.get(service)
        if not entry or mode_key not in entry:
            sys.exit(f"error: service '{service}' in PolicyReadOnlyMap has no "
                     f"'{mode_key}' entry -- refusing to silently drop it; "
                     f"fix the mapping in {os.path.basename(MAIN_TEMPLATE)}")
        path = include_path_for(entry[mode_key])
        if not os.path.isfile(path):
            sys.exit(f"error: include file not found: {path}")
        with open(path) as fh:
            doc = json.load(fh)
        for stmt in doc.get("Statement", []):
            blob = json.dumps(stmt, sort_keys=True)
            if blob in seen:
                continue  # identical statement already included
            sid = stmt.get("Sid")
            if sid is not None:
                if sid in sids and sids[sid] != blob:
                    sys.exit(f"error: duplicate Sid '{sid}' with differing content "
                             f"across includes -- CloudFormation rejects duplicate "
                             f"Sids in one policy document; rename or fix upstream")
                sids[sid] = blob
            seen.append(blob)
            statements.append(stmt)
    return statements


def verify_written(dest, expected_count):
    """Re-parse the written file and confirm it has the expected shape and size.

    Guards against a template that was written but is malformed or truncated --
    we would rather fail the build than publish a broken policy.
    """
    try:
        with open(dest) as fh:
            doc = yaml.load(fh, Loader=_CfnLoader)
        stmts = (doc["Resources"]["SedaiIntegrationServiceRole"]
                 ["Properties"]["Policies"][0]["PolicyDocument"]["Statement"])
    except Exception as exc:
        sys.exit(f"error: {dest} failed post-write verification -- could not parse "
                 f"the expected role/policy shape: {exc}")
    if not isinstance(stmts, list) or len(stmts) != expected_count:
        got = len(stmts) if isinstance(stmts, list) else "non-list"
        sys.exit(f"error: {dest} has {got} statements after write, "
                 f"expected {expected_count}")


def render_statements_yaml(statements, indent):
    body = yaml.safe_dump(
        statements, default_flow_style=False, sort_keys=False, width=4096
    )
    pad = " " * indent
    return "".join(pad + line + "\n" for line in body.splitlines())


def build_template(statements, mode):
    stmts_yaml = render_statements_yaml(statements, indent=14)
    return f"""AWSTemplateFormatVersion: '2010-09-09'
Description: Template to create IAM role for Sedai across customer AWS accounts using StackSets ({mode})
# GENERATED by aws/cloudformation/stacksets/generate_stackset_templates.py -- do not edit by hand.
Resources:
  SedaiIntegrationServiceRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: {ROLE_NAME}
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              AWS:
                - {SEDAI_ACCOUNT_ID} # Sedai's AWS account ID
            Action:
              - sts:AssumeRole
            Condition:
              StringEquals:
                sts:ExternalId: !Sub ext-${{AWS::AccountId}}
      Path: "/"
      Policies:
        - PolicyName: {POLICY_NAME}
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
{stmts_yaml}Outputs:
  SedaiIntegrationServiceRoleArn:
    Description: "ARN of the Sedai Integration Service Role"
    Value: !GetAtt SedaiIntegrationServiceRole.Arn
    Export:
      Name: SedaiIntegrationServiceRoleArn
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=SCRIPT_DIR,
                    help="output directory for the templates (default: this script's dir)")
    args = ap.parse_args()

    out = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(out, exist_ok=True)

    mapping = load_mapping()

    for mode, (mode_key, filename) in MODES.items():
        print(f"[{mode}] merging {mode_key} includes:")
        statements = merge_statements(mapping, mode_key)
        if not statements:
            sys.exit(f"error: [{mode}] produced no statements -- check "
                     f"PolicyReadOnlyMap and the include files")
        size = len(json.dumps(
            {"Version": "2012-10-17", "Statement": statements},
            separators=(",", ":")))
        if size > INLINE_POLICY_LIMIT:
            sys.exit(f"error: [{mode}] inline policy is {size} chars, over the "
                     f"{INLINE_POLICY_LIMIT}-char IAM inline-policy limit -- "
                     f"split into multiple policies")
        template = build_template(statements, mode)
        dest = os.path.join(out, filename)
        with open(dest, "w") as fh:
            fh.write(template)
        verify_written(dest, len(statements))
        print(f"  -> {dest}  ({len(statements)} statements, "
              f"policy {size} chars, {round(100 * size / INLINE_POLICY_LIMIT)}% "
              f"of the {INLINE_POLICY_LIMIT}-char inline limit)  [verified]")

    print("OK: all StackSet templates generated and verified.")


if __name__ == "__main__":
    main()
