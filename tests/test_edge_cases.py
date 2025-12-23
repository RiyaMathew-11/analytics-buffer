"""
Unit tests for AnalyticsBuffer covering edge cases.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from analytics_buffer import AnalyticsBuffer


class TestEdgeCases:

    def test_track_none_event(self):
        """Test tracking None event is rejected."""
        buffer = AnalyticsBuffer()

        result = buffer.track(None)

        assert result is False
        assert len(buffer.buffer) == 0
        assert buffer.total_events_tracked == 0

    def test_track_empty_dict_event(self):
        """Test tracking empty dict is allowed."""
        buffer = AnalyticsBuffer()

        result = buffer.track({})

        assert result is True
        assert len(buffer.buffer) == 1
        assert buffer.total_events_tracked == 1

        buffer.shutdown()

    def test_concurrent_tracking(self):
        """Test buffer handles concurrent track() calls."""
        mock_api = Mock()
        buffer = AnalyticsBuffer(max_size=100, api_callable=mock_api)

        # Track events from multiple threads
        def track_events(thread_id, count):
            for i in range(count):
                buffer.track({"thread": thread_id, "event": i})

        threads = []
        for i in range(5):
            thread = threading.Thread(target=track_events, args=(i, 20))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should have tracked all events
        assert buffer.total_events_tracked == 100

        buffer.shutdown()

    def test_flush_empty_buffer(self):
        """Test flushing empty buffer doesn't crash."""
        mock_api = Mock()
        buffer = AnalyticsBuffer(api_callable=mock_api)

        buffer.flush_now()

        # API should not be called for empty buffer
        assert mock_api.call_count == 0

    def test_shutdown_rejects_new_events(self):
        """Test events are rejected after shutdown."""
        buffer = AnalyticsBuffer()

        buffer.shutdown()

        result = buffer.track({"event": "after_shutdown"})

        assert result is False

    def test_shutdown_flushes_remaining_events(self):
        """Test shutdown flushes any remaining events."""
        mock_api = Mock()
        buffer = AnalyticsBuffer(api_callable=mock_api)

        # Add events
        for i in range(3):
            buffer.track({"event": f"click_{i}"})

        buffer.shutdown()

        assert mock_api.call_count == 1
        assert len(mock_api.call_args[0][0]) == 3
