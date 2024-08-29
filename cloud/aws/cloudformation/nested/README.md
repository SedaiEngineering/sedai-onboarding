# Nested CloudFormation Templates

This folder contains a set of nested AWS CloudFormation templates that provide more granular control over IAM roles and policies. These templates allow users to selectively deploy specific permissions based on their requirements. Each template is modular, focusing on specific AWS services, and provides options for read-only (r) or read-write (rw) permissions.

### Folder Structure
```
cloud
├── aws
│   ├── cloudformation
│   │   ├── nested
│   │   │   ├── sedai-integration-include-billing-r.json
│   │   │   ├── sedai-integration-include-billing-rw.json
│   │   │   ├── sedai-integration-include-common-r.json
│   │   │   ├── sedai-integration-include-common-rw.json
│   │   │   ├── sedai-integration-include-dynamodb-r.json
│   │   │   ├── sedai-integration-include-dynamodb-rw.json
│   │   │   ├── sedai-integration-include-ec2instance-r.json
│   │   │   ├── sedai-integration-include-ec2instance-rw.json
│   │   │   ├── sedai-integration-include-ecs-r.json
│   │   │   ├── sedai-integration-include-ecs-rw.json
│   │   │   ├── sedai-integration-include-kinesis-r.json
│   │   │   ├── sedai-integration-include-kinesis-rw.json
│   │   │   ├── sedai-integration-include-kubernetes-r.json
│   │   │   ├── sedai-integration-include-kubernetes-rw.json
│   │   │   ├── sedai-integration-include-lambda-r.json
│   │   │   ├── sedai-integration-include-lambda-rw.json
│   │   │   ├── sedai-integration-include-stepfunction-r.json
│   │   │   ├── sedai-integration-include-stepfunction-rw.json
│   │   │   ├── sedai-integration-include-storageebs-r.json
│   │   │   ├── sedai-integration-include-storageebs-rw.json
│   │   │   ├── sedai-integration-include-storages3-r.json
│   │   │   ├── sedai-integration-include-storages3-rw.json
│   │   │   ├── sedai-integration-main.yml
│   │   │   ├── sedai-integration-nested-billingresource.yml
│   │   │   ├── sedai-integration-nested-inlinepolicy.yml
│   │   │   └── sedai-integration-nested-managedpolicy.yml
```
### Key Templates

- **sedai-integration-main.yml**: The main CloudFormation template that orchestrates the deployment of nested resources. This template allows users to select which permissions to deploy based on Yes/No inputs.
- **sedai-integration-nested-billingresource.yml**: A nested template for billing-related resources.
- **sedai-integration-nested-inlinepolicy.yml**: A nested template for creating inline IAM policies.
- **sedai-integration-nested-managedpolicy.yml**: A nested template for creating managed IAM policies.

### Permission Modules

The following JSON files contain the IAM policies for various AWS services. Each service has two versions: read-only (`r`) and read-write (`rw`). These policies are included in the main template (`sedai-integration-main.yml`) based on user selection:

- **Billing**
  - `sedai-integration-include-billing-r.json`
  - `sedai-integration-include-billing-rw.json`
- **Common**
  - `sedai-integration-include-common-r.json`
  - `sedai-integration-include-common-rw.json`
- **DynamoDB**
  - `sedai-integration-include-dynamodb-r.json`
  - `sedai-integration-include-dynamodb-rw.json`
- **EC2 Instances**
  - `sedai-integration-include-ec2instance-r.json`
  - `sedai-integration-include-ec2instance-rw.json`
- **ECS**
  - `sedai-integration-include-ecs-r.json`
  - `sedai-integration-include-ecs-rw.json`
- **Kinesis**
  - `sedai-integration-include-kinesis-r.json`
  - `sedai-integration-include-kinesis-rw.json`
- **Kubernetes**
  - `sedai-integration-include-kubernetes-r.json`
  - `sedai-integration-include-kubernetes-rw.json`
- **Lambda**
  - `sedai-integration-include-lambda-r.json`
  - `sedai-integration-include-lambda-rw.json`
- **Step Functions**
  - `sedai-integration-include-stepfunction-r.json`
  - `sedai-integration-include-stepfunction-rw.json`
- **Storage (EBS)**
  - `sedai-integration-include-storageebs-r.json`
  - `sedai-integration-include-storageebs-rw.json`
- **Storage (S3)**
  - `sedai-integration-include-storages3-r.json`
  - `sedai-integration-include-storages3-rw.json`

### Parameters

The `sedai-integration-main.yml` template includes the following parameters, which are grouped into two sections: **Sedai app configuration section** and **Permission section**.

#### Sedai App Configuration Section

- **UniqueExternalId**: A string parameter. Leave this empty to generate a unique external ID in the `ext-{AWSAccountID}` format.

#### Permission Section

These parameters control which permissions to grant Sedai. Each parameter is a `Yes/No` choice, with default values set to `No`. If the `ReadOnly` parameter is set to `Yes`, Sedai will only have read-only access to the specified resources, and will not be able to optimize the workloads.

- **ReadOnly**: Select Yes for read-only access or No to allow Sedai to optimize workloads.
- **LambdaRequired**: Yes or No for Lambda workload permissions.
- **DynamoDBRequired**: Yes or No for DynamoDB workload permissions.
- **EC2InstanceRequired**: Yes or No for EC2 Instance workload permissions.
- **KinesisRequired**: Yes or No for Kinesis workload permissions.
- **StepFunctionRequired**: Yes or No for Step Function workload permissions.
- **ECSRequired**: Yes or No for ECS workload permissions.
- **KubernetesRequired**: Yes or No for Kubernetes workload permissions.
- **S3StorageRequired**: Yes or No for S3 Storage workload permissions.
- **EBSStorageRequired**: Yes or No for EBS Storage workload permissions.
- **BillingRequired**: Yes or No for Billing permissions.

### Usage

To deploy the nested CloudFormation stack:

1. Navigate to the AWS Management Console.
2. Open the **CloudFormation** service.
3. Choose **Create stack** and then **With new resources (standard)**.
4. In the **Specify template** section, upload the `sedai-integration-main.yml` file.
5. During stack creation, the template will prompt you to select the specific permissions you need (e.g., Billing, EC2, Lambda, etc.). You can choose read-only or read-write access for each service.
6. Follow the on-screen instructions to configure stack details and parameters.
7. Review and create the stack.

Alternatively, you can deploy the main template using the AWS CLI:

```bash
aws cloudformation create-stack --stack-name <stack-name> --template-body file://sedai-integration-main.yml
```

Replace <stack-name> with your desired stack name.

This setup provides flexibility, allowing you to deploy only the permissions that are needed, reducing unnecessary permissions and following the principle of least privilege.