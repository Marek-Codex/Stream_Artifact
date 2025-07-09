# Stream Artifact OAuth Setup Guide

## Overview
Stream Artifact uses OAuth to securely connect to your streaming and backup services. This guide explains how to set up OAuth applications for each service.

## Required OAuth Applications

### 1. Twitch Application
For Twitch integration, you need to create a Twitch application:

1. Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Click "Register Your Application"
3. Fill in the details:
   - **Name**: Stream Artifact Bot
   - **OAuth Redirect URLs**: `http://localhost:3000/auth/twitch`
   - **Category**: Chat Bot
4. Click "Create"
5. Note down your **Client ID** and **Client Secret**

### 2. GitHub Application (Optional - for backup)
For cloud backup to GitHub Gists:

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Stream Artifact Backup
   - **Homepage URL**: `https://github.com/your-username/stream-artifact`
   - **Authorization callback URL**: `http://localhost:3000/auth/github`
4. Click "Register application"
5. Note down your **Client ID** and **Client Secret**

### 3. OpenRouter API Key
For AI responses:

1. Go to [OpenRouter](https://openrouter.ai)
2. Sign up or log in
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Note down your API key (starts with `sk-or-`)

## Configuration
Update the OAuth client IDs and secrets in the wizard:

```python
# In src/ui/oauth_wizard.py
self.twitch_client_id = "your_twitch_client_id"
self.twitch_client_secret = "your_twitch_client_secret"
self.github_client_id = "your_github_client_id"
self.github_client_secret = "your_github_client_secret"
```

## Security Notes
- Never commit your OAuth secrets to version control
- Use environment variables for production deployments
- The local OAuth server runs on port 3000 during setup
- OAuth tokens are stored securely in the local configuration

## Troubleshooting
- Make sure your OAuth redirect URLs are exactly `http://localhost:3000/auth/[service]`
- Check that the OAuth server is running during the setup process
- Verify that your OAuth applications have the correct permissions/scopes
- For Twitch: `chat:read`, `chat:edit`, `channel:read:subscriptions`
- For GitHub: `gist` scope for backup functionality
