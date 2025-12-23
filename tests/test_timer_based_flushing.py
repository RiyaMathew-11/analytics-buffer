"""
Unit tests for AnalyticsBuffer covering timer based flushing.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from analytics_buffer import AnalyticsBuffer


class TestTimerBasedFlushing:

    def test_flushes_after_interval_without_filling_buffer(self):
        """Test buffer flushes after interval even if not full."""
        mock_api = Mock()
        buffer = AnalyticsBuffer(
            max_size=10,
            flush_interval=1.0,  # Short interval for testing
            api_callable=mock_api,
        )

        # Add only 3 events (buffer not full)
        for i in range(3):
            buffer.track({"event": f"click_{i}"})

        # Should not flush immediately
        time.sleep(0.3)
        assert mock_api.call_count == 0

        # Wait for timer to fire
        time.sleep(1.0)

        # Should have flushed
        assert mock_api.call_count == 1
        assert len(mock_api.call_args[0][0]) == 3

        buffer.shutdown()

    def test_timer_resets_after_buffer_flush(self):
        """Test timer resets when buffer flushes due to size."""
        mock_api = Mock()
        buffer = AnalyticsBuffer(
            max_size=5, flush_interval=2.0, api_callable=mock_api
        )

        # Fill buffer (triggers size-based flush)
        for i in range(5):
            buffer.track({"event": f"click_{i}"})

        time.sleep(0.2)  # Wait for flush

        # Add 2 more events
        buffer.track({"event": "click_5"})
        buffer.track({"event": "click_6"})

        time.sleep(1.0)

        # Should NOT have flushed yet (timer was reset)
        assert mock_api.call_count == 1

        # Wait for new timer to complete
        time.sleep(1.5)

        # Now should flush the 2 new events
        assert mock_api.call_count == 2

        buffer.shutdown()

    def test_no_double_flush(self):
        """Test we don't get double flush from buffer and timer."""
        mock_api = Mock()
        buffer = AnalyticsBuffer(
            max_size=5,
            flush_interval=0.5,  # Short interval
            api_callable=mock_api,
        )

        # Fill buffer right before timer would fire
        for i in range(5):
            buffer.track({"event": f"click_{i}"})

        # Wait for both buffer flush and where timer would fire
        time.sleep(1.0)

        # Should only flush once (timer should be cancelled)
        assert mock_api.call_count == 1

        buffer.shutdown()
