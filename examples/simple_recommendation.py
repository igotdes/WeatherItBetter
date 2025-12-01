"""
Simple Recommendation Example

This example demonstrates basic usage of the WeatherItBetter agent
to get outfit recommendations for different cities.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import Config
from agents.recommendation_agent import OutfitRecommendationAgent


async def main():
    """Simple example of getting outfit recommendations."""

    print("=" * 70)
    print("WeatherItBetter - Simple Recommendation Example")
    print("=" * 70)
    print()

    # Validate configuration
    if not Config.validate():
        print("\n❌ Please set up your .env file first!")
        print("See .env.example and docs/API_CREDENTIALS.md")
        return

    # Initialize agent (without calendar integration)
    agent = OutfitRecommendationAgent(
        google_api_key=Config.GOOGLE_API_KEY,
        weather_api_key=Config.OPENWEATHER_API_KEY,
        use_calendar=False
    )

    print("✅ Agent initialized!\n")

    # Example 1: Get recommendation for Manila
    print("=" * 70)
    print("Example 1: Manila, Philippines")
    print("=" * 70)
    recommendation = await agent.get_recommendation("Manila")
    print(recommendation)
    print()

    # Example 2: Add a preference
    print("=" * 70)
    print("Example 2: Adding a preference")
    print("=" * 70)
    response = await agent.chat("I prefer business casual style")
    print(f"Agent: {response}")
    print()

    # Example 3: Get recommendation with preference applied
    print("=" * 70)
    print("Example 3: Tokyo, Japan (with preference)")
    print("=" * 70)
    recommendation = await agent.get_recommendation("Tokyo")
    print(recommendation)
    print()

    # Example 4: Different weather conditions
    print("=" * 70)
    print("Example 4: London, UK (typically rainy)")
    print("=" * 70)
    recommendation = await agent.get_recommendation("London")
    print(recommendation)
    print()

    # Example 5: Using Fahrenheit
    print("=" * 70)
    print("Example 5: New York, USA (Fahrenheit)")
    print("=" * 70)
    recommendation = await agent.get_recommendation("New York", temperature_unit="imperial")
    print(recommendation)
    print()

    print("=" * 70)
    print("✅ Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
