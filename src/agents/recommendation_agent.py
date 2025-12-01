"""
Recommendation Agent - Main Outfit Recommendation Engine

Combines weather data, calendar activities, and user preferences to generate
intelligent, personalized outfit recommendations using AI.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from google import genai
from google.genai import types

from .weather_agent import WeatherFetcher
from .activity_agent import CalendarConnector, ActivityDetector
from .preference_agent import PreferenceManager


class OutfitRecommendationAgent:
    """
    Main agent that orchestrates all data sources for outfit recommendations.

    Combines:
    1. Weather data (temperature, conditions)
    2. Calendar activities (meetings, exercise, etc.)
    3. User preferences (style, temperature sensitivity)

    Uses AI to generate contextual, personalized recommendations.
    """

    def __init__(
        self,
        google_api_key: str,
        weather_api_key: str,
        use_calendar: bool = True,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        agent_engine_id: Optional[str] = None,
        user_id: str = "default_user",
        calendar_connector: Optional['CalendarConnector'] = None
    ):
        """
        Initialize the recommendation agent.

        Args:
            google_api_key: Google AI API key for Gemini
            weather_api_key: OpenWeatherMap API key
            use_calendar: Whether to integrate Google Calendar (requires credentials)
            project_id: Google Cloud project ID for Vertex AI
            location: GCP location (e.g., 'us-central1')
            agent_engine_id: Vertex AI Agent Engine ID
            user_id: User identifier for preference memory (from authenticated email)
            calendar_connector: Pre-authenticated CalendarConnector instance

        Raises:
            ValueError: If required API keys are missing
        """
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        if not weather_api_key:
            raise ValueError("OPENWEATHER_API_KEY is required")

        # Initialize AI client
        self.client = genai.Client(api_key=google_api_key)
        self.model = "gemini-2.0-flash-exp"

        # Initialize data sources
        self.weather_fetcher = WeatherFetcher(weather_api_key)

        # Initialize preference manager with Vertex AI Memory Bank
        self.preference_manager = PreferenceManager(
            use_vertex_ai=True,
            project_id=project_id,
            location=location,
            agent_engine_id=agent_engine_id,
            user_id=user_id
        )

        # Calendar integration
        self.use_calendar = use_calendar
        if use_calendar:
            # Use provided calendar connector or create new one
            self.calendar_connector = calendar_connector if calendar_connector else CalendarConnector()
            self.activity_detector = ActivityDetector()

            # If we created a new connector, authenticate it
            if not calendar_connector:
                self.calendar_connector.authenticate()
        else:
            self.calendar_connector = None
            self.activity_detector = None

    async def initialize(self):
        """
        Initialize async components (Memory Bank).

        Should be called after __init__ in an async context.
        """
        await self.preference_manager.initialize_memory_bank()

    async def get_recommendation(self, location: str, 
                                 temperature_unit: str = "metric") -> str:
        """
        Generate outfit recommendation for a location.

        Args:
            location: City name (e.g., "Manila", "Tokyo")
            temperature_unit: "metric" (Celsius) or "imperial" (Fahrenheit)

        Returns:
            AI-generated outfit recommendation text

        Example:
            >>> agent = OutfitRecommendationAgent(google_key, weather_key)
            >>> recommendation = await agent.get_recommendation("Manila")
            >>> print(recommendation)
            For today's 28°C sunny weather in Manila:
            - Light cotton t-shirt
            - Shorts or light pants
            - Sunglasses and sun protection
            ...
        """
        # 1. Fetch weather data
        weather = self.weather_fetcher.get_weather(location, units=temperature_unit)

        if not weather['success']:
            return f"Unable to fetch weather: {weather['error']}"

        # 2. Get calendar activities (if enabled)
        activities = []
        if self.use_calendar and self.calendar_connector:
            if self.calendar_connector.authenticate():
                events = self.calendar_connector.get_todays_events()
                activities = [self.activity_detector.analyze_event(e) for e in events]

        # 3. Get user preferences
        preferences = self.preference_manager.get_preference_list()
        pref_source = self.preference_manager.get_preference_source()

        # 4. Build context for AI
        context = self._build_context(weather, activities, preferences, pref_source)

        # 5. Generate recommendation with AI
        recommendation = await self._generate_with_ai(context)

        return recommendation

    def _build_context(self, weather: Dict, activities: List[Dict],
                      preferences: List[str], pref_source: str = "unknown") -> str:
        """Build context string for AI prompt."""
        context = "# Outfit Recommendation Context\n\n"

        # Weather section
        context += "## Weather\n"
        context += f"- Location: {weather['city']}, {weather['country']}\n"
        context += f"- Temperature: {weather['temperature']}°{weather['units']}\n"
        context += f"- Feels like: {weather['feels_like']}°{weather['units']}\n"
        context += f"- Conditions: {weather['conditions']} ({weather['description']})\n"
        context += f"- Humidity: {weather['humidity']}%\n"
        context += f"- Wind: {weather['wind_speed']} m/s\n\n"

        # Activities section
        if activities:
            context += "## Today's Activities\n"
            for i, activity in enumerate(activities, 1):
                context += f"\n### Activity {i}: {activity['title']}\n"
                context += f"- Time: {activity['start_time']}\n"
                context += f"- Type: {activity['location_type']}\n"
                context += f"- Formality: {activity['formality']}\n"
                if activity['is_exercise']:
                    context += "- Includes exercise\n"
                if activity['is_outdoor']:
                    context += "- Outdoor activity\n"
            context += "\n"
        else:
            context += "## Activities\n"
            context += "- No specific activities scheduled\n\n"

        # Preferences section
        if preferences:
            source_label = "☁️ Cloud (Vertex AI)" if pref_source == "vertex_ai_memory_bank" else "💾 Local File"
            context += f"## User Preferences (Loaded from: {source_label})\n"
            for pref in preferences:
                context += f"- {pref}\n"
        else:
            context += "## User Preferences\n"
            context += "- No preferences set yet\n"

        return context

    async def _generate_with_ai(self, context: str) -> str:
        """Generate recommendation using AI."""
        system_instruction = """
You are an expert outfit recommendation assistant. Provide highly specific,
contextual outfit suggestions that reference actual weather data, activities,
and user preferences.

CRITICAL REQUIREMENTS:
1. ALWAYS mention the exact temperature and weather conditions in your opening
2. ALWAYS reference specific user preferences when making recommendations
3. ALWAYS explain WHY each item is recommended based on the context
4. Be SPECIFIC - mention fabrics, colors, and practical details

OUTPUT FORMAT:

Opening line format: "For your [activity] in [temperature]°[C/F] [conditions] weather:"

Then provide:
- SPECIFIC clothing items (not generic categories)
- For EACH item, explain WHY (reference weather, activity, or preference)
- Accessories with reasoning
- Practical considerations (sun exposure time, indoor/outdoor transitions, etc.)

End with:
"Reasoning: [Comprehensive explanation that ties together weather + activities + preferences]"

EXAMPLE STYLE:
"For your rooftop client lunch in 28°C sunny weather:

- Light-colored button-down shirt (professional + reflects sun)
- Dress pants or chinos (client meeting requires professional appearance)
- Sunglasses (rooftop = 1.5 hours of direct sun exposure)
- Skip the jacket outdoors, but bring light blazer (indoor AC afterward)
- Consider: Breathable fabric since you'll be outside during peak heat

Reasoning: Balancing professional appearance for client meeting with practical
outdoor comfort. While you typically get cold easily, 28°C rooftop seating
requires heat management. The blazer addresses your cold sensitivity for
air-conditioned indoor spaces afterward."

KEY PRINCIPLES:
- Reference EXACT temperature and conditions
- Quote or paraphrase user preferences when relevant
- Explain time-based factors (duration outdoors, time of day)
- Account for transitions (outdoor→indoor, sun→shade)
- Be conversational but professional
- Give specific fabric/color suggestions when relevant to weather
"""

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )

        prompt = f"""{context}

Based on this information, provide a detailed outfit recommendation following this format:

1. Start with: "For your [activity/day] in [exact temperature]°[C/F] [weather conditions]:"
2. List specific clothing items with explanations for each
3. Include accessories with reasoning
4. End with "Reasoning:" paragraph that ties everything together

Remember to:
- Quote the exact temperature and weather conditions
- Reference user preferences when making choices
- Explain WHY each item is recommended
- Consider practical details like sun exposure, indoor/outdoor transitions
- Be specific about fabrics, colors, and styles"""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            return f"Error generating recommendation: {str(e)}"

    async def chat(self, message: str) -> str:
        """
        Chat with the agent to add preferences or ask questions.

        Automatically extracts and saves preferences from natural language.

        Args:
            message: User message

        Returns:
            Agent response

        Example:
            >>> response = await agent.chat("I prefer Celsius")
            >>> print(response)
            Got it! I've saved: "prefers Celsius"
        """
        # Try to extract preference
        extraction_prompt = f"""
Is this message expressing a clothing or weather preference?
Message: "{message}"

Respond with JSON:
{{"is_preference": true/false, "preference": "extracted text or null"}}

Examples:
- "I prefer Celsius" → {{"is_preference": true, "preference": "prefers Celsius"}}
- "I don't like shorts" → {{"is_preference": true, "preference": "dislikes shorts"}}
- "What should I wear?" → {{"is_preference": false, "preference": null}}
"""

        try:
            config = types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=extraction_prompt,
                config=config
            )

            import json
            result = json.loads(response.text)

            # Save preference if detected
            if result.get('is_preference') and result.get('preference'):
                pref = result['preference']
                await self.preference_manager.add_preference_async(f"pref_{len(self.preference_manager.preferences) + 1}", pref)
                return f"✅ Saved preference: \"{pref}\"\nThis will be used in future recommendations."

            # Otherwise, have normal conversation
            return "I'm here to help with outfit recommendations! Ask for recommendations or tell me your preferences."

        except Exception as e:
            return f"Error: {str(e)}"
