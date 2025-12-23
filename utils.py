import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def default_api_call(events: List[Dict[str, Any]]):
    """
    Mock API call that simulates network delay.

    In real implementation, this would be replaced with actual HTTP request:

    async def real_api_call(events):
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=events) as response:
                response.raise_for_status()

    Args:
        events: List of events to send

    Raises:
        Exception: Simulated API failure (for testing)
    """
    # Simulate network delay
    time.sleep(0.1)

    # Mock successful API response
    logger.debug(f"Mock API received {len(events)} events")

    # In production, make the actual HTTP request here:
    # response = requests.post('https://api.example.com/events', json=events)
    # response.raise_for_status()

def flaky_api(events, attempt_count: dict):
    """
    Mock API call that fails first 2 times, then succeeds.
    """
    attempt_count["count"] += 1
    if attempt_count["count"] <= 2:
        print(f"  ✗ API call #{attempt_count['count']} failed (simulated)")
        raise Exception("Simulated API failure")
    else:
        print(f"  ✓ API call #{attempt_count['count']} succeeded!")


def user_session(user_id: int, action_count: int, buffer: "AnalyticsBuffer"):
    """Simulate user session with multiple actions."""
    for i in range(action_count):
        event = {
            "user_id": user_id,
            "event": "action",
            "action_number": i,
            "timestamp": time.time()
        }
        buffer.track(event)
        time.sleep(0.1)