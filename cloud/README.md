# CloudFormation Templates

This directory contains AWS CloudFormation templates for setting up various AWS resources, such as IAM roles and policies. Each template is designed to create specific IAM roles and permissions. Additionally, corresponding IAM policies are provided in JSON format for reference.

### Folder Structure
cloud
├── aws
│   ├── cloudformation
│   │   ├── sedai-integration-billing-account-s3-and-api.yaml
│   │   ├── sedai-integration-service-role-autonomous.yml
│   │   ├── sedai-integration-service-role-readonly.yml
│   │   ├── sedai-policy-autonomous.json
│   │   ├── sedai-policy-billing-account-s3-and-api.json
│   │   └── sedai-policy-readonly.json

### CloudFormation Templates

The CloudFormation templates in this directory deploy IAM roles and policies for different services. The templates and their respective purposes are:

- **sedai-integration-billing-account-s3-and-api.yml**: Creates the IAM role and permissions for billing account integration with S3 and API Gateway.
- **sedai-integration-service-role-autonomous.yml**: Creates an IAM role with autonomous service permissions.
- **sedai-integration-service-role-readonly.yml**: Creates a read-only IAM role for specific services.

Each template has a corresponding JSON file that represents the IAM policy created by that template.

### Usage

To deploy one of the CloudFormation templates:

1. Navigate to the AWS Management Console.
2. Open the **CloudFormation** service.
3. Choose **Create stack** and then **With new resources (standard)**.
4. In the **Specify template** section, upload the desired YAML file:
   - `sedai-integration-billing-account-s3-and-api.yml`
   - `sedai-integration-service-role-autonomous.yml`
   - `sedai-integration-service-role-readonly.yml`
5. Follow the on-screen instructions to configure stack details and parameters.
6. Review and create the stack.

Alternatively, you can deploy the templates using the AWS CLI:

```bash
aws cloudformation create-stack --stack-name <stack-name> --template-body file://<template-file>.yml
```

Replace <stack-name> with your desired stack name and <template-file> with the name of the template you want to deploy.

For more complex deployments that involve user input to customize permissions, refer to the nested folder for further information.