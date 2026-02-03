# GitHub Configuration Required for China Partition Support

## GitHub Secrets to Create

Navigate to: **Settings** → **Secrets and variables** → **Actions** → **Secrets**

### China Partition Credentials

1. **AWS_CHINA_ACCESS_KEY_ID**
   - Type: Repository Secret
   - Value: Your AWS China IAM user access key ID
   - Required permissions:
     - `directconnect:DescribeLocations`
     - `ec2:DescribeRegions`

2. **AWS_CHINA_SECRET_ACCESS_KEY**
   - Type: Repository Secret
   - Value: Your AWS China IAM user secret access key

## Existing Secrets (for reference)

### AWS Commercial Partition
- **AWS_ROLE_ARN** (Variable, not Secret)
  - Value: `arn:aws:iam::<ACCOUNT_ID>:role/GitHubActions-DXLocationDetails`
  - Uses OIDC authentication (no long-lived credentials)

### EU Sovereign Cloud
- **AWS_EUSC_ACCESS_KEY_ID** (Secret)
- **AWS_EUSC_SECRET_ACCESS_KEY** (Secret)

## IAM User Setup for China Partition

Create an IAM user in your AWS China account with the following policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "directconnect:DescribeLocations",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    }
  ]
}
```

## Verification

After adding the secrets, the GitHub Actions workflow will:
1. Collect data from AWS Commercial (via OIDC)
2. Collect data from EU Sovereign Cloud (via access keys)
3. Collect data from China (via access keys)
4. Merge all three partitions
5. Generate CSV, KML, and HTML outputs
6. Publish to GitHub Pages

The China tab will appear on the right side of the EUSC tab in the interactive HTML page.
