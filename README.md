# Analytics Buffer

A thread-safe analytics event buffer that batches events and flushes them to an API endpoint based on buffer size or time interval.

## Features

- **Batch Processing**: Buffers events and flushes when buffer reaches `max_size`
- **Time-Based Flushing**: Automatically flushes after `flush_interval` seconds even if buffer isn't full
- **Thread-Safe**: Safe for concurrent event tracking from multiple threads
- **Non-Blocking**: `track()` returns immediately without waiting for flush
- **Error Handling**: Preserves events on API failure for retry
- **Graceful Shutdown**: Ensures all buffered events are flushed before exit

## Requirements

- Python 3.9+
- pipenv

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd the-patient-care
```

2. Install pipenv (if not already installed):
```bash
pip install pipenv
```

3. Install dependencies:
```bash
pipenv install --dev
```

## Running Tests

Run all tests:
```bash
pipenv run test
```

Or directly with pytest:
```bash
pipenv run pytest -v tests/
```

## Running the Demo

```bash
pipenv run python demo.py
```

## Project Structure

```
the-patient-care/
├── analytics_buffer.py    # Main AnalyticsBuffer class
├── utils.py               # Utility functions (mock API calls)
├── demo.py                # Demo script showing usage examples
├── tests/
│   ├── conftest.py                   # Pytest configuration
│   ├── test_basic_functionality.py   # Basic feature tests
│   ├── test_edge_cases.py            # Edge case tests
│   ├── test_error_handling.py        # Error handling tests
│   └── test_timer_based_flushing.py  # Timer-based flush tests
├── Pipfile                # Python dependencies
├── Pipfile.lock           # Locked dependency versions
└── README.md
```

## Usage

```python
from analytics_buffer import AnalyticsBuffer

# Create buffer with custom settings
buffer = AnalyticsBuffer(
    max_size=100,           # Flush when buffer reaches 100 events
    flush_interval=60.0,    # Or flush every 60 seconds
    api_callable=my_api_function  # Optional custom API function
)

# Track events
buffer.track({"event": "page_view", "page": "/home"})
buffer.track({"event": "button_click", "button_id": "signup"})

# Get current stats
stats = buffer.get_stats()
print(f"Buffer size: {stats['buffer_size']}")

# Graceful shutdown (flushes remaining events)
buffer.shutdown()
```

## Development (Optional)

| Command | Description |
|---------|-------------|
| `pipenv run format` | Format code with Black |
| `pipenv run lint` | Run Flake8 linter |
| `pipenv run typecheck` | Run MyPy type checker |
