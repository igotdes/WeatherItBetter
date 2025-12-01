"""
WeatherItBetter - Main Entry Point

AI-powered outfit recommendation system that considers weather, calendar activities,
and personal preferences to suggest what to wear.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from agents.recommendation_agent import OutfitRecommendationAgent
from agents.activity_agent import CalendarConnector


async def main():
    """Main application entry point."""
    print("\n" + "=" * 70)
    print("👔 WeatherItBetter - AI Outfit Recommendation Agent")
    print("=" * 70)

    # Validate configuration
    if not Config.validate():
        return

    # Ensure data directory exists
    Config.ensure_data_directory()

    try:
        # Step 1: Authenticate with Google Calendar to get user identity
        print("\n" + "=" * 70)
        print("🔐 AUTHENTICATING USER")
        print("=" * 70)

        calendar_connector = CalendarConnector()
        if not calendar_connector.authenticate():
            print("\n❌ Failed to authenticate with Google Calendar")
            print("Please check your credentials.json file\n")
            return

        # Get authenticated user's email
        user_email = calendar_connector.get_user_email()
        user_id = user_email if user_email else "default_user"

        print("=" * 70 + "\n")

        # Step 2: Initialize agent with authenticated user ID
        agent = OutfitRecommendationAgent(
            google_api_key=Config.GOOGLE_API_KEY,
            weather_api_key=Config.OPENWEATHER_API_KEY,
            use_calendar=True,
            project_id=Config.GOOGLE_CLOUD_PROJECT,
            location=Config.GOOGLE_CLOUD_LOCATION,
            agent_engine_id=Config.AGENT_ENGINE_ID,
            user_id=user_id,
            calendar_connector=calendar_connector  # Pass the authenticated connector
        )

        # Step 3: Initialize async components (load preferences from Memory Bank)
        await agent.initialize()

        print("\n✅ Agent initialized successfully!")
        print("\nCommands:")
        print("  recommend <city> - Get outfit recommendation")
        print("  pref <text>      - Add a preference")
        print("  quit             - Exit")
        print()

        # Interactive loop
        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye!\n")
                    break

                if user_input.lower().startswith('recommend '):
                    city = user_input[10:].strip()
                    if not city:
                        print("❌ Please provide a city name")
                        continue

                    print("\n🔄 Generating recommendation...\n")
                    recommendation = await agent.get_recommendation(city)

                    print("=" * 70)
                    print("🎯 YOUR OUTFIT RECOMMENDATION")
                    print("=" * 70)
                    print()
                    print(recommendation)
                    print()
                    print("=" * 70)

                elif user_input.lower().startswith('pref '):
                    pref_text = user_input[5:].strip()
                    if not pref_text:
                        print("❌ Please provide a preference")
                        continue

                    response = await agent.chat(pref_text)
                    print(f"\n🤖 {response}\n")

                else:
                    # General chat
                    response = await agent.chat(user_input)
                    print(f"\n🤖 {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("Please check your .env file and ensure all required API keys are set.\n")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
