"""
Unit tests for AnalyticsBuffer covering basic functionality.

"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from analytics_buffer import AnalyticsBuffer


class TestBasicFunction:

    def test_buffer_initialization(self):
        """Test buffer initializes with correct defaults."""
        buffer = AnalyticsBuffer()

        assert buffer.max_size == 10
        assert buffer.flush_interval == 5.0
        assert len(buffer.buffer) == 0
        assert buffer.total_events_tracked == 0

    def test_custom_configuration(self):
        """Test buffer accepts custom configuration."""
        buffer = AnalyticsBuffer(max_size=50, flush_interval=30.0)

        assert buffer.max_size == 50
        assert buffer.flush_interval == 30.0

    def test_invalid_configuration(self):
        """Test buffer rejects invalid configuration."""
        with pytest.raises(ValueError):
            AnalyticsBuffer(max_size=0)

        with pytest.raises(ValueError):
            AnalyticsBuffer(flush_interval=-1)

    def test_track_adds_event_to_buffer(self):
        """Test track() adds events to buffer."""
        buffer = AnalyticsBuffer()

        event = {"event": "button_clicked", "button_id": "submit"}
        result = buffer.track(event)

        assert result is True
        assert len(buffer.buffer) == 1
        assert buffer.buffer[0] == event
        assert buffer.total_events_tracked == 1

    def test_track_is_non_blocking(self):
        """Test track() returns immediately without waiting for flush."""
        buffer = AnalyticsBuffer()

        start_time = time.time()

        # Track 10 events (should trigger flush)
        for i in range(10):
            buffer.track({"event": f"click_{i}"})

        elapsed = time.time() - start_time

        # Should complete in < 0.5 seconds (non-blocking)
        assert elapsed < 0.5

        # Give background thread time to complete
        time.sleep(0.2)
        buffer.shutdown()
