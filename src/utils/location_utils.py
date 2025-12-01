"""
Location Detection Utilities

Provides multiple methods for detecting user location:
1. IP-based geolocation (primary)
2. Manual entry (fallback)
3. Browser geolocation (future enhancement with JavaScript component)
"""

import requests
from typing import Dict, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationDetector:
    """Enhanced location detection with multiple fallback options."""

    def __init__(self):
        self.last_location = None
        self.detection_history = []

    def get_ip_location(self) -> Optional[Dict[str, Any]]:
        """
        Get location based on IP address using ipapi.co API.

        Returns:
            Dictionary with location data or None if detection fails
        """
        try:
            response = requests.get('https://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()

                location_data = {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', ''),
                    'region_code': data.get('region_code', ''),
                    'country': data.get('country_name', ''),
                    'country_code': data.get('country_code', ''),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timezone': data.get('timezone', ''),
                    'postal': data.get('postal', ''),
                    'location_string': self._format_location_string(
                        data.get('city', 'Unknown'),
                        data.get('region', ''),
                        data.get('country_code', '')
                    ),
                    'method': 'IP-based',
                    'accuracy': 'city',
                    'raw_data': data
                }

                self.last_location = location_data
                self._log_detection('ip', True, location_data)

                logger.info(f"IP-based location detected: {location_data['location_string']}")
                return location_data

            else:
                logger.warning(f"IP location API returned status code: {response.status_code}")
                self._log_detection('ip', False, {'status_code': response.status_code})
                return None

        except requests.Timeout:
            logger.error("IP location detection timed out")
            self._log_detection('ip', False, {'error': 'timeout'})
            return None
        except requests.RequestException as e:
            logger.error(f"IP location detection failed: {e}")
            self._log_detection('ip', False, {'error': str(e)})
            return None
        except Exception as e:
            logger.error(f"Unexpected error in IP location detection: {e}")
            self._log_detection('ip', False, {'error': str(e)})
            return None

    def get_ip_location_alternative(self) -> Optional[Dict[str, Any]]:
        """
        Alternative IP-based location detection using ip-api.com.

        Fallback option if ipapi.co fails.
        """
        try:
            response = requests.get('http://ip-api.com/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()

                if data.get('status') == 'success':
                    location_data = {
                        'city': data.get('city', 'Unknown'),
                        'region': data.get('regionName', ''),
                        'region_code': data.get('region', ''),
                        'country': data.get('country', ''),
                        'country_code': data.get('countryCode', ''),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone', ''),
                        'postal': data.get('zip', ''),
                        'location_string': self._format_location_string(
                            data.get('city', 'Unknown'),
                            data.get('regionName', ''),
                            data.get('countryCode', '')
                        ),
                        'method': 'IP-based (alternative)',
                        'accuracy': 'city',
                        'raw_data': data
                    }

                    self.last_location = location_data
                    self._log_detection('ip_alternative', True, location_data)

                    logger.info(f"Alternative IP location detected: {location_data['location_string']}")
                    return location_data

            return None

        except Exception as e:
            logger.error(f"Alternative IP location detection failed: {e}")
            self._log_detection('ip_alternative', False, {'error': str(e)})
            return None

    def create_manual_location(self, location_string: str) -> Dict[str, Any]:
        """
        Create location data from manual entry.

        Args:
            location_string: User-provided location string (e.g., "New York, NY")

        Returns:
            Dictionary with location data
        """
        # Parse the location string
        parts = [part.strip() for part in location_string.split(',')]

        city = parts[0] if len(parts) > 0 else location_string
        region = parts[1] if len(parts) > 1 else ''
        country = parts[2] if len(parts) > 2 else ''

        location_data = {
            'city': city,
            'region': region,
            'country': country,
            'location_string': location_string,
            'method': 'Manual entry',
            'accuracy': 'user_provided',
            'latitude': None,
            'longitude': None,
            'manual': True
        }

        self.last_location = location_data
        self._log_detection('manual', True, location_data)

        logger.info(f"Manual location created: {location_string}")
        return location_data

    def detect_location_auto(self) -> Optional[Dict[str, Any]]:
        """
        Automatically detect location with fallback chain:
        1. Try primary IP-based detection
        2. Try alternative IP-based detection
        3. Return None (manual entry required)

        Returns:
            Dictionary with location data or None
        """
        logger.info("Starting automatic location detection...")

        # Try primary IP detection
        location = self.get_ip_location()
        if location:
            return location

        # Try alternative IP detection
        logger.info("Primary IP detection failed, trying alternative...")
        location = self.get_ip_location_alternative()
        if location:
            return location

        logger.warning("All automatic location detection methods failed")
        return None

    def validate_location_string(self, location_string: str) -> Tuple[bool, str]:
        """
        Validate a location string for basic formatting.

        Args:
            location_string: Location string to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not location_string or len(location_string.strip()) == 0:
            return False, "Location cannot be empty"

        if len(location_string) < 2:
            return False, "Location is too short"

        if len(location_string) > 200:
            return False, "Location is too long"

        # Check for at least some alphabetic characters
        if not any(c.isalpha() for c in location_string):
            return False, "Location must contain letters"

        return True, "Valid location format"

    def geocode_location(self, location_string: str) -> Optional[Dict[str, Any]]:
        """
        Geocode a location string to get coordinates (future enhancement).

        This would use a geocoding API like OpenStreetMap Nominatim or Google Maps.
        Currently returns None as placeholder.

        Args:
            location_string: Location to geocode

        Returns:
            Dictionary with coordinates or None
        """
        # Placeholder for geocoding functionality
        # In production, this would call a geocoding API
        logger.info(f"Geocoding not yet implemented for: {location_string}")
        return None

    def _format_location_string(self, city: str, region: str, country_code: str) -> str:
        """
        Format a location string from components.

        Args:
            city: City name
            region: Region/state name
            country_code: Country code

        Returns:
            Formatted location string
        """
        parts = [city]

        if region:
            parts.append(region)
        elif country_code and country_code != 'US':
            # Show country code if no region and not US
            parts.append(country_code)

        return ', '.join(parts)

    def _log_detection(self, method: str, success: bool, data: Dict[str, Any]):
        """
        Log detection attempt for debugging and analytics.

        Args:
            method: Detection method used
            success: Whether detection succeeded
            data: Detection data or error info
        """
        from datetime import datetime

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'success': success,
            'data': data
        }

        self.detection_history.append(log_entry)

        # Keep only last 50 entries
        if len(self.detection_history) > 50:
            self.detection_history = self.detection_history[-50:]

    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about location detection attempts.

        Returns:
            Dictionary with detection statistics
        """
        if not self.detection_history:
            return {
                'total_attempts': 0,
                'success_rate': 0,
                'methods_used': []
            }

        total = len(self.detection_history)
        successful = sum(1 for entry in self.detection_history if entry['success'])
        methods = list(set(entry['method'] for entry in self.detection_history))

        return {
            'total_attempts': total,
            'successful_attempts': successful,
            'success_rate': successful / total if total > 0 else 0,
            'methods_used': methods,
            'last_location': self.last_location
        }


# Convenience functions for quick usage
def detect_location() -> Optional[Dict[str, Any]]:
    """
    Quick function to detect location automatically.

    Returns:
        Dictionary with location data or None
    """
    detector = LocationDetector()
    return detector.detect_location_auto()


def create_location(location_string: str) -> Dict[str, Any]:
    """
    Quick function to create location from manual entry.

    Args:
        location_string: User-provided location string

    Returns:
        Dictionary with location data
    """
    detector = LocationDetector()
    return detector.create_manual_location(location_string)


def validate_location(location_string: str) -> Tuple[bool, str]:
    """
    Quick function to validate location string.

    Args:
        location_string: Location string to validate

    Returns:
        Tuple of (is_valid, message)
    """
    detector = LocationDetector()
    return detector.validate_location_string(location_string)


if __name__ == "__main__":
    # Test the location detection
    print("Testing Location Detection...")
    print("-" * 50)

    detector = LocationDetector()

    # Test automatic detection
    print("\n1. Testing automatic detection:")
    location = detector.detect_location_auto()
    if location:
        print(f"   ✓ Detected: {location['location_string']}")
        print(f"   Method: {location['method']}")
        print(f"   Coordinates: ({location.get('latitude')}, {location.get('longitude')})")
    else:
        print("   ✗ Automatic detection failed")

    # Test manual entry
    print("\n2. Testing manual entry:")
    manual_loc = detector.create_manual_location("San Francisco, CA")
    print(f"   ✓ Created: {manual_loc['location_string']}")

    # Test validation
    print("\n3. Testing validation:")
    test_strings = ["New York, NY", "London", "", "A", "123"]
    for test_str in test_strings:
        valid, msg = detector.validate_location_string(test_str)
        status = "✓" if valid else "✗"
        print(f"   {status} '{test_str}': {msg}")

    # Show stats
    print("\n4. Detection statistics:")
    stats = detector.get_detection_stats()
    print(f"   Total attempts: {stats['total_attempts']}")
    print(f"   Success rate: {stats['success_rate']*100:.1f}%")
    print(f"   Methods used: {', '.join(stats['methods_used'])}")

    print("\n" + "-" * 50)
    print("Location detection test complete!")
