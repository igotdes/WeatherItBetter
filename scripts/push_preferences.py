#!/usr/bin/env python3
"""
Push local preferences to Vertex AI Memory Bank (one-way sync).

This script ONLY pushes your local preferences to Memory Bank.
It does NOT load from Memory Bank first, avoiding overwrites.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import Config
from agents.activity_agent import CalendarConnector

# Vertex AI imports
import vertexai


async def push_preference(client, agent_engine_name, user_id, preference_value):
    """Push a single preference to Memory Bank."""
    # Skip generic preferences
    if "remember my clothing preferences" in preference_value.lower():
        print(f"   ⏭️  Skipping: {preference_value}")
        return

    print(f"   💾 Saving: {preference_value}")

    # Create conversation for this specific preference
    user_message = f"Please remember this about my clothing preferences: {preference_value}"
    assistant_message = f"Got it! I'll remember that you {preference_value}. I'll use this when making outfit recommendations."

    # Generate memory
    events = [
        {
            "content": {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        },
        {
            "content": {
                "role": "model",
                "parts": [{"text": assistant_message}]
            }
        }
    ]

    result = client.agent_engines.memories.generate(
        name=agent_engine_name,
        direct_contents_source={"events": events},
        scope={"user_id": user_id},
        config={"wait_for_completion": True}
    )

    print(f"      ✅ Saved successfully")


async def main():
    print("\n" + "=" * 70)
    print("📤 Push Local Preferences to Memory Bank")
    print("=" * 70)

    # Validate configuration
    if not Config.validate():
        return

    # Authenticate to get user ID
    print("\n🔐 Authenticating...")
    calendar_connector = CalendarConnector()
    if not calendar_connector.authenticate():
        print("❌ Failed to authenticate")
        return

    user_email = calendar_connector.get_user_email()
    user_id = user_email if user_email else "default_user"
    print(f"✅ Authenticated as: {user_id}\n")

    # Initialize Vertex AI client
    client = vertexai.Client(
        project=Config.GOOGLE_CLOUD_PROJECT,
        location=Config.GOOGLE_CLOUD_LOCATION
    )

    agent_engine_name = f"projects/{Config.GOOGLE_CLOUD_PROJECT}/locations/{Config.GOOGLE_CLOUD_LOCATION}/reasoningEngines/{Config.AGENT_ENGINE_ID}"

    # Load local preferences
    prefs_file = Path("data/preferences.json")
    if not prefs_file.exists():
        print("❌ No local preferences file found")
        return

    with open(prefs_file) as f:
        local_prefs = json.load(f)

    print(f"📋 Found {len(local_prefs)} local preferences to push:\n")
    for key, value in local_prefs.items():
        await push_preference(client, agent_engine_name, user_id, value)

    print("\n✅ Push complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
