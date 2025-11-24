"""Clarity API client for fetching analytics data."""

import requests
import json
import time
from typing import Dict, List, Optional
from pathlib import Path
import config


class ClarityAPIClient:
    """Client for Microsoft Clarity Data Export API."""

    def __init__(self, api_token: Optional[str] = None):
        """Initialize Clarity API client.

        Args:
            api_token: JWT token for authentication (defaults to config)
        """
        self.api_token = api_token or config.CLARITY_API_TOKEN
        self.base_url = config.API_BASE_URL
        self.endpoint = config.API_ENDPOINT_PROJECT_INSIGHTS
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def fetch_project_insights(self,
                               num_days: int = 3,
                               dimension1: Optional[str] = None,
                               dimension2: Optional[str] = None,
                               dimension3: Optional[str] = None,
                               max_retries: int = 3) -> Dict:
        """Fetch project insights from Clarity API.

        Args:
            num_days: Number of days to fetch (1-3)
            dimension1: First dimension (e.g., 'Device', 'Country', 'Browser')
            dimension2: Second dimension
            dimension3: Third dimension
            max_retries: Maximum number of retry attempts

        Returns:
            API response as dictionary

        Raises:
            ValueError: If num_days is invalid
            requests.RequestException: If API request fails
        """
        # Validate num_days
        if num_days not in [1, 2, 3]:
            raise ValueError("num_days must be 1, 2, or 3")

        # Build query parameters
        params = {'numOfDays': num_days}
        if dimension1:
            params['dimension1'] = dimension1
        if dimension2:
            params['dimension2'] = dimension2
        if dimension3:
            params['dimension3'] = dimension3

        # Retry logic
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.endpoint, params=params, timeout=30)

                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"⚠️  Rate limit hit. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()

                # Parse JSON response
                data = response.json()

                return {
                    'success': True,
                    'status_code': response.status_code,
                    'data': data,
                    'params': params,
                    'response_size': len(response.content)
                }

            except requests.exceptions.Timeout as e:
                last_error = f"Request timeout: {e}"
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: Timeout")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP error: {e}"
                print(f"❌ HTTP Error {response.status_code}: {response.text[:200]}")
                # Don't retry on client errors (4xx)
                if 400 <= response.status_code < 500:
                    break

            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {e}"
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

            except json.JSONDecodeError as e:
                last_error = f"Invalid JSON response: {e}"
                print(f"❌ Invalid JSON response: {e}")
                break

        # All retries failed
        return {
            'success': False,
            'status_code': response.status_code if 'response' in locals() else None,
            'error': last_error,
            'params': params
        }

    def save_response_to_file(self, response_data: Dict, filename: str):
        """Save API response to JSON file.

        Args:
            response_data: Response dictionary from fetch_project_insights
            filename: Output filename (without path)
        """
        output_path = config.RAW_DATA_DIR / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(response_data, f, indent=2)

        print(f"💾 Saved to: {output_path}")
        return output_path

    def test_connection(self) -> bool:
        """Test API connection and authentication.

        Returns:
            True if connection successful, False otherwise
        """
        print("Testing Clarity API connection...")
        print(f"Endpoint: {self.endpoint}")
        print(f"Token: {self.api_token[:20]}...")

        result = self.fetch_project_insights(num_days=1)

        if result['success']:
            print("✅ Connection successful!")
            print(f"Status code: {result['status_code']}")
            print(f"Response size: {result['response_size']} bytes")

            # Show sample of data structure
            if result.get('data'):
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    print(f"Number of metric groups: {len(data)}")
                    print(f"Sample metric: {data[0].get('metricName', 'N/A')}")

            return True
        else:
            print("❌ Connection failed!")
            print(f"Error: {result.get('error')}")
            return False


def test_api_client():
    """Test API client functionality."""
    print("=" * 60)
    print("CLARITY API CLIENT TEST")
    print("=" * 60)

    # Initialize client
    client = ClarityAPIClient()

    # Test connection
    if not client.test_connection():
        print("\n❌ API connection test failed!")
        return False

    print("\n" + "=" * 60)
    print("✅ All API client tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_api_client()
