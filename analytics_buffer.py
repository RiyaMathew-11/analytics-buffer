import threading
import time
from typing import Any, Dict, List, Optional, Callable
import logging
from utils import default_api_call


class AnalyticsBuffer:

    def __init__(
        self, max_size: int, flush_interval: float, api_callable: Optional[Callable]
    ):
        """
        Initialize the AnalyticsBuffer.

        Args:
            max_size (int): Maximum size of the buffer.
            flush_interval (float): Interval at which the buffer is flushed (in seconds).
            api_callable (Optional[Callable]): A custom api function.

        Raises:
            ValueError: If max_size is less than or equal to 0.
            ValueError: If flush_interval is less than or equal to 0.
        """

        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")

        if flush_interval <= 0:
            raise ValueError("flush_interval must be greater than 0")

        # Configuration
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.api_callable = api_callable or default_api_call

        # State variables
        self.buffer: List[Dict[str, Any]] = []
        self.timer: Optional[threading.Timer] = None
        self.is_shutting_down = False
        self.is_flushing = False

        # Lock for thread-safe operations
        self.lock = threading.Lock()

        # Metrics (useful for testing and monitoring)
        self.total_events_tracked = 0
        self.successful_flushes = 0
        self.failed_flushes = 0

        logger.info(
            f"Initialised Analytics Buffer: max_items={max_items}, "
            f"flush_interval={flush_interval}s"
        )

        def track(self, event: Optional[Dict[str, Any]]) -> bool:
            """
            Args:
                event (Optional[Dict[str, Any]]): The dictionary of event data.

            Returns:
                bool: True if the event was tracked successfully, otherwise False.
            """
            # Handle None events
            if event is None:
                logger.warning("Attempted to track a None event - rejected")
                return False

            # Reject events during shutdown
            if self.is_shutting_down:
                logger.warning("Buffer is shutting down - rejecting event")
                return False

            with self.lock:

                self.buffer.append(event)
                self.total_events_tracked += 1

                logger.debug(
                    f"Event tracked. Buffer size: {len(self.buffer)}/{self.max_items}"
                )

                # Start timer if this is the first event
                if len(self.buffer) == 1 and self.timer is None:
                    self._start_timer()

                # Check if buffer is full
                if len(self.buffer) >= self.max_items:
                    logger.info(
                        f"Buffer full ({self.max_items} items) - triggering flush"
                    )
                    # Flush in a separate thread to keep track() non-blocking
                    threading.Thread(target=self.flush, daemon=True).start()

            return True

    def _start_timer(self):
        """
        Start a background timer that will trigger a flush after flush_interval.

        Note: Should only be called when holding self.lock
        """
        # Timer already running
        if self.timer is not None:
            return

        self.timer = threading.Timer(self.flush_interval, self.flush)
        self.timer.daemon = True  # Don't prevent program exit
        self.timer.start()

        logger.debug(f"Timer started: will flush in {self.flush_interval}s")

    def _flush(self):
        """
        Flush buffered events to the API:
        - Cancels existing timer to prevent double-flush
        - Sends events to API
        - On success: clears buffer and restarts timer if needed
        - On failure: preserves events in buffer for retry

        """
        with self.lock:
            # Prevent concurrent flushes
            if self.is_flushing:
                logger.debug("Flush in progress - skipping")
                return

            # Nothing to flush
            if len(self.buffer) == 0:
                logger.debug("Empty buffer - nothing to flush")
                # Cancel the timer if it's running
                if self.timer:
                    self.timer.cancel()
                    self.timer = None
                return

            self.is_flushing = True

            # Cancel existing timer to prevent double-flush
            if self.timer:
                self.timer.cancel()
                self.timer = None
                logger.debug("Timer cancelled")

            # Copy events to send (so we can restore on failure)
            events_to_send = self.buffer.copy()
            event_count = len(events_to_send)

        # API call happens outside the lock (to avoid blocking other operations)
        try:
            logger.info(f"Flushing {event_count} events to API...")
            self.api_call_function(events_to_send)

            # Call to action for success: Clear buffer and restart timer
            with self.lock:
                # Only clear the events we sent (new events might have arrived)
                self.buffer = self.buffer[event_count:]
                self.successful_flushes += 1
                self.is_flushing = False

                logger.info(f"✓ Successfully flushed {event_count} events")

                # Restart timer if buffer still has events
                if len(self.buffer) > 0:
                    self._start_timer()

        except Exception as error:
            # Call to action for failure - events remain in buffer for retry
            with self.lock:
                self.failed_flushes += 1
                self.is_flushing = False

                logger.error(f"Flush failed: {error}")
                logger.info(
                    f"Events preserved in buffer for retry. Buffer size: {len(self.buffer)}"
                )

                if len(self.buffer) > 0:
                    self._start_timer()

                # If API is permanently down, the buffer will keep growing. Need a max buffer size to prevent infinite growth. For now, the timer just restarts.

                # In production, need to implement a max buffer size or other strategies to prevent infinite growth.

    def flush_now(self):
        """
        Manually trigger an immediate flush.
        """
        logger.info("Triggering a manual flush")
        self._flush()

    def shutdown(self, timeout: float = 10.0):
        """
        Shutdown the buffer.

        Args:
            timeout: Maximum seconds to wait for final flush

        """
        logger.info("Shutting down Analytics Buffer...")

        self.is_shutting_down = True

        # Flush any remaining events
        self.flush_now()

        # Wait for flush to complete
        start_time = time.time()
        while self.is_flushing and (time.time() - start_time) < timeout:
            time.sleep(0.1)

        # Cancel timer
        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None

        logger.info(
            f"Shutdown complete. Final stats: "
            f"tracked={self.total_events_tracked}, "
            f"successful_flushes={self.successful_flushes}, "
            f"failed_flushes={self.failed_flushes}, "
            f"remaining_in_buffer={len(self.buffer)}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get current buffer statistics.

        Returns:
            Dictionary with buffer metrics
        """
        with self.lock:
            return {
                "buffer_size": len(self.buffer),
                "total_events_tracked": self.total_events_tracked,
                "successful_flushes": self.successful_flushes,
                "failed_flushes": self.failed_flushes,
                "is_timer_active": self.timer is not None,
                "is_flushing": self.is_flushing,
                "is_shutting_down": self.is_shutting_down,
            }
