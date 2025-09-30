# GitHub App Setup Guide

This guide helps you create your own GitHub App for use with Data Product Hub, either with our hosted service or your own deployment.

## Why Create Your Own GitHub App?

### Use Cases

1. **Enterprise Compliance**: Your organization requires custom GitHub Apps
2. **Enhanced Control**: Manage permissions and installations yourself
3. **Custom Branding**: Use your organization's name and branding
4. **Audit Requirements**: Need detailed access logs and controls

### Benefits

- **Custom Permissions**: Set exactly the repository access you need
- **Organization Control**: Install only on repositories you choose
- **Enhanced Security**: Private key under your control
- **Usage Analytics**: Detailed insights into app usage

## Step-by-Step Setup

### 1. Create the GitHub App

1. **Navigate to GitHub Settings**:
   - Go to your GitHub organization
   - Click **Settings** → **Developer settings** → **GitHub Apps**
   - Click **New GitHub App**

2. **Basic Information**:
   ```
   App Name: [Your Org] Data Product Hub
   Homepage URL: https://your-organization.com
   Description: AI-powered dbt project analysis for your organization
   ```

3. **Webhook Configuration**:
   ```
   Webhook URL: (leave blank - not needed)
   Webhook Secret: (leave blank)
   SSL verification: Enabled
   ```

### 2. Configure Permissions

**Repository Permissions** (Required):
- **Contents**: Read
- **Metadata**: Read

**Repository Permissions** (Optional for enhanced features):
- **Actions**: Read (for CI/CD integration)
- **Pull requests**: Read (for PR analysis)
- **Issues**: Read (for issue context)

**Organization Permissions** (Optional):
- **Members**: Read (for user context)

### 3. Event Subscriptions

For basic functionality, no webhook events are required. Leave all unchecked.

### 4. Installation Options

- **Where can this GitHub App be installed?**:
  - Choose "Only on this account" for organization-specific apps
  - Choose "Any account" if you want to share with other organizations

### 5. Generate Credentials

1. **App ID**: Note the App ID (you'll need this later)

2. **Generate Private Key**:
   - Click **Generate a private key**
   - Download the `.pem` file
   - Keep this file secure - it cannot be recovered

3. **Convert Private Key to Base64**:
   ```bash
   # Convert the .pem file to base64 format
   base64 -i your-app-name.2024-01-01.private-key.pem | tr -d '\n' > private-key-base64.txt

   # The output file contains your base64-encoded private key
   cat private-key-base64.txt
   ```

## Installation and Usage

### Install the App

1. **Navigate to Install App**:
   - In your GitHub App settings, click **Install App**
   - Choose your organization
   - Select repositories:
     - **All repositories** (for organization-wide access)
     - **Selected repositories** (for specific dbt projects)

2. **Grant Permissions**:
   - Review the permissions
   - Click **Install & Authorize**

### Using with Hosted Data Product Hub

If you want to use your GitHub App with our hosted service:

1. **Contact Support**: Reach out to configure your custom GitHub App
2. **Provide Credentials**: Securely share your App ID and private key
3. **Custom Configuration**: We'll configure a custom endpoint for your organization

### Using with Self-Hosted Deployment

Set environment variables in your deployment:

```bash
# Required
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY_BASE64=LS0tLS1CRUdJTi0tLS0t...

# Optional
GITHUB_API_BASE_URL=https://api.github.com  # For GitHub Enterprise
```

## Security Best Practices

### Private Key Management

1. **Secure Storage**: Store private keys in encrypted secret management systems
2. **Access Control**: Limit access to private keys to essential personnel only
3. **Rotation**: Plan for periodic private key rotation
4. **Backup**: Securely backup private keys with proper encryption

### App Permissions

1. **Principle of Least Privilege**: Only grant necessary permissions
2. **Regular Audits**: Review and audit app installations periodically
3. **Monitor Usage**: Track which repositories the app accesses
4. **Revoke When Needed**: Remove access for unused repositories

### Installation Management

1. **Repository Selection**: Only install on repositories containing dbt projects
2. **Team Awareness**: Ensure relevant teams know about the app installation
3. **Documentation**: Document the app's purpose and usage for your organization

## Troubleshooting

### Common Issues

**"Bad credentials" error:**
- Verify App ID is correct
- Check that private key is properly base64-encoded
- Ensure the private key file wasn't corrupted during conversion

**"Not Found" or "Resource not accessible" errors:**
- Verify the app is installed on the repository
- Check that the repository exists and is accessible
- Ensure the app has the required permissions

**Rate limiting issues:**
- GitHub Apps have higher rate limits than personal access tokens
- Monitor your app's rate limit usage in the GitHub API
- Consider implementing exponential backoff for retries

### Verification Steps

1. **Test App Authentication**:
   ```bash
   # Test that your credentials work
   curl -H "Authorization: Bearer $(your-jwt-token)" \
        "https://api.github.com/app"
   ```

2. **Verify Installation**:
   ```bash
   # List app installations
   curl -H "Authorization: Bearer $(your-jwt-token)" \
        "https://api.github.com/app/installations"
   ```

3. **Test Repository Access**:
   ```bash
   # Test access to a specific repository
   curl -H "Authorization: token $(installation-access-token)" \
        "https://api.github.com/repos/your-org/your-repo"
   ```

## Migration from Public App

If you're migrating from using the public Data Product Hub GitHub App:

### Before Migration
1. **Document Current Usage**: Note which repositories currently use the service
2. **Plan Downtime**: Schedule the migration during low-usage periods
3. **Inform Users**: Notify your team about the upcoming change

### Migration Steps
1. **Create New App**: Follow this guide to create your organization's app
2. **Install New App**: Install on the same repositories as the old app
3. **Update Configuration**: Switch to using your new app credentials
4. **Test Functionality**: Verify everything works with the new app
5. **Remove Old App**: Uninstall the public app from your repositories

### After Migration
1. **Monitor Performance**: Ensure the new app works as expected
2. **Update Documentation**: Update any internal documentation
3. **Team Training**: Brief your team on any changes in functionality

## Enterprise Features

### Advanced Configurations

**GitHub Enterprise Server:**
```bash
GITHUB_API_BASE_URL=https://your-github-enterprise.com/api/v3
```

**Custom dbt Profiles:**
```bash
DBT_PROFILES_DIR=/custom/path/to/profiles
DEFAULT_DBT_PROJECT_PATH=/fallback/dbt/project
```

**Enhanced Logging:**
```bash
LOG_LEVEL=DEBUG
GITHUB_API_LOG_LEVEL=INFO
```

### Integration Options

1. **SSO Integration**: Configure with your organization's SSO
2. **Audit Logging**: Enhanced logging for compliance requirements
3. **Custom Endpoints**: Organization-specific MCP endpoints
4. **Dedicated Support**: Priority support for enterprise customers

## Support

- **Setup Assistance**: Contact us for help setting up your GitHub App
- **Enterprise Support**: Dedicated support for organizations using custom apps
- **Documentation**: Additional guides available in our full documentation
- **Community**: Join our community for tips and best practices

---

Need help? [Contact our support team](mailto:support@data-product-hub.com) or [open an issue](https://github.com/data-product-hub/issues).