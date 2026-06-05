# AWS GitHub OIDC Setup

This guide explains how to configure AWS IAM to allow GitHub Actions to authenticate using OIDC (OpenID Connect) instead of long-lived access keys.

## Prerequisites

- AWS account with IAM permissions to create roles and policies
- GitHub repository with Actions enabled
- AWS CLI installed and configured

## Setup Steps

### 1. Create OIDC Identity Provider in AWS

If you haven't already set up the GitHub OIDC provider in your AWS account:

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**Note:** You only need to create the OIDC provider once per AWS account. It can be reused across multiple repositories.

### 2. Create IAM Role for GitHub Actions

#### a. Create Trust Policy and Role

Replace `<AWS_ACCOUNT_ID>` with your AWS account ID and `<GITHUB_ORG>/<GITHUB_REPO>` with your repository (e.g., `chriselsen/dx-location-details`):

```bash
# Create trust policy
cat > github-oidc-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<GITHUB_ORG>/<GITHUB_REPO>:*"
        }
      }
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name GitHubActions-DXLocationDetails \
  --assume-role-policy-document file://github-oidc-trust-policy.json \
  --description "Role for GitHub Actions to query AWS Direct Connect locations"
```

#### b. Create and Attach Permissions Policy

```bash
# Create permissions policy
cat > github-oidc-permissions-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "directconnect:DescribeLocations"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "account:ListRegions"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Attach the policy to the role
aws iam put-role-policy \
  --role-name GitHubActions-DXLocationDetails \
  --policy-name DXLocationQuery \
  --policy-document file://github-oidc-permissions-policy.json
```

### 3. Configure GitHub Repository

Add the IAM role ARN and credentials as GitHub Actions secrets and variables:

#### AWS Commercial Partition (OIDC)
1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository variable**
4. Name: `AWS_ROLE_ARN`
5. Value: `arn:aws:iam::<AWS_ACCOUNT_ID>:role/GitHubActions-DXLocationDetails`

Replace `<AWS_ACCOUNT_ID>` with your actual AWS account ID.

#### EU Sovereign Cloud (Access Keys)
1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:
   - Name: `AWS_EUSC_ACCESS_KEY_ID`
   - Value: Your EUSC IAM user access key ID
   - Name: `AWS_EUSC_SECRET_ACCESS_KEY`
   - Value: Your EUSC IAM user secret access key

#### China Partition (Access Keys)
1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:
   - Name: `AWS_CHINA_ACCESS_KEY_ID`
   - Value: Your China IAM user access key ID
   - Name: `AWS_CHINA_SECRET_ACCESS_KEY`
   - Value: Your China IAM user secret access key

### 4. Verify Setup

The GitHub Actions workflow is now configured to use OIDC authentication. You can verify by:

1. Triggering a manual workflow run from the Actions tab
2. Checking the workflow logs for successful AWS authentication
3. Verifying that DX location data is collected successfully

## IAM Permissions

### AWS Commercial Partition
The OIDC role has minimal permissions required:
- `directconnect:DescribeLocations` - Query Direct Connect location information
- `account:ListRegions` - List enabled AWS regions

### EU Sovereign Cloud
The IAM user requires:
- `directconnect:DescribeLocations` - Query Direct Connect location information
- `ec2:DescribeRegions` - List available regions (alternative to account:ListRegions)

### China Partition
The IAM user requires:
- `directconnect:DescribeLocations` - Query Direct Connect location information
- `ec2:DescribeRegions` - List available regions

These permissions are read-only and scoped to the minimum required for the workflow to function.

## Security Benefits

Using OIDC instead of long-lived credentials provides:

- **No stored secrets**: No AWS access keys stored in GitHub
- **Automatic rotation**: Temporary credentials expire automatically
- **Audit trail**: CloudTrail logs show which GitHub workflow assumed the role
- **Least privilege**: Role can only be assumed by specific GitHub repository
- **Revocable**: Disable access by deleting the IAM role

## Troubleshooting

### Authentication Fails

- Verify the OIDC provider exists in IAM
- Check that the role ARN in GitHub matches the created role
- Ensure trust policy has correct GitHub org/repo name
- Confirm the role has the permissions policy attached

### Missing Regions

- Verify `account:ListRegions` permission is granted
- Ensure all required AWS regions are enabled in your account

### Permission Denied

- Check CloudTrail logs for the specific API call that failed
- Verify the permissions policy includes required actions
