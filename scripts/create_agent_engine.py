"""
Create a new Agent Engine with Memory Bank enabled.

Run this script once to create the Agent Engine, then copy the ID to your .env file.
"""

import vertexai

# Configuration
PROJECT_ID = "pure-stronghold-477813-j2"  # Your project ID
LOCATION = "asia-southeast1"  # Your region

def create_agent_engine():
    """Create a new Agent Engine with Memory Bank enabled."""
    print("=" * 70)
    print("Creating Agent Engine with Memory Bank")
    print("=" * 70)
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}\n")

    # Initialize Vertex AI client
    client = vertexai.Client(
        project=PROJECT_ID,
        location=LOCATION,
    )

    print("Creating Agent Engine (this may take a moment)...")

    # Create Agent Engine (Memory Bank is automatically enabled with defaults)
    agent_engine = client.agent_engines.create()

    print("\n" + "=" * 70)
    print("✅ SUCCESS - Agent Engine Created!")
    print("=" * 70)
    print(f"\nFull resource name:")
    print(f"  {agent_engine.api_resource.name}\n")

    # Extract the numeric ID
    agent_engine_id = agent_engine.api_resource.name.split("/")[-1]

    print(f"Agent Engine ID (copy this to your .env file):")
    print(f"  {agent_engine_id}\n")

    print("=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print(f"1. Update your .env file:")
    print(f"   AGENT_ENGINE_ID={agent_engine_id}")
    print(f"\n2. Restart your application")
    print(f"\n3. Memory Bank should now work correctly!")
    print("=" * 70)

    return agent_engine_id

if __name__ == "__main__":
    try:
        create_agent_engine()
    except Exception as e:
        print(f"\n❌ Error creating Agent Engine: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you have Vertex AI API enabled")
        print("2. Run: gcloud auth application-default login")
        print("3. Verify you have 'Vertex AI User' role")
        print("4. Check that google-cloud-aiplatform>=1.111.0 is installed")
