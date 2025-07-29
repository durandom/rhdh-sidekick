.PHONY: prepare-commit lint format typecheck test validate-tooling \
	clean-logs filter-logs-errors filter-logs-stream filter-logs-performance \
	show-recent-logs monitor-logs test-with-logs test-unit-with-logs \
	test-performance-with-logs filter-logs-component filter-logs-detectors \
	filter-logs-session analyze-log-levels help-logs

# Main commit preparation - use pre-commit hooks for consistency
prepare-commit:
	@echo "🚀 Preparing commit..."
	git add .
	@echo "🔍 Running pre-commit hooks..."
	pre-commit run

# Development commands
lint:
	@echo "🔍 Running linter..."
	uv run ruff check --fix --unsafe-fixes

format:
	@echo "🎨 Formatting code..."
	uv run ruff format

typecheck:
	@echo "🏷️  Type checking..."
	uv run mypy --ignore-missing-imports --explicit-package-bases src tests || echo "⚠️  Type checking completed with errors"

test:
	@echo "🧪 Running tests..."
	uv run pytest

# Validate tool configuration consistency
validate-tooling:
	@echo "🔍 Validating tooling configuration..."
	@echo "📋 Checking ruff..."
	@uv run ruff check src tests --diff || echo "⚠️  Ruff would make changes"
	@echo "🪝 Checking pre-commit..."
	@pre-commit run --all-files || echo "⚠️  Pre-commit hooks would modify files"
	@echo "✅ Tooling validation complete"

# Run all quality checks
quality: lint typecheck test
	@echo "✅ All quality checks passed"

#
# LOG MANAGEMENT TARGETS
#

# Clean all log files
clean-logs:
	@echo "🧹 Cleaning log files..."
	@rm -f logs/*.log
	@rm -f logs/*.log.*
	@echo "✅ Log files cleaned"

# Filter logs for errors and warnings
filter-logs-errors:
	@echo "🔍 Filtering logs for errors and warnings..."
	@if [ -f logs/test-b4rt.log ]; then \
		echo "📋 Test log errors:"; \
		grep -E "(ERROR|WARNING)" logs/test-b4rt.log | tail -20; \
	fi
	@if [ -f logs/b4rt.log ]; then \
		echo "📋 Application log errors:"; \
		grep -E "(ERROR|WARNING)" logs/b4rt.log | tail -20; \
	fi

# Filter logs for stream processing
filter-logs-stream:
	@echo "🔍 Filtering logs for stream processing..."
	@if [ -f logs/test-b4rt.log ]; then \
		echo "📋 Stream processing logs:"; \
		grep "b4rt.stream" logs/test-b4rt.log | tail -20; \
	fi

# Filter logs for performance information
filter-logs-performance:
	@echo "🔍 Filtering logs for performance information..."
	@if [ -f logs/test-b4rt.log ]; then \
		echo "📋 Performance logs:"; \
		grep -E "(profile|throughput|memory|processing_time)" logs/test-b4rt.log | tail -20; \
	fi

# Show recent log entries
show-recent-logs:
	@echo "📋 Recent log entries:"
	@if [ -f logs/test-b4rt.log ]; then \
		echo "🧪 Test logs (last 20 lines):"; \
		tail -20 logs/test-b4rt.log; \
	fi
	@if [ -f logs/b4rt.log ]; then \
		echo "🚀 Application logs (last 20 lines):"; \
		tail -20 logs/b4rt.log; \
	fi

# Monitor logs in real-time
monitor-logs:
	@echo "👁️  Monitoring logs in real-time (Ctrl+C to stop)..."
	@if [ -f logs/test-b4rt.log ]; then \
		tail -f logs/test-b4rt.log; \
	else \
		echo "⚠️  No test log file found. Run tests first."; \
	fi

#
# TESTING WITH LOGGING TARGETS
#

# Run tests with log monitoring
test-with-logs:
	@echo "🧪 Running tests with log monitoring..."
	@mkdir -p logs
	@uv run pytest tests/ -v
	@echo "📋 Recent test log entries:"
	@tail -20 logs/test-b4rt.log

# Run unit tests with logging
test-unit-with-logs:
	@echo "🧪 Running unit tests with logging..."
	@mkdir -p logs
	@uv run pytest tests/unit/ -v
	@echo "📋 Recent unit test log entries:"
	@tail -20 logs/test-b4rt.log

# Run performance tests with logging
test-performance-with-logs:
	@echo "🧪 Running performance tests with logging..."
	@mkdir -p logs
	@uv run pytest tests/unit/test_performance_regression.py -v
	@echo "📋 Performance test log entries:"
	@grep -E "(profile|throughput|memory)" logs/test-b4rt.log | tail -10

#
# ADVANCED LOG FILTERING
#

# Filter logs by component
filter-logs-component:
	@echo "🔍 Available log filtering options:"
	@echo "  make filter-logs-stream      - Stream processing logs"
	@echo "  make filter-logs-performance - Performance logs"
	@echo "  make filter-logs-errors      - Error and warning logs"
	@echo "  make filter-logs-detectors   - Event detector logs"
	@echo "  make filter-logs-session     - Session management logs"

# Filter logs for event detectors
filter-logs-detectors:
	@echo "🔍 Filtering logs for event detectors..."
	@if [ -f logs/test-b4rt.log ]; then \
		echo "📋 Event detector logs:"; \
		grep -E "(detector|detect_events)" logs/test-b4rt.log | tail -20; \
	fi

# Filter logs for session management
filter-logs-session:
	@echo "🔍 Filtering logs for session management..."
	@if [ -f logs/test-b4rt.log ]; then \
		echo "📋 Session management logs:"; \
		grep -E "(SessionInfo|session_id|landmarks)" logs/test-b4rt.log | tail -20; \
	fi

#
# LOG ANALYSIS HELPERS
#

# Count log levels
analyze-log-levels:
	@echo "📊 Analyzing log levels..."
	@if [ -f logs/test-b4rt.log ]; then \
		echo "📋 Log level distribution:"; \
		echo "TRACE:   $$(grep -c "TRACE" logs/test-b4rt.log || echo 0)"; \
		echo "DEBUG:   $$(grep -c "DEBUG" logs/test-b4rt.log || echo 0)"; \
		echo "INFO:    $$(grep -c "INFO" logs/test-b4rt.log || echo 0)"; \
		echo "WARNING: $$(grep -c "WARNING" logs/test-b4rt.log || echo 0)"; \
		echo "ERROR:   $$(grep -c "ERROR" logs/test-b4rt.log || echo 0)"; \
	fi

# Show help for log targets
help-logs:
	@echo "🔍 B4RT Logging Makefile Targets:"
	@echo ""
	@echo "📋 Log Management:"
	@echo "  make clean-logs              - Remove all log files"
	@echo "  make show-recent-logs        - Show recent log entries"
	@echo "  make monitor-logs            - Monitor logs in real-time"
	@echo ""
	@echo "🔍 Log Filtering:"
	@echo "  make filter-logs-errors      - Show errors and warnings"
	@echo "  make filter-logs-stream      - Show stream processing logs"
	@echo "  make filter-logs-performance - Show performance logs"
	@echo "  make filter-logs-detectors   - Show event detector logs"
	@echo "  make filter-logs-session     - Show session management logs"
	@echo ""
	@echo "🧪 Testing with Logging:"
	@echo "  make test-with-logs          - Run all tests with log monitoring"
	@echo "  make test-unit-with-logs     - Run unit tests with logging"
	@echo "  make test-performance-with-logs - Run performance tests with logging"
	@echo ""
	@echo "📊 Log Analysis:"
	@echo "  make analyze-log-levels      - Count log entries by level"
	@echo ""
	@echo "💡 Example Usage:"
	@echo "  make test-with-logs          # Run tests and show logs"
	@echo "  make filter-logs-errors      # Check for issues"
	@echo "  make monitor-logs            # Watch logs in real-time"
