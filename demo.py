"""
Demo script showing AnalyticsBuffer usage examples.
"""

import time
import logging
import threading
from analytics_buffer import AnalyticsBuffer
from utils import flaky_api, user_session

logging.basicConfig(level=logging.INFO)

def demo_buffer_size_flush():

    """Demonstrate buffer flushing when it reaches max_size."""
    print("-"*60)
    print("DEMO 1: Buffer Size-Based Flush")
    print("-"*60)
    
    # Try a custom configuration
    buffer = AnalyticsBuffer(max_size = 10, flush_interval = 2.0)
    
    print(f"Buffer configuration: max_size = 10, flush_interval = 2s")
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

    print("Simulating flaky API")
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

def demo_concurrent_usage():
    """Demonstrate concurrent event tracking."""
    print("\n" + "-"*60)
    print("DEMO 4: Concurrent Event Tracking")
    print("-"*60)
    
    buffer = AnalyticsBuffer(max_size = 20, flush_interval = 3.0)
    
    print("Simulating multiple threads tracking events concurrently...\n")
    
    # Simulate 3 concurrent users
    threads = []
    for user_id in range(1, 4):
        print(f"User {user_id} starting session with 8 actions...")
        thread = threading.Thread(target=user_session, args=(user_id, 8, buffer))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    print("✓ All threads completed")
    
    # Give time for final flush
    time.sleep(1.0)
    
    stats = buffer.get_stats()
    print(f"\nStats: {stats}")
    print(f"Total events tracked: {stats['total_events_tracked']}")
    
    buffer.shutdown()

def demo_edge_cases():
    """Demonstrate edge case handling."""
    print("\n" + "-"*60)
    print("DEMO 5: Edge Cases")
    print("-"*60)
    
    buffer = AnalyticsBuffer()
    
    print("Testing edge cases:\n")
    
    # Test 1: None event
    print("1. Tracking None event:")
    result = buffer.track(None)
    print(f"Result: {result}")
    
    # Test 2: Empty dict
    print("\n2. Tracking empty dict:")
    result = buffer.track({})
    print(f"Result: {result}")
    
    # Test 3: Valid event
    print("\n3. Tracking valid event:")
    result = buffer.track({"event": "click"})
    print(f"Result: {result}")
    
    # Test 4: Manual flush
    print("\n4. Manual flush:")
    buffer.flush_now()
    time.sleep(0.5)
    print("✓ Manual flush completed")
    
    # Test 5: Shutdown and reject
    print("\n5. Shutdown and attempt to track:")
    buffer.shutdown()
    result = buffer.track({"event": "after_shutdown"})
    print(f"Result: {result}")
    
    print("\n✓ All edge cases handled gracefully")

# --------------------------------------------------- #

print("\nRunning demos for AnalyticsBuffer:\n")

demos = [
        # ("Buffer Size Flush", demo_buffer_size_flush),
        # ("Timer Flush", demo_timer_flush),
        # ("Error Handling", demo_error_handling),
        # ("Concurrent Usage", demo_concurrent_usage),
        ("Edge Cases", demo_edge_cases)
]

for name, demo_func in demos:
    try:
        demo_func()
    except Exception as e:
        print(f"\n✗ Demo '{name}' failed: {e}")

    time.sleep(1)

print("\nAll demos completed.")