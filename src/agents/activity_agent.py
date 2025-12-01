"""
Activity Agent - Calendar Integration

Connects to Google Calendar to fetch today's events and analyze activity types.
Helps recommend outfits based on scheduled activities.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarConnector:
    """Connects to Google Calendar and fetches events."""

    SCOPES = [
        'openid',
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/userinfo.email'  # To get user email
    ]

    def __init__(self, credentials_path: str = 'credentials.json',
                 token_path: str = 'token.json'):
        """
        Initialize calendar connector.

        Args:
            credentials_path: Path to OAuth credentials file
            token_path: Path to store/load authorization token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.credentials = None
        self.user_email = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API.

        Returns:
            bool: True if authentication successful

        Note:
            First run will open browser for authorization.
            Token is saved to token.json for subsequent runs.
        """
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=creds)
            self.credentials = creds

            # Get user email from token info
            self._extract_user_email()

            return True
        except Exception:
            return False

    def _extract_user_email(self):
        """Extract user email from OAuth token."""
        try:
            import json
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                    # Try to get email from token data
                    # The email might be in client_id or we need to fetch it
                    if self.credentials:
                        # Use OAuth2 API to get user info
                        import requests
                        headers = {'Authorization': f'Bearer {self.credentials.token}'}
                        response = requests.get(
                            'https://www.googleapis.com/oauth2/v2/userinfo',
                            headers=headers
                        )
                        if response.status_code == 200:
                            user_info = response.json()
                            self.user_email = user_info.get('email')
                            if self.user_email:
                                print(f"\n👤 Authenticated as: {self.user_email}\n")
                            else:
                                print(f"\n⚠️  Email not found in user info response")
                                print(f"   Response: {user_info}")
                                print("   Using default user ID\n")
                        else:
                            print(f"\n⚠️  OAuth API returned status {response.status_code}")
                            print(f"   Response: {response.text[:200]}")
                            print("   Using default user ID\n")
                            self.user_email = None
        except Exception as e:
            # Fallback to default if we can't get email
            self.user_email = None
            print(f"\n⚠️  Could not extract user email: {e}")
            print("   Using default user ID\n")

    def get_user_email(self) -> Optional[str]:
        """
        Get the authenticated user's email address.

        Returns:
            User's email address or None if not available
        """
        return self.user_email

    def get_todays_events(self) -> List[Dict[str, Any]]:
        """
        Fetch today's calendar events.

        Returns:
            List of event dictionaries with time, summary, location
        """
        if not self.service:
            return []

        try:
            # Get start and end of today
            now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now + timedelta(days=1)

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            formatted_events = []
            for event in events:
                formatted_events.append({
                    'summary': event.get('summary', 'Untitled Event'),
                    'location': event.get('location', ''),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                })

            return formatted_events

        except HttpError:
            return []


class ActivityDetector:
    """Analyzes calendar events to determine activity types and outfit requirements."""

    @staticmethod
    def analyze_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a calendar event to determine activity characteristics.

        Args:
            event: Event dictionary from calendar

        Returns:
            Dictionary with activity analysis including:
            - title, start_time, raw_location
            - location_type: office, outdoor, indoor, home
            - formality: casual, business_casual, formal
            - is_exercise, is_outdoor

        Example:
            >>> detector = ActivityDetector()
            >>> event = {'summary': 'Client Meeting', 'location': 'Office'}
            >>> analysis = detector.analyze_event(event)
            >>> print(analysis['formality'])
            'formal'
        """
        summary = event.get('summary', '').lower()
        location = event.get('location', '').lower()

        # Determine location type
        location_type = 'indoor'
        if any(word in location for word in ['park', 'outdoor', 'trail', 'beach']):
            location_type = 'outdoor'
        elif any(word in location for word in ['office', 'workplace']):
            location_type = 'office'
        elif any(word in location for word in ['home', 'house']):
            location_type = 'home'

        # Determine formality
        formality = 'casual'
        if any(word in summary for word in ['meeting', 'presentation', 'interview', 'client']):
            formality = 'formal'
        elif any(word in summary for word in ['work', 'office', 'business']):
            formality = 'business_casual'

        # Check for exercise
        is_exercise = any(word in summary for word in 
                         ['gym', 'workout', 'run', 'exercise', 'yoga', 'fitness'])

        # Check for outdoor
        is_outdoor = location_type == 'outdoor' or \
                    any(word in summary for word in ['outdoor', 'outside', 'park', 'hike'])

        return {
            'title': event.get('summary', 'Event'),
            'start_time': event.get('start', ''),
            'raw_location': event.get('location', ''),
            'location_type': location_type,
            'formality': formality,
            'is_exercise': is_exercise,
            'is_outdoor': is_outdoor
        }
