"""
Demo script showing AnalyticsBuffer usage examples.
"""

import time
import logging
from analytics_buffer import AnalyticsBuffer
from utils import flaky_api

logging.basicConfig(level=logging.INFO)

def demo_buffer_size_flush():

    """Demonstrate buffer flushing when it reaches max_size."""
    print("-"*60)
    print("DEMO 1: Buffer Size-Based Flush")
    print("-"*60)
    
    buffer = AnalyticsBuffer(max_size = 5, flush_interval = 2.0)
    
    print(f"Buffer configuration: max_size = 5, flush_interval = 2s")
    print(f"Adding 5 events to trigger flush...\n")
    
    for i in range(5):
        event = {"event": "button_click", "button_id": f"btn_{i}", "timestamp": time.time()}
        buffer.track(event)
        print(f"  [{i+1}/5] Tracked: {event['event']}")
        time.sleep(0.2)
    
    print("\n✓ Buffer should have flushed (check logs above)")
    time.sleep(0.5)
    
    stats = buffer.get_stats()
    print(f"\nStats: {stats}")
    
    buffer.shutdown()
    print("\nBuffer shut down cleanly")

def demo_timer_flush():
    """Demonstrate timer-based flushing."""
    print("\n" + "-"*60)
    print("DEMO 2: Timer-Based Flush")
    print("-"*60)
    
    buffer = AnalyticsBuffer(max_size = 10, flush_interval = 2.0)
    
    print(f"Buffer configuration: max_size = 10, flush_interval = 2s")
    print(f"Adding only 3 events (buffer won't fill)...\n")
    
    for i in range(3):
        event = {"event": "page_view", "page": f"/page{i}"}
        buffer.track(event)
        print(f"  [{i+1}/3] Tracked: {event['event']}")
        time.sleep(0.3)
    
    print(f"\nWaiting 2 seconds for timer to trigger flush...")
    time.sleep(2.5)
    
    print("✓ Timer should have triggered flush (check logs above)")
    
    stats = buffer.get_stats()
    print(f"\nStats: {stats}")
    
    buffer.shutdown()
    print("\nBuffer shut down cleanly")

def demo_error_handling():

    """Demonstrate error handling and retry."""
    print("\n" + "-"*60)
    print("DEMO 3: Error Handling and Retry")
    print("-"*60)

    # Create API that fails first 2 times, then succeeds
    attempt_count = {"count": 0}
    
    buffer = AnalyticsBuffer(
        max_size = 3,
        flush_interval = 1.5,
        api_callable = lambda events: flaky_api(events, attempt_count)
    )

    print("Simulating flaky API (fails 2 times, then succeeds)")
    print("Adding 3 events to trigger first flush...\n")
    
    for i in range(3):
        buffer.track({"event": f"event_{i}"})
    
    print("\nWaiting for retries...")
    time.sleep(5.0)
    
    print(f"\nFinal attempt count: {attempt_count['count']}")
    print("✓ Events were preserved and eventually sent")
    
    stats = buffer.get_stats()
    print(f"\nStats: {stats}")
    
    buffer.shutdown()

# --------------------------------------------------- #

print("\nRunning demos for AnalyticsBuffer:\n")

demos = [
        # ("Buffer Size Flush", demo_buffer_size_flush),
        # ("Timer Flush", demo_timer_flush),
        ("Error Handling", demo_error_handling),
]

for name, demo_func in demos:
    try:
        demo_func()
    except Exception as e:
        print(f"\n✗ Demo '{name}' failed: {e}")

    time.sleep(1)

print("\nAll demos completed.")