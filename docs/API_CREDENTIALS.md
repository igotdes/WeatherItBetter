# API Credentials Setup Guide

This guide provides detailed step-by-step instructions for obtaining all API credentials needed for the WeatherItBetter application.

## Required Credentials

### 1. Google AI API Key (Required)

The Google AI API key is used to access Google's Gemini AI model for generating outfit recommendations.

#### Steps to Get Your Google AI API Key:

1. **Visit Google AI Studio**
   - Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click on "Create API Key" button
   - Select an existing Google Cloud project or create a new one
   - Click "Create API key in new project" (if creating new)

3. **Copy Your Key**
   - Your API key will be displayed (format: `AIza...`)
   - Copy this key immediately
   - Store it securely

4. **Add to .env File**
   ```
   GOOGLE_API_KEY=AIzaSy...your-actual-key-here
   ```

#### Important Notes:
- Keep your API key secret - never commit it to Git
- Free tier includes generous quota for testing
- See [Google AI pricing](https://ai.google.dev/pricing) for usage limits

---

### 2. OpenWeatherMap API Key (Required)

The OpenWeatherMap API provides real-time weather data for outfit recommendations.

#### Steps to Get Your OpenWeatherMap API Key:

1. **Create Account**
   - Go to [https://openweathermap.org/](https://openweathermap.org/)
   - Click "Sign In" → "Create an Account"
   - Fill in your details and verify your email

2. **Navigate to API Keys**
   - After logging in, click on your username (top right)
   - Select "My API keys" from the dropdown

3. **Generate API Key**
   - You'll see a default API key already created
   - Or create a new one by entering a name and clicking "Generate"
   - Copy the API key (format: 32-character hexadecimal string)

4. **Add to .env File**
   ```
   OPENWEATHER_API_KEY=29eba27f...your-actual-key-here
   ```

#### Important Notes:
- API key activation takes about 10-15 minutes
- Free tier allows 60 calls/minute, 1,000,000 calls/month
- Sufficient for personal use and testing
- See [OpenWeatherMap pricing](https://openweathermap.org/price) for details

---

### 3. Google Calendar API (Required)

Google Calendar integration allows the app to consider your scheduled activities when making recommendations.

#### Steps to Set Up Google Calendar API:

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a project" → "New Project"
   - Name it (e.g., "WeatherItBetter")
   - Click "Create"

2. **Enable Calendar API**
   - In your project, go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

3. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure the OAuth consent screen:
     - User Type: External
     - App name: WeatherItBetter
     - User support email: your email
     - Developer contact: your email
     - Click "Save and Continue"
     - Scopes: Click "Add or Remove Scopes", search for and add:
       - `.../auth/calendar.readonly` (View your calendars)
       - `.../auth/userinfo.email` (See your email address)
       - Then click "Update" and "Save and Continue"
     - Test users: Add your email
     - Click "Save and Continue"

4. **Create OAuth Client ID**
   - Application type: "Desktop app"
   - Name: "WeatherItBetter Desktop"
   - Click "Create"

5. **Download Credentials**
   - Click "Download JSON" on the credentials you just created
   - Save as `credentials.json` in the root directory of the project

6. **First-Time Authorization**
   - In `src/main.py`, change `use_calendar=False` to `use_calendar=True`
   - Run the application
   - A browser window will open asking for authorization
   - Sign in with your Google account
   - Grant calendar read permission
   - A `token.json` file will be created (this is gitignored)

#### Important Notes:
- `credentials.json` and `token.json` are automatically gitignored
- Never share these files publicly
- Token expires after some time; delete `token.json` to re-authenticate
- Calendar integration is required for the app to function properly

---

### 4. Vertex AI Memory Bank (Required)

Vertex AI Memory Bank provides persistent cloud-based preference storage and advanced memory capabilities for the outfit recommendation system. It enables intelligent semantic search across user preferences and maintains session history.

#### Steps to Set Up Vertex AI:

1. **Create or Use Existing Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select or create a project

2. **Enable Required APIs**
   - Enable "Vertex AI API"
   - Enable "Cloud Resource Manager API"

3. **Create Agent Engine** (formerly "Reasoning Engine")
   - Navigate to: **Vertex AI** → **Agents** → **Agent Engines**
   - Or direct URL: [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
   - Click "Create" to create a new Agent Engine (if needed)
   - Note your Engine ID (numeric ID displayed in the list or details page)

   **Alternative - List Engines via Python SDK:**
   ```python
   import vertexai
   from vertexai.preview import reasoning_engines

   vertexai.init(project="your-project-id", location="us-central1")
   reasoning_engine_list = reasoning_engines.ReasoningEngine.list()
   print(reasoning_engine_list)
   ```
   The Engine ID is the numeric value at the end of the resource name (e.g., `5842963119676063744`)

4. **Get Project Details**
   - **Project NUMBER** (required for Memory Bank): Found in project settings (numeric format: `123456789012`)
     - Go to [Google Cloud Console](https://console.cloud.google.com/)
     - Select your project
     - The project number is shown on the dashboard
     - Or run: `gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"`
   - Location: Usually `us-central1` or your preferred region (e.g., `asia-southeast1`)

5. **Add to .env File**
   ```
   GOOGLE_CLOUD_PROJECT=225866861023  # Use project NUMBER, not project ID
   GOOGLE_CLOUD_LOCATION=us-central1
   AGENT_ENGINE_ID=5842963119676063744
   ```

6. **Set Up Authentication**
   - Install Google Cloud CLI: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
   - Run: `gcloud auth application-default login`
   - Follow browser prompts to authenticate

#### Important Notes:
- Vertex AI Memory Bank is required for the app to function properly
- Provides persistent cloud storage for user preferences across sessions
- Local backup is automatically maintained at `data/preferences.json`
- May incur costs - see [Vertex AI pricing](https://cloud.google.com/vertex-ai/pricing)
- Requires `gcloud` CLI authentication for access
- **Package Requirements**: Ensure you have compatible versions installed:
  - `google-genai >= 1.50.0`
  - `google-adk[vertexai] >= 1.19.0`
  - `websockets >= 15.0.1`

#### Verification:
When the app starts successfully, you'll see:
```
✅ Vertex AI Memory Bank connected successfully!
   Storage: Cloud-based (Vertex AI)
   Backup: Local file (data/preferences.json)
```

---

## Security Best Practices

### DO:
- Store all credentials in `.env` file only
- Keep `.env` in `.gitignore` (already configured)
- Use different API keys for development and production
- Regenerate keys if accidentally exposed
- Set up usage quotas and alerts in API dashboards

### DON'T:
- Never commit `.env` to Git
- Never hardcode credentials in source code
- Never share credentials in screenshots or logs
- Never commit `credentials.json` or `token.json`
- Never push to public repositories with exposed keys

---

## Verifying Your Setup

After setting up credentials, verify everything works:

```bash
# 1. Check .env file exists
ls -la .env

# 2. Run the application
python src/main.py

# 3. Try a recommendation
You: recommend Tokyo

# 4. Check for errors
# If you see "Missing required environment variables", review your .env file
# If you see "Invalid API key", verify your keys are correct
```

---

## Troubleshooting

### "Missing required environment variables"
**Problem**: `.env` file not found or incomplete

**Solution**:
1. Make sure `.env` exists in the root directory
2. Copy from `.env.example`: `cp .env.example .env`
3. Fill in all required values
4. Restart the application

### "Invalid API key" (Google AI)
**Problem**: API key is incorrect or doesn't have permissions

**Solution**:
1. Verify key is copied correctly (starts with `AIza`)
2. Check if you have API quota remaining
3. Generate a new key if needed
4. Wait a few minutes for key activation

### "Invalid API key" (OpenWeatherMap)
**Problem**: API key is incorrect or not activated

**Solution**:
1. Verify key is 32 characters (hexadecimal)
2. Wait 10-15 minutes after creation for activation
3. Check account status on OpenWeatherMap dashboard
4. Generate new key if needed

### Calendar Authorization Issues
**Problem**: Cannot authenticate with Google Calendar

**Solution**:
1. Make sure `credentials.json` is in root directory
2. Delete `token.json` if it exists
3. Run application again to re-authenticate
4. Check OAuth consent screen is configured
5. Verify your email is added as test user

### Vertex AI Authentication Issues
**Problem**: Cannot connect to Vertex AI

**Solution**:
1. Run `gcloud auth application-default login`
2. Verify project ID matches exactly
3. Check all required APIs are enabled
4. Verify you have necessary permissions in GCP
5. Try different region if connection fails

---

## Cost Estimates

### Free Tier Usage (Typical Personal Use):

**Google AI (Gemini)**:
- Free tier: Very generous
- Typical usage: ~10-50 requests/day
- Cost: $0/month (within free tier)

**OpenWeatherMap**:
- Free tier: 1,000,000 calls/month
- Typical usage: ~50-100 calls/day
- Cost: $0/month (well within free tier)

**Google Calendar API**:
- Completely free for personal use
- No usage limits for reasonable personal usage

**Vertex AI Memory Bank** (Optional):
- This may incur costs
- See [pricing page](https://cloud.google.com/vertex-ai/pricing)
- Set up billing alerts if using

---

## Getting Help

If you encounter issues not covered here:

1. Check the main [README.md](../README.md) for general troubleshooting
2. Review [SETUP.md](SETUP.md) for detailed setup instructions
3. Check API provider documentation:
   - [Google AI Studio Docs](https://ai.google.dev/docs)
   - [OpenWeatherMap API Docs](https://openweathermap.org/api)
   - [Google Calendar API Docs](https://developers.google.com/calendar)
4. Open an issue on GitHub

---

**Last Updated**: 2025-01-30
