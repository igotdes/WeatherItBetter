"""
Preference Agent - User Preference Management

Stores and retrieves user preferences for outfit recommendations using
Vertex AI Memory Bank for persistent cloud storage.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Vertex AI Memory imports
try:
    from google.adk.memory import VertexAiMemoryBankService
    from google.adk.sessions import Session
    VERTEX_AI_AVAILABLE = True
except (ImportError, AttributeError) as e:
    VERTEX_AI_AVAILABLE = False
    # Silently fall back - will print warning when PreferenceManager is initialized
    VertexAiMemoryBankService = None
    Session = None


class PreferenceManager:
    """
    Manages user preferences for outfit recommendations.

    Uses Vertex AI Memory Bank for persistent cloud storage,
    with file-based fallback for local development.
    """

    def __init__(
        self,
        storage_path: str = 'data/preferences.json',
        use_vertex_ai: bool = True,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        agent_engine_id: Optional[str] = None,
        user_id: str = "default_user"
    ):
        """
        Initialize preference manager.

        Args:
            storage_path: Path to JSON file for local storage backup
            use_vertex_ai: Whether to use Vertex AI Memory Bank
            project_id: Google Cloud project ID
            location: GCP location (e.g., 'us-central1')
            agent_engine_id: Vertex AI Agent Engine ID
            user_id: User identifier for memory bank
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.user_id = user_id
        self.app_name = "weatheritbetter"

        # File-based storage (always used as backup)
        self.preferences = self._load_preferences_from_file()

        # Vertex AI Memory Bank setup
        self.use_vertex_ai = use_vertex_ai and VERTEX_AI_AVAILABLE
        self.memory_service = None
        self.preferences_loaded_from = "local_file"  # Track source

        if self.use_vertex_ai:
            if not all([project_id, location, agent_engine_id]):
                print("\n" + "=" * 70)
                print("⚠️  VERTEX AI CREDENTIALS INCOMPLETE")
                print("=" * 70)
                print("   Using file-based preference storage")
                print(f"   Storage location: {self.storage_path}")
                print("=" * 70 + "\n")
                self.use_vertex_ai = False
            else:
                try:
                    self._initialize_vertex_ai(project_id, location, agent_engine_id)
                except Exception as e:
                    print("\n" + "=" * 70)
                    print("⚠️  FAILED TO INITIALIZE VERTEX AI MEMORY BANK")
                    print("=" * 70)
                    print(f"   Error: {e}")
                    print("   Falling back to file-based storage")
                    print(f"   Storage location: {self.storage_path}")
                    print("=" * 70 + "\n")
                    self.use_vertex_ai = False
        else:
            if not VERTEX_AI_AVAILABLE:
                print("\n" + "=" * 70)
                print("ℹ️  VERTEX AI NOT AVAILABLE")
                print("=" * 70)
                print("   google-adk package not installed or incompatible")
                print("   Using file-based preference storage")
                print(f"   Storage location: {self.storage_path}")
                print("=" * 70 + "\n")

    def _initialize_vertex_ai(self, project_id: str, location: str, agent_engine_id: str):
        """Initialize Vertex AI Memory Bank and Session services."""
        print("\n" + "=" * 70)
        print("🔗 INITIALIZING VERTEX AI MEMORY BANK")
        print("=" * 70)
        print(f"   Project: {project_id}")
        print(f"   Location: {location}")
        print(f"   User: {self.user_id}")

        # Create Memory Bank service
        self.memory_service = VertexAiMemoryBankService(
            project=project_id,
            location=location,
            agent_engine_id=agent_engine_id
        )

        print("✅ Vertex AI Memory Bank connected successfully!")
        print("   Storage: Cloud-based (Vertex AI)")
        print("   Backup: Local file (data/preferences.json)")
        print("=" * 70 + "\n")

    async def initialize_memory_bank(self):
        """
        Load preferences from Vertex AI Memory Bank.

        This should be called after __init__ when running in an async context.
        """
        if not self.use_vertex_ai or not self.memory_service:
            return

        print("📥 Loading preferences from Vertex AI Memory Bank...")
        try:
            loaded_prefs = await self.load_from_memory_bank()
            if loaded_prefs:
                print(f"   ✅ Loaded {len(loaded_prefs)} preferences from cloud")
                self.preferences_loaded_from = "vertex_ai_memory_bank"
            else:
                print("   ℹ️  No preferences found in Memory Bank (new user or first run)")
                self.preferences_loaded_from = "local_file"
        except Exception as e:
            print(f"   ⚠️  Could not load from Memory Bank: {e}")
            print("   Using local file preferences")
            self.preferences_loaded_from = "local_file"

    def _load_preferences_from_file(self) -> Dict[str, str]:
        """Load preferences from local file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_preferences_to_file(self):
        """Save preferences to local file (backup)."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except IOError as e:
            print(f"⚠️  Warning: Could not save to file: {e}")

    async def _save_to_memory_bank(self, preference_key: str, preference_value: str):
        """Save a preference to Vertex AI Memory Bank using direct memory generation."""
        if not self.use_vertex_ai or not self.memory_service:
            return

        # Skip saving generic/useless preferences
        if "remember my clothing preferences" in preference_value.lower():
            return

        try:
            print(f"   💾 Saving preference to Memory Bank...")

            # Create a specific conversation for THIS preference only
            # Make it very clear what the preference is
            user_message = f"Please remember this about my clothing preferences: {preference_value}"
            assistant_message = f"Got it! I'll remember that you {preference_value}. I'll use this when making outfit recommendations."

            # Use Vertex AI client directly to generate memories
            import vertexai

            # Initialize Vertex AI client (sync with memory_service config)
            client = vertexai.Client(
                project=self.memory_service._project,
                location=self.memory_service._location
            )

            # Get the agent engine resource name
            agent_engine_name = f"projects/{self.memory_service._project}/locations/{self.memory_service._location}/reasoningEngines/{self.memory_service._agent_engine_id}"

            # Create events with natural conversation
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

            # Generate memories directly with explicit scope
            client.agent_engines.memories.generate(
                name=agent_engine_name,
                direct_contents_source={"events": events},
                scope={"user_id": self.user_id},
                config={"wait_for_completion": True}
            )

            print(f"   ✅ Preference saved to cloud")

        except Exception as e:
            print(f"   ⚠️  Warning: Could not save to Memory Bank: {e}")

    def add_preference(self, key: str, value: str):
        """
        Add or update a preference.

        Args:
            key: Preference identifier
            value: Preference value

        Example:
            >>> manager = PreferenceManager()
            >>> manager.add_preference("temp_preference", "prefers Celsius")
            >>> manager.add_preference("style", "business casual")
        """
        # Generate unique key if needed
        pref_id = f"pref_{len(self.preferences) + 1}" if key.startswith("pref_") else key

        # Store in memory
        self.preferences[pref_id] = value

        # Save to file (synchronous backup)
        self._save_preferences_to_file()

        # Save to Vertex AI Memory Bank (async, best effort)
        if self.use_vertex_ai:
            import asyncio
            try:
                # Try to get running loop, or create new one
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create task if loop is running
                    asyncio.create_task(self._save_to_memory_bank(pref_id, value))
                else:
                    # Run in new loop if no loop running
                    loop.run_until_complete(self._save_to_memory_bank(pref_id, value))
            except Exception as e:
                print(f"⚠️  Could not sync to Memory Bank: {e}")

    async def add_preference_async(self, key: str, value: str):
        """
        Add or update a preference (async version).

        Args:
            key: Preference identifier
            value: Preference value
        """
        pref_id = f"pref_{len(self.preferences) + 1}" if key.startswith("pref_") else key
        self.preferences[pref_id] = value
        self._save_preferences_to_file()

        if self.use_vertex_ai:
            await self._save_to_memory_bank(pref_id, value)

    def get_all_preferences(self) -> Dict[str, str]:
        """Get all stored preferences."""
        return self.preferences.copy()

    def get_preference_list(self) -> List[str]:
        """Get preferences as a list of values."""
        return list(self.preferences.values())

    def get_preference_source(self) -> str:
        """Get the source where preferences were loaded from."""
        return self.preferences_loaded_from

    def clear_preferences(self):
        """Clear all preferences."""
        self.preferences = {}
        self._save_preferences_to_file()

    async def load_from_memory_bank(self) -> Dict[str, str]:
        """
        Load preferences from Vertex AI Memory Bank using retrieve API.

        Returns:
            Dictionary of preferences loaded from memory bank
        """
        if not self.use_vertex_ai or not self.memory_service:
            return {}

        try:
            # Use Vertex AI client directly to retrieve memories
            import vertexai

            client = vertexai.Client(
                project=self.memory_service._project,
                location=self.memory_service._location
            )

            agent_engine_name = f"projects/{self.memory_service._project}/locations/{self.memory_service._location}/reasoningEngines/{self.memory_service._agent_engine_id}"

            # Retrieve memories with exact scope match
            search_results = client.agent_engines.memories.retrieve(
                name=agent_engine_name,
                scope={"user_id": self.user_id},
                similarity_search_params={
                    "search_query": "clothing preferences outfit style"
                }
            )

            # Extract preferences from retrieved memories
            loaded_prefs = {}
            memory_count = 0

            for result in search_results:
                memory_count += 1

                # The result has a nested 'memory' attribute containing the actual Memory object
                try:
                    # Access the nested memory object first
                    memory = result.memory if hasattr(result, 'memory') else result
                    fact_text = memory.fact

                    # Extract preference from the fact
                    # The fact should contain information about preferences
                    if fact_text and ('prefer' in fact_text.lower() or 'style' in fact_text.lower() or 'casual' in fact_text.lower() or 'formal' in fact_text.lower()):
                        pref_key = f"pref_{len(loaded_prefs) + 1}"
                        loaded_prefs[pref_key] = fact_text
                except (AttributeError, TypeError):
                    # Skip memories that don't have the expected structure
                    continue

            if loaded_prefs:
                self.preferences.update(loaded_prefs)
                self._save_preferences_to_file()

            return loaded_prefs
        except Exception as e:
            print(f"   ⚠️  Could not load from Memory Bank: {e}")

        return {}
