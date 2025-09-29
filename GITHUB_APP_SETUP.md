# GitHub App Setup Guide for Data Product Hub

This guide walks you through setting up a GitHub App to enable the Data Product Hub MCP Server to analyze any dbt repository on GitHub.

## Why GitHub App?

A GitHub App provides secure, scalable access to repositories:
- ✅ Users control which repositories to grant access to
- ✅ Fine-grained permissions (read-only access to code)
- ✅ Works with private repositories
- ✅ No need for users to share personal access tokens
- ✅ Scalable across multiple users and organizations

## Step 1: Create Your GitHub App

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/apps
   - Click "New GitHub App"

2. **Fill in Basic Information**
   ```
   GitHub App name: Data Product Hub Analyzer
   Description: Analyzes dbt projects for data product quality assessment
   Homepage URL: https://data-product-hub.fastmcp.app (or your documentation URL)
   ```

3. **Set Permissions**
   The app only needs minimal read permissions:
   ```
   Repository permissions:
   - Contents: Read
   - Metadata: Read

   User permissions: (none needed)

   Organization permissions: (none needed)
   ```

4. **Configure Installation**
   ```
   Where can this GitHub App be installed?
   ☑️ Any account

   User authorization callback URL: (leave empty for now)
   Setup URL: (leave empty for now)
   Webhook URL: (leave empty - we don't need webhooks)
   Webhook secret: (leave empty)
   ```

5. **Create the App**
   - Click "Create GitHub App"
   - Note down your **App ID** (you'll need this)

## Step 2: Generate Private Key

1. **Generate Private Key**
   - In your app settings, scroll down to "Private keys"
   - Click "Generate a private key"
   - Download the `.pem` file

2. **Convert to Base64**
   ```bash
   # Convert the private key to base64 (single line)
   base64 -w 0 < your-app-name.2024-01-01.private-key.pem
   ```

   Save this base64 string - you'll need it for FastMCP Cloud.

## Step 3: Configure FastMCP Cloud Environment

In your FastMCP Cloud deployment, set these environment variables:

```bash
GITHUB_APP_ID=123456  # Your GitHub App ID
GITHUB_APP_PRIVATE_KEY_BASE64=LS0tLS1CRUdJTi... # Your base64-encoded private key
```

## Step 4: Test Your Setup

1. **Deploy to FastMCP Cloud**
   - Use `server.py` as your entry point
   - Your MCP server will be available at: `https://data-product-hub.fastmcp.app/mcp`

2. **Test Repository Validation**
   Create a test that calls:
   ```json
   {
     "tool": "validate_github_repository",
     "arguments": {
       "repo_url": "https://github.com/your-org/test-dbt-repo"
     }
   }
   ```

## Step 5: Install App on Repositories

### For Users to Install Your App:

1. **Share Installation URL**
   ```
   https://github.com/apps/data-product-hub-analyzer/installations/new
   ```

2. **Users Choose Repositories**
   - Users visit the installation URL
   - They select which repositories to grant access to
   - GitHub handles the OAuth flow

3. **Ready to Analyze**
   Once installed, users can analyze any repository via Claude:
   ```
   "Analyze the user_sessions model in https://github.com/company/analytics-dbt"
   "Check metadata coverage for github.com/myorg/data-warehouse"
   ```

## How It Works in Practice

### User Experience:
1. **Install GitHub App** (one-time): User installs your app on their dbt repositories
2. **Use via Claude**: `"Analyze customer_metrics model in github.com/company/dbt-models"`
3. **Get Results**: Claude calls your MCP server which clones the repo and analyzes the model

### Technical Flow:
```
Claude → Your MCP Server → GitHub API (authenticate) → Clone Repo → Analyze dbt → Return Results
```

## Tool Usage Examples

Once set up, users can use these tools via Claude:

```python
# Analyze specific model from any GitHub repo
analyze_dbt_model(
    model_name="customer_lifetime_value",
    repo_url="https://github.com/company/analytics-dbt"
)

# Check metadata coverage across entire project
check_metadata_coverage(
    repo_url="https://github.com/myorg/data-warehouse"
)

# Get project lineage
get_project_lineage(
    repo_url="github.com/startup/dbt-models"
)

# Comprehensive quality assessment
assess_data_product_quality(
    model_name="user_engagement_metrics",
    repo_url="https://github.com/saas-company/data-models"
)
```

## Security Notes

- ✅ **Read-only access**: App only requests read permissions
- ✅ **User control**: Users choose which repositories to grant access
- ✅ **Minimal scope**: Only accesses Contents and Metadata
- ✅ **Temporary tokens**: Uses short-lived installation access tokens
- ✅ **No data persistence**: Repositories are cached temporarily and cleaned up

## Troubleshooting

### "GitHub App not installed" Error
- User needs to install your app on the repository
- Share the installation URL: `https://github.com/apps/YOUR_APP_NAME/installations/new`

### "Authentication failed" Error
- Check `GITHUB_APP_ID` and `GITHUB_APP_PRIVATE_KEY_BASE64` environment variables
- Ensure private key is properly base64 encoded

### "Not a valid dbt project" Error
- Repository must contain `dbt_project.yml` file
- Repository must have a `models/` directory with `.sql` files

## Next Steps

Once your GitHub App is set up and deployed:

1. **Test with your own repositories** first
2. **Share installation URL** with potential users
3. **Update documentation** with your specific app name and URLs
4. **Monitor usage** through GitHub App settings

Your MCP server will now be a **universal dbt project analyzer** that works with any GitHub repository! 🚀