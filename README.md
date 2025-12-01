# WeatherItBetter - AI Outfit Recommendation Agent

An intelligent outfit recommendation system that combines real-time weather data, calendar activities, and personal preferences to suggest what to wear each day.

## Features

- **Weather-Aware Recommendations**: Fetches real-time weather data from OpenWeatherMap
- **AI-Powered Suggestions**: Uses Google Gemini AI to generate contextual outfit recommendations
- **Calendar Integration**: Google Calendar integration to consider scheduled activities
- **Cloud Preference Storage**: Vertex AI Memory Bank for persistent preference storage across sessions
- **Preference Learning**: Learns and applies your personal style preferences (business casual, color preferences, clothing dislikes)
- **Interactive CLI**: Simple command-line interface for easy interaction
- **Dual Storage**: Cloud-based preferences with automatic local backup for offline access

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Google AI API key (for Gemini)
- OpenWeatherMap API key
- Google Calendar OAuth credentials (credentials.json)
- Google Cloud project with Vertex AI enabled
- Vertex AI Agent Engine instance configured

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd weatheritbetter-clean
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your credentials:
```bash
cp .env.example .env
```

4. Edit `.env` and add your API keys:
```
GOOGLE_API_KEY=your_actual_google_ai_key_here
OPENWEATHER_API_KEY=your_actual_openweather_key_here
```

5. Set up Google Calendar credentials:
   - Follow the instructions in [API_CREDENTIALS.md](docs/API_CREDENTIALS.md)
   - Download `credentials.json` to the project root directory
   - On first run, you'll be prompted to authorize calendar access

6. Set up Vertex AI Memory Bank for cloud-based preference storage:
   - Create a Google Cloud project
   - Enable Vertex AI API
   - Create an Agent Engine instance
   - Add `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `AGENT_ENGINE_ID` to `.env`
   - Authenticate: `gcloud auth application-default login`

See [API_CREDENTIALS.md](docs/API_CREDENTIALS.md) for detailed instructions on obtaining all credentials.

**Important**: Make sure you have the correct package versions installed:
- `google-genai >= 1.50.0`
- `google-adk[vertexai] >= 1.19.0`
- `websockets >= 15.0.1`

### Running the Application

```bash
python src/main.py
```

### Usage Examples

**Get an outfit recommendation:**
```
You: recommend Manila
```

**Add a preference:**
```
You: pref I prefer business casual style
```

**General chat:**
```
You: I don't like wearing shorts
```

**Exit:**
```
You: quit
```

## Project Structure

```
weatheritbetter-clean/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Template for environment variables
├── .gitignore               # Git ignore rules (excludes credentials)
│
├── src/                     # Source code
│   ├── main.py             # Entry point - interactive CLI
│   ├── config.py           # Configuration loader
│   │
│   ├── agents/             # Agent modules
│   │   ├── weather_agent.py        # Weather data fetcher
│   │   ├── activity_agent.py       # Calendar integration
│   │   ├── preference_agent.py     # Preference management with Memory Bank
│   │   └── recommendation_agent.py # Main recommendation engine
│   │
│   └── utils/              # Utility modules
│       ├── observability.py        # Logging and tracing
│       └── location_utils.py       # Location helpers
│
├── scripts/               # Utility scripts
│   ├── create_agent_engine.py     # Setup Vertex AI Agent Engine
│   ├── push_preferences.py        # Push local prefs to Memory Bank
│   └── resync_preferences.py      # Re-sync preferences
│
├── docs/                  # Documentation
│   └── API_CREDENTIALS.md # How to get API keys & setup guides
│
├── examples/              # Example scripts
│   ├── simple_recommendation.py   # Basic usage example
│   └── with_observability.py      # Example with tracing
│
└── data/                  # Data storage (gitignored)
    └── preferences.json   # Local backup of preferences
```

## How It Works

1. **Weather Fetching**: Uses OpenWeatherMap API to get current weather conditions for your location
2. **Activity Detection**: Optionally reads your Google Calendar to understand your daily activities
3. **Preference Learning**: Saves your style preferences and temperature sensitivities
4. **AI Generation**: Combines all context and uses Google Gemini AI to generate personalized outfit recommendations
5. **Continuous Learning**: Your preferences are saved and applied to future recommendations

## Components

### Weather Agent
Fetches real-time weather data including:
- Current temperature and "feels like" temperature
- Weather conditions (sunny, rainy, cloudy, etc.)
- Humidity and wind speed
- Location information

### Activity Agent (Optional)
Integrates with Google Calendar to detect:
- Meeting formality levels (casual, business casual, formal)
- Exercise activities
- Indoor vs outdoor events
- Time-based planning

### Preference Agent
Manages your personal preferences with Vertex AI Memory Bank:
- Style preferences (casual, formal, business casual)
- Temperature sensitivity
- Color preferences
- Clothing dislikes
- **Cloud storage**: Preferences synced to Vertex AI Memory Bank for persistence
- **Local backup**: Automatically backed up to `data/preferences.json`
- **Semantic retrieval**: Uses AI to intelligently retrieve relevant preferences

### Recommendation Agent
Main orchestrator that:
- Combines weather, activities, and preferences
- Builds context for AI model
- Generates specific, actionable outfit recommendations
- Explains reasoning behind suggestions

## Security Notes

**IMPORTANT**: This repository does NOT contain any real API keys or credentials.

- Never commit your `.env` file
- Never commit `credentials.json` or `token.json`
- Never share your API keys publicly
- All sensitive files are listed in `.gitignore`

See `.env.example` for the template of required environment variables.

## Advanced Configuration

### Vertex AI Memory Bank

The application uses Vertex AI Memory Bank for persistent, cloud-based preference storage across sessions. Preferences are automatically synchronized to the cloud and also backed up locally to `data/preferences.json`.

**Features:**
- ✅ **Persistent storage** across sessions and devices
- ✅ **Semantic search** for intelligent preference retrieval using similarity matching
- ✅ **Automatic local backup** to `data/preferences.json` for offline access
- ✅ **User-scoped memories** - each user's preferences are isolated by email
- ✅ **Smart consolidation** - Memory Bank's AI intelligently merges related preferences

**How it works:**
1. When you add preferences (e.g., "I prefer business casual"), they're saved locally
2. The preference is converted to a natural conversation and sent to Memory Bank
3. Memory Bank's LLM extracts facts and stores them as semantic memories
4. On app startup, preferences are retrieved using semantic search
5. Retrieved preferences are merged with local storage for fast access

**Setup:**
1. Create a Google Cloud Project
2. Enable Vertex AI API
3. Create an Agent Engine instance using `scripts/create_agent_engine.py` (see [API_CREDENTIALS.md](docs/API_CREDENTIALS.md))
4. Set up authentication: `gcloud auth application-default login`
5. Add credentials to your `.env`:
```
GOOGLE_CLOUD_PROJECT=123456789012    # Your project NUMBER (not ID)
GOOGLE_CLOUD_LOCATION=us-central1    # Your preferred region
AGENT_ENGINE_ID=1234567890123456     # Numeric ID only
```

**Verification:**
When you start the app, you'll see:
```
✅ Vertex AI Memory Bank connected successfully!
   Storage: Cloud-based (Vertex AI)
   Backup: Local file (data/preferences.json)
📥 Loading preferences from Vertex AI Memory Bank...
   ✅ Loaded X preferences from cloud
```

This confirms your preferences are being saved to and loaded from the cloud.

**Utility Scripts:**
- `scripts/push_preferences.py` - Push local preferences to Memory Bank
- `scripts/resync_preferences.py` - Re-sync preferences from local file

## Dependencies

Key dependencies:
- `google-genai >= 1.50.0` - Google Gemini AI SDK
- `google-adk[vertexai] >= 1.19.0` - Google Agent Development Kit for Vertex AI Memory Bank
- `websockets >= 15.0.1` - WebSocket support (required by google-adk)
- `requests >= 2.31.0` - HTTP requests for weather API
- `python-dotenv >= 1.0.0` - Environment variable management
- `google-auth >= 2.23.0` - Google authentication
- `google-api-python-client >= 2.100.0` - Google Calendar API

See `requirements.txt` for complete list with specific version constraints.

**Note**: Package versions are important for compatibility. The `google-adk` package requires `google-genai >= 1.50.0` and `websockets >= 15.0.1`.

## Troubleshooting

**"Missing required environment variables"**
- Make sure you've created `.env` from `.env.example`
- Check that all required API keys are set

**"Invalid API key"**
- Verify your API keys are correct
- Check if API keys have proper permissions enabled

**"City not found"**
- Try using the full city name
- Use English spelling
- Try adding country code (e.g., "Manila, PH")

**Calendar not working**
- Make sure you've set `use_calendar=True` in main.py
- Verify `credentials.json` exists
- Re-authenticate by deleting `token.json` and running again

## Contributing

This is a capstone project. If you'd like to extend it:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all credentials are excluded
5. Submit a pull request

## License

This project is for educational purposes as part of a Kaggle capstone submission.

## Acknowledgments

- Google Gemini AI for intelligent recommendations
- OpenWeatherMap for weather data
- Google Calendar API for activity detection

## Contact

For questions about this project, please open an issue on GitHub.

---

**Built with Google Gemini AI as part of a Kaggle Data Science Capstone Project**
