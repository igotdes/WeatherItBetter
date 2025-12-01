"""
Recommendation with Observability Example

This example demonstrates how to use the WeatherItBetter agent
with observability features enabled (logging, tracing, metrics).
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import Config
from agents.recommendation_agent import OutfitRecommendationAgent
from utils.observability import setup_logging, get_logger, log_function_call


# Set up logging
setup_logging(level="INFO", log_file="data/weatheritbetter.log")
logger = get_logger(__name__)


@log_function_call
async def get_recommendation_with_logging(agent, city: str):
    """
    Get recommendation with automatic logging.

    The @log_function_call decorator automatically logs:
    - Function entry and exit
    - Execution time
    - Any errors that occur
    """
    logger.info(f"Fetching recommendation for {city}")

    try:
        recommendation = await agent.get_recommendation(city)
        logger.info(f"Successfully generated recommendation for {city}")
        return recommendation
    except Exception as e:
        logger.error(f"Error getting recommendation for {city}: {e}")
        raise


@log_function_call
async def add_preference_with_logging(agent, preference: str):
    """Add preference with logging."""
    logger.info(f"Adding preference: {preference}")

    try:
        response = await agent.chat(preference)
        logger.info("Preference added successfully")
        return response
    except Exception as e:
        logger.error(f"Error adding preference: {e}")
        raise


async def main():
    """Example with observability enabled."""

    print("=" * 70)
    print("WeatherItBetter - Observability Example")
    print("=" * 70)
    print()

    logger.info("Starting WeatherItBetter with observability")

    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed")
        print("\n❌ Please set up your .env file first!")
        return

    # Initialize agent
    logger.info("Initializing recommendation agent")
    agent = OutfitRecommendationAgent(
        google_api_key=Config.GOOGLE_API_KEY,
        weather_api_key=Config.OPENWEATHER_API_KEY,
        use_calendar=False
    )
    logger.info("Agent initialized successfully")

    print("✅ Agent initialized with observability!\n")
    print("📊 Logs are being written to: data/weatheritbetter.log\n")

    # Example 1: Get recommendation with logging
    print("=" * 70)
    print("Example 1: Getting recommendation for Manila")
    print("=" * 70)
    recommendation = await get_recommendation_with_logging(agent, "Manila")
    print(recommendation)
    print()

    # Example 2: Add preference with logging
    print("=" * 70)
    print("Example 2: Adding preference")
    print("=" * 70)
    response = await add_preference_with_logging(agent, "I prefer lightweight fabrics")
    print(f"Agent: {response}")
    print()

    # Example 3: Multiple requests (for metrics)
    print("=" * 70)
    print("Example 3: Multiple requests for different cities")
    print("=" * 70)
    cities = ["Tokyo", "London", "Sydney"]

    for city in cities:
        logger.info(f"Processing request for {city}")
        print(f"\n--- {city} ---")
        recommendation = await get_recommendation_with_logging(agent, city)
        print(recommendation[:200] + "..." if len(recommendation) > 200 else recommendation)

    print()

    # Example 4: Demonstrate error handling
    print("=" * 70)
    print("Example 4: Error handling with logging")
    print("=" * 70)
    try:
        logger.info("Attempting to get recommendation for invalid city")
        recommendation = await get_recommendation_with_logging(agent, "NonexistentCity12345")
        print(recommendation)
    except Exception as e:
        logger.error(f"Caught expected error: {e}")
        print(f"✓ Error handled gracefully and logged")
    print()

    logger.info("All examples completed successfully")

    print("=" * 70)
    print("✅ Examples completed!")
    print("=" * 70)
    print("\n📊 Check data/weatheritbetter.log for detailed logs")


if __name__ == "__main__":
    asyncio.run(main())
