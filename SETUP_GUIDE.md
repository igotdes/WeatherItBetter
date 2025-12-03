# WeatherItBetter - Quick Setup Guide

This guide will help you set up and run the WeatherItBetter AI Outfit Recommendation Agent in under 30 minutes.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: Install Dependencies](#step-1-install-dependencies)
- [Step 2: Configure API Keys](#step-2-configure-api-keys)
- [Step 3: Set Up Google Calendar](#step-3-set-up-google-calendar)
- [Step 4: Set Up Vertex AI Memory Bank](#step-4-set-up-vertex-ai-memory-bank)
- [Step 5: Run the Application](#step-5-run-the-application)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:
- **Python 3.8 or higher** installed
- **pip** package manager
- A **Google account** (for API access)
- **Google Cloud account** (free tier is sufficient)
- Terminal/command line access

Check your Python version:
```bash
python3 --version
```

---

## Step 1: Install Dependencies

1. **Navigate to project directory:**
```bash
cd weatheritbetter-clean
```

2. **Install required packages:**
```bash
pip3 install -r requirements.txt
```

This will install:
- Google Gemini AI SDK
- Google Agent Development Kit (ADK)
- Weather API client
- Google Calendar integration
- Other dependencies

**Estimated time: 2-5 minutes**

---

## Step 2: Configure API Keys

### 2.1 Create .env File

Copy the example environment file:
```bash
cp .env.example .env
```

### 2.2 Get Google AI API Key (FREE)

1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Add to `.env`:
   ```
   GOOGLE_API_KEY=AIzaSy...your-key-here
   ```

**Estimated time: 2 minutes**

### 2.3 Get OpenWeatherMap API Key (FREE)

1. Visit: https://openweathermap.org/
2. Sign up for a free account
3. Go to "My API keys"
4. Copy the default key or create a new one
5. Add to `.env`:
   ```
   OPENWEATHER_API_KEY=your-key-here
   ```
6. **Wait 10-15 minutes** for the key to activate

**Estimated time: 3 minutes + 15 min activation**

---

## Step 3: Set Up Google Calendar

### 3.1 Create OAuth Credentials

1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable **Google Calendar API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Configure consent screen if prompted:
      - User Type: External
      - App name: WeatherItBetter
      - User support email: your email
      - Developer contact: your email
      - Click "Save and Continue"
      - **Scopes**: Click "Add or Remove Scopes", search for and add:
         - `.../auth/calendar.readonly` (View your calendars)
         - `.../auth/userinfo.email` (See your email address)
      - Click "Update" and "Save and Continue"
    - **Test users**: Add your email address
    - Click "Save and Continue"
   - Application type: "Desktop app"
   - Name: WeatherItBetter
   - Click "Create"

5. **Download credentials.json**:
   - Click the download icon next to your OAuth 2.0 Client ID
   - Save as `credentials.json` in the project root directory

**Estimated time: 5-7 minutes**

### 3.2 First-Time Authorization

The app will automatically prompt for authorization on first run. You'll:
1. See a browser window open
2. Sign in with your Google account
3. Grant calendar read permission
4. A `token.json` file will be created automatically

**Note:** Both `credentials.json` and `token.json` are automatically excluded from git.

---

## Step 4: Set Up Vertex AI Memory Bank

Vertex AI Memory Bank provides cloud-based preference storage so your clothing preferences persist across sessions.

### 4.1 Enable Vertex AI

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Enable **Vertex AI API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Vertex AI API"
   - Click "Enable"

### 4.2 Create Agent Engine

1. Navigate to: **Vertex AI** → **Agents** → **Agent Engines**
   - Direct link: https://console.cloud.google.com/vertex-ai/agents/agent-engines
2. Click "Create" to create a new Agent Engine
3. Note the **Agent Engine ID** (numeric value from the list)

**Alternative - Use Script:**
```bash
python3 scripts/create_agent_engine.py
```

### 4.3 Get Project Details

You need your **Project NUMBER** (not Project ID):

**Method 1 - Console:**
1. Go to: https://console.cloud.google.com/
2. Select your project
3. The project number is shown on the dashboard (numeric format: `123456789012`)

**Method 2 - Command Line:**
```bash
gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"
```

### 4.4 Configure Environment

Add to your `.env` file:
```
GOOGLE_CLOUD_PROJECT=123456789012      # Your PROJECT NUMBER (numeric)
GOOGLE_CLOUD_LOCATION=us-central1      # Or your preferred region
AGENT_ENGINE_ID=1234567890123456       # Numeric ID only
```

### 4.5 Authenticate with Google Cloud

Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install

Then authenticate:
```bash
gcloud auth application-default login
```

Follow the browser prompts to sign in.

**Estimated time: 10 minutes**

---

## Step 5: Run the Application

You're ready! Start the application:

```bash
python3 src/main.py
```

### Expected Output

You should see:
```
======================================================================
👔 WeatherItBetter - AI Outfit Recommendation Agent
======================================================================

🔐 AUTHENTICATING USER
======================================================================
👤 Authenticated as: your-email@gmail.com
✅ Authenticated as: your-email@gmail.com

======================================================================
🔗 INITIALIZING VERTEX AI MEMORY BANK
======================================================================
   Project: 123456789012
   Location: us-central1
   User: your-email@gmail.com
✅ Vertex AI Memory Bank connected successfully!
   Storage: Cloud-based (Vertex AI)
   Backup: Local file (data/preferences.json)
======================================================================

📥 Loading preferences from Vertex AI Memory Bank...
   ℹ️  No preferences found in Memory Bank (new user or first run)

✅ Agent initialized successfully!

Commands:
  recommend <city> - Get outfit recommendation
  pref <text>      - Add a preference
  quit             - Exit

You:
```

### Try It Out!

**Get your first recommendation:**
```
You: recommend Tokyo
```

**Add your preferences:**
```
You: pref I prefer business casual style
You: pref I don't like wearing shorts
You: pref I like autumn colors
```

**Get a personalized recommendation:**
```
You: recommend Manila
```

The agent will now consider your preferences when making recommendations!

**Exit:**
```
You: quit
```

---

## Troubleshooting

### "Missing required environment variables"
- Verify `.env` file exists in project root
- Check all required variables are set
- Make sure there are no extra spaces or quotes

### "Invalid API key" (Google AI)
- Verify key starts with `AIza`
- Check for typos when copying
- Try generating a new key

### "Invalid API key" (OpenWeatherMap)
- Wait 10-15 minutes after creating the key
- Key should be 32 characters (hexadecimal)
- Verify account is active

### Calendar authorization fails
- Make sure `credentials.json` is in project root
- Delete `token.json` and try again
- Verify your email is added as a test user in OAuth consent screen

### Vertex AI connection fails
- Run: `gcloud auth application-default login`
- Verify all APIs are enabled
- Check project number (not project ID) is correct
- Try a different region in `GOOGLE_CLOUD_LOCATION`

### ImportError or ModuleNotFoundError
- Reinstall dependencies: `pip3 install -r requirements.txt`
- Use a virtual environment if system packages conflict
- Ensure Python 3.8+ is being used

### "Cannot connect to Memory Bank"
- Verify Agent Engine ID is correct (numeric only)
- Check authentication: `gcloud auth application-default login`
- Ensure Vertex AI API is enabled
- Verify you have permissions in the GCP project

---

## Next Steps

Once everything is working:

1. **Explore Calendar Integration:**
   - Add events to your Google Calendar
   - The agent will suggest appropriate outfits based on your schedule

2. **Build Your Preference Profile:**
   - Add more preferences about your style
   - Tell the agent about temperature sensitivities
   - Mention specific clothing items you like or dislike

3. **Try Different Locations:**
   - Test recommendations for different cities
   - See how the agent adapts to different climates

4. **Check the Examples:**
   - See `examples/simple_recommendation.py` for basic usage
   - See `examples/with_observability.py` for tracing

---

## Need More Help?

- **Detailed API setup:** See [docs/API_CREDENTIALS.md](docs/API_CREDENTIALS.md)
- **Architecture details:** See [README.md](README.md)
- **Common issues:** Check the Troubleshooting sections in README.md

---

## Estimated Total Setup Time

- **Minimum (all APIs ready):** ~15 minutes
- **Typical (need to create accounts):** ~30-40 minutes
- **First time (including wait times):** ~45-60 minutes

Most of the time is spent waiting for API key activation and navigating cloud consoles.

---

**Happy outfit planning!** 👔🌤️

---

*Last Updated: 2025-12-01*
