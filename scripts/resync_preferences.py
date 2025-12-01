#!/usr/bin/env python3
"""
Re-sync local preferences to Vertex AI Memory Bank.

This script reads your local preferences file and saves each preference
to Memory Bank as an individual memory fact.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import Config
from agents.preference_agent import PreferenceManager
from agents.activity_agent import CalendarConnector


async def main():
    print("\n" + "=" * 70)
    print("🔄 Re-syncing Preferences to Memory Bank")
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

    # Initialize preference manager
    pref_manager = PreferenceManager(
        use_vertex_ai=True,
        project_id=Config.GOOGLE_CLOUD_PROJECT,
        location=Config.GOOGLE_CLOUD_LOCATION,
        agent_engine_id=Config.AGENT_ENGINE_ID,
        user_id=user_id
    )

    await pref_manager.initialize_memory_bank()

    # Get all local preferences
    local_prefs = pref_manager.get_all_preferences()
    print(f"\n📋 Found {len(local_prefs)} local preferences:")
    for key, value in local_prefs.items():
        print(f"   - {key}: {value}")

    # Re-save each preference to Memory Bank
    print(f"\n💾 Re-saving to Memory Bank...")
    for key, value in local_prefs.items():
        await pref_manager._save_to_memory_bank(key, value)

    print("\n✅ Re-sync complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
