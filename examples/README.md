# Examples

This directory contains example scripts demonstrating how to use the WeatherItBetter agent.

## Available Examples

### 1. simple_recommendation.py

Basic usage example showing:
- How to initialize the agent
- Getting outfit recommendations for different cities
- Adding user preferences
- Using different temperature units (Celsius/Fahrenheit)

**Run it:**
```bash
python examples/simple_recommendation.py
```

**What it demonstrates:**
- Basic agent initialization
- Multiple city recommendations
- Preference management
- Temperature unit conversion

---

### 2. with_observability.py

Advanced example with observability features:
- Logging all operations
- Tracking function execution
- Error handling and logging
- Metrics collection

**Run it:**
```bash
python examples/with_observability.py
```

**What it demonstrates:**
- Setting up logging
- Using the `@log_function_call` decorator
- Structured logging
- Error handling with logs
- Log file creation (data/weatheritbetter.log)

---

## Prerequisites

Before running examples:

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up credentials:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Verify setup:**
Make sure you have:
- `GOOGLE_API_KEY` in your `.env`
- `OPENWEATHER_API_KEY` in your `.env`

See [docs/API_CREDENTIALS.md](../docs/API_CREDENTIALS.md) for detailed setup instructions.

---

## Expected Output

### simple_recommendation.py

You should see:
- Agent initialization confirmation
- Weather information for each city
- Detailed outfit recommendations
- Preference confirmations
- Different recommendation styles based on weather

### with_observability.py

You should see:
- All of the above, plus:
- INFO/DEBUG log messages in console
- A log file created at `data/weatheritbetter.log`
- Function entry/exit logs
- Timing information
- Error handling demonstrations

---

## Customization

Feel free to modify these examples:

- Change cities to test different weather conditions
- Add your own preferences
- Experiment with different temperature units
- Try different logging levels
- Add more observability features

---

## Troubleshooting

**"Missing required environment variables"**
- Make sure `.env` exists and contains required keys
- See [API_CREDENTIALS.md](../docs/API_CREDENTIALS.md)

**"Invalid API key"**
- Verify your API keys are correct
- For OpenWeatherMap, wait 10-15 minutes after key creation

**Import errors**
- Make sure you're running from the project root
- Install all dependencies: `pip install -r requirements.txt`

---

## Next Steps

After running these examples:

1. Try the interactive CLI: `python src/main.py`
2. Read the architecture docs: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
3. Explore the source code in `src/agents/`
4. Build your own custom agent!

---

**Need help?** See the main [README.md](../README.md) or open an issue on GitHub.
