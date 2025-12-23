"""
Unit tests for AnalyticsBuffer covering error handling.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from analytics_buffer import AnalyticsBuffer


class TestErrorHandling:
    """Test error handling and retry logic."""

    def test_events_preserved_on_api_failure(self):
        """Test events remain in buffer when API fails."""
        # Create API that always fails
        mock_api = Mock(side_effect=Exception("API Error"))
        buffer = AnalyticsBuffer(max_size=5, api_callable=mock_api)

        # Add events
        for i in range(5):
            buffer.track({"event": f"click_{i}"})

        time.sleep(0.2)  # Wait for flush attempt

        # API should have been called
        assert mock_api.call_count == 1

        # Events should still be in buffer
        assert len(buffer.buffer) == 5
        assert buffer.failed_flushes == 1

        buffer.shutdown()

    def test_retry_after_failure(self):
        """Test buffer retries after API failure."""
        # API fails first time, succeeds second time
        mock_api = Mock(side_effect=[Exception("API Error"), None])  # Success

        buffer = AnalyticsBuffer(
            max_size=10, flush_interval=0.5, api_callable=mock_api
        )

        # Add events and trigger first flush (will fail)
        for i in range(10):
            buffer.track({"event": f"click_{i}"})

        time.sleep(0.2)

        # First flush failed
        assert mock_api.call_count == 1
        assert len(buffer.buffer) == 10

        # Wait for timer to trigger retry
        time.sleep(0.6)

        # Second flush succeeded
        assert mock_api.call_count == 2
        assert len(buffer.buffer) == 0

        buffer.shutdown()

    def test_tracks_failure_metrics(self):
        """Test buffer tracks failure statistics."""
        mock_api = Mock(side_effect=Exception("API Error"))
        buffer = AnalyticsBuffer(max_size=3, api_callable=mock_api)

        # Trigger multiple failed flushes
        for batch in range(3):
            for i in range(3):
                buffer.track({"event": f"batch{batch}_event{i}"})
            time.sleep(0.2)

        stats = buffer.get_stats()
        assert stats["failed_flushes"] >= 1
        assert stats["successful_flushes"] == 0

        buffer.shutdown()
