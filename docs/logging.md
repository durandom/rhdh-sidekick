# B4RT Logging Guide

This document describes B4RT's logging system designed for efficient debugging and AI agent assistance.

## Overview

B4RT uses [loguru](https://github.com/Delgan/loguru) with:
- Environment variable configuration (`LOG_LEVEL`, `LOG_FILE`, `LOG_FORMAT`)
- CLI-based log level control (`-v`, `--log-level`, `--log-file`)
- Automatic pytest integration (logs to `logs/test-b4rt.log`)
- Comprehensive instrumentation throughout the codebase

## Quick Start

### Basic CLI Usage

```bash
# Default logging (INFO level to stderr)
uv run b4rt command

# Enable debug logging
uv run b4rt -v command

# Enable trace logging (most verbose)
uv run b4rt -vv command

# Log to file
uv run b4rt --log-file=debug.log command
```

### Environment Variables

```bash
# Standard environment variables (preferred)
export LOG_LEVEL=DEBUG
export LOG_FILE=logs/b4rt.log
export LOG_FORMAT=pretty

# Legacy environment variables (backward compatible)
export LOGGING__LEVEL=DEBUG
export LOGGING__FILE=logs/b4rt.log
export LOGGING__FORMAT=pretty
```

## Log Levels

| Level | Description | CLI Flag |
|-------|-------------|----------|
| `INFO` | User-facing actions (default) | Default |
| `DEBUG` | Decision points and algorithm steps | `-v` |
| `TRACE` | Function entry/exit and detailed flow | `-vv` |
| `WARNING` | Recoverable issues and deprecations | - |
| `ERROR` | Error conditions and exceptions | - |

## Log Locations

```
logs/
├── test-b4rt.log      # Pytest session logs (automatic)
├── b4rt.log           # Main application log (if configured)
└── custom.log         # User-specified log files
```

## Makefile Targets (Recommended)

### Log Management
```bash
make clean-logs              # Remove all log files
make show-recent-logs        # Show recent log entries
make monitor-logs            # Monitor logs in real-time
```

### Testing with Logging
```bash
make test-with-logs          # Run all tests with log monitoring
make test-unit-with-logs     # Run unit tests with logging
make test-performance-with-logs # Run performance tests with logging
```

### Log Filtering
```bash
make filter-logs-errors      # Show errors and warnings
make filter-logs-stream      # Show stream processing logs
make filter-logs-performance # Show performance logs
make filter-logs-detectors   # Show event detector logs
make filter-logs-session     # Show session management logs
```

### Analysis & Help
```bash
make analyze-log-levels      # Count log entries by level
make help-logs              # Show all logging targets
```

## AI Agent Usage

### Common Debugging Patterns

```bash
# Check for issues
make filter-logs-errors

# Debug stream processing
make filter-logs-stream

# Monitor test execution
make test-with-logs

# Real-time debugging
make monitor-logs
```

### Understanding Execution Flow

The logging provides visibility into:
1. **Data Loading**: File loading, DataFrame creation, data validation
2. **Session Setup**: Game detection, landmark loading, session metadata
3. **Stream Processing**: Data conversion, event detection pipeline
4. **Performance**: Processing throughput, memory usage, timing metrics
5. **Error Handling**: Failure points, recovery strategies, fallback behavior

### Example Log Output

```
2025-07-09 20:47:19 | INFO     | tests.conftest:configure_test_logging:78 | Starting B4RT test session
2025-07-09 20:47:19 | DEBUG    | b4rt.stream.stream:from_parquet:53 | Loaded parquet file: /path/to/session.parquet, shape: (2132, 35)
2025-07-09 20:47:19 | DEBUG    | b4rt.stream.stream:from_dataframe:75 | Created SessionInfo: session_id=1732892968, game=Richard Burns Rally
2025-07-09 20:47:19 | INFO     | b4rt.stream.stream:detect_events:205 | Starting event detection with 7 detectors
```

## Best Practices

### For Development
1. Use `make test-with-logs` for debugging tests
2. Use `make filter-logs-errors` to check for issues
3. Use `make monitor-logs` for real-time debugging
4. Use `make filter-logs-stream` for stream processing issues

### For CI/CD
1. Always enable file logging in CI environments
2. Archive log files as build artifacts
3. Use JSON format for structured log analysis
4. Set appropriate log levels for different environments

## Manual Commands (Alternative)

If you prefer manual commands over Makefile targets:

```bash
# View recent test logs
tail -20 logs/test-b4rt.log

# Filter for errors
grep -E "(ERROR|WARNING)" logs/test-b4rt.log

# Filter for stream processing
grep "b4rt.stream" logs/test-b4rt.log

# Monitor logs in real-time
tail -f logs/test-b4rt.log

# Run tests with logging
uv run pytest tests/ -v && tail -20 logs/test-b4rt.log
```

## Troubleshooting

### Common Issues
1. **No log output**: Check log level settings
2. **Permission errors**: Ensure `logs/` directory is writable
3. **Log file not created**: Verify file path and directory permissions
4. **Pytest logs missing**: Check that tests are actually running

### Debug Commands
```bash
# Check current logging configuration
uv run python -c "from src.b4rt.settings import settings; print(f'Level: {settings.logging.level}'); print(f'File: {settings.logging.file}')"

# Verify environment variables
env | grep LOG

# Check log file permissions
ls -la logs/
```

This logging system provides comprehensive visibility into B4RT's execution, making it ideal for both human debugging and AI agent assistance.
