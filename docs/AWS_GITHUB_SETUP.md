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

#### a. Update Trust Policy

Edit `iam/github-oidc-trust-policy.json` and replace:
- `<AWS_ACCOUNT_ID>` with your AWS account ID
- `<GITHUB_ORG>/<GITHUB_REPO>` with your GitHub organization and repository name (e.g., `chriselsen/dx-location-details`)

#### b. Create the IAM Role

```bash
aws iam create-role \
  --role-name GitHubActions-DXLocationDetails \
  --assume-role-policy-document file://iam/github-oidc-trust-policy.json \
  --description "Role for GitHub Actions to query AWS Direct Connect locations"
```

#### c. Attach Permissions Policy

```bash
aws iam put-role-policy \
  --role-name GitHubActions-DXLocationDetails \
  --policy-name DXLocationQuery \
  --policy-document file://iam/github-oidc-permissions-policy.json
```

### 3. Configure GitHub Repository

Add the IAM role ARN as a GitHub Actions variable:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository variable**
4. Name: `AWS_ROLE_ARN`
5. Value: `arn:aws:iam::<AWS_ACCOUNT_ID>:role/GitHubActions-DXLocationDetails`

Replace `<AWS_ACCOUNT_ID>` with your actual AWS account ID.

### 4. Verify Setup

The GitHub Actions workflow is now configured to use OIDC authentication. You can verify by:

1. Triggering a manual workflow run from the Actions tab
2. Checking the workflow logs for successful AWS authentication
3. Verifying that DX location data is collected successfully

## IAM Permissions

The role has minimal permissions required for this workflow:

- `directconnect:DescribeLocations` - Query Direct Connect location information
- `account:ListRegions` - List enabled AWS regions

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
