"""
Observability Module for Weather Outfit Agent

Provides logging, tracing, and metrics capabilities to understand and debug
the agent's internal operations.

Features:
- Structured logging with trace IDs
- Request tracing through the system
- Performance metrics collection
- Configurable log levels
"""

import logging
import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from collections import defaultdict
import threading


class TraceContext:
    """Thread-local storage for trace IDs."""
    _thread_local = threading.local()

    @classmethod
    def set_trace_id(cls, trace_id: str):
        """Set the current trace ID."""
        cls._thread_local.trace_id = trace_id

    @classmethod
    def get_trace_id(cls) -> Optional[str]:
        """Get the current trace ID."""
        return getattr(cls._thread_local, 'trace_id', None)

    @classmethod
    def clear_trace_id(cls):
        """Clear the current trace ID."""
        if hasattr(cls._thread_local, 'trace_id'):
            delattr(cls._thread_local, 'trace_id')


class TraceIDFilter(logging.Filter):
    """Logging filter to add trace IDs to log records."""

    def filter(self, record):
        """Add trace_id to the log record."""
        trace_id = TraceContext.get_trace_id()
        record.trace_id = trace_id if trace_id else 'no-trace'
        return True


class MetricsCollector:
    """Collects and stores metrics about agent operations."""

    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'api_calls': defaultdict(int),
            'agent_calls': defaultdict(int),
            'errors': defaultdict(int),
            'start_time': datetime.now().isoformat()
        }
        self.lock = threading.Lock()

    def record_request(self, success: bool, response_time: float):
        """Record a completed request."""
        with self.lock:
            self.metrics['total_requests'] += 1
            if success:
                self.metrics['successful_requests'] += 1
            else:
                self.metrics['failed_requests'] += 1
            self.metrics['response_times'].append(response_time)

    def record_api_call(self, api_name: str):
        """Record an API call."""
        with self.lock:
            self.metrics['api_calls'][api_name] += 1

    def record_agent_call(self, agent_name: str):
        """Record an agent execution."""
        with self.lock:
            self.metrics['agent_calls'][agent_name] += 1

    def record_error(self, error_type: str):
        """Record an error occurrence."""
        with self.lock:
            self.metrics['errors'][error_type] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        with self.lock:
            response_times = self.metrics['response_times']

            return {
                'total_requests': self.metrics['total_requests'],
                'successful_requests': self.metrics['successful_requests'],
                'failed_requests': self.metrics['failed_requests'],
                'success_rate': (
                    self.metrics['successful_requests'] / self.metrics['total_requests'] * 100
                    if self.metrics['total_requests'] > 0 else 0
                ),
                'response_times': {
                    'count': len(response_times),
                    'average': sum(response_times) / len(response_times) if response_times else 0,
                    'min': min(response_times) if response_times else 0,
                    'max': max(response_times) if response_times else 0
                },
                'api_calls': dict(self.metrics['api_calls']),
                'agent_calls': dict(self.metrics['agent_calls']),
                'errors': dict(self.metrics['errors']),
                'uptime_since': self.metrics['start_time']
            }

    def format_metrics(self) -> str:
        """Format metrics for display."""
        metrics = self.get_metrics()

        lines = [
            "=" * 60,
            "AGENT METRICS",
            "=" * 60,
            f"Total Requests:       {metrics['total_requests']}",
            f"Success Rate:         {metrics['success_rate']:.1f}% ({metrics['successful_requests']}/{metrics['total_requests']})",
            f"Failed Requests:      {metrics['failed_requests']}",
            "",
            "Response Times:",
            f"  Average:            {metrics['response_times']['average']:.2f}s",
            f"  Min:                {metrics['response_times']['min']:.2f}s",
            f"  Max:                {metrics['response_times']['max']:.2f}s",
            "",
            "API Calls:",
        ]

        for api_name, count in metrics['api_calls'].items():
            lines.append(f"  {api_name:20} {count}")

        lines.append("")
        lines.append("Agent Executions:")
        for agent_name, count in metrics['agent_calls'].items():
            lines.append(f"  {agent_name:20} {count}")

        if metrics['errors']:
            lines.append("")
            lines.append("Errors:")
            for error_type, count in metrics['errors'].items():
                lines.append(f"  {error_type:20} {count}")

        lines.append("")
        lines.append(f"Uptime Since:         {metrics['uptime_since']}")
        lines.append("=" * 60)

        return "\n".join(lines)

    def reset(self):
        """Reset all metrics."""
        with self.lock:
            self.metrics = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'api_calls': defaultdict(int),
                'agent_calls': defaultdict(int),
                'errors': defaultdict(int),
                'start_time': datetime.now().isoformat()
            }


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics_collector


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup structured logging with trace ID support.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('weather_outfit_agent')
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Create formatter with trace ID
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(trace_id)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    console_handler.addFilter(TraceIDFilter())
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always DEBUG for file
        file_handler.setFormatter(formatter)
        file_handler.addFilter(TraceIDFilter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Optional logger name (uses default if not provided)

    Returns:
        Logger instance
    """
    logger_name = f'weather_outfit_agent.{name}' if name else 'weather_outfit_agent'
    return logging.getLogger(logger_name)


@contextmanager
def trace_request(operation: str, **metadata):
    """
    Context manager for tracing a request through the system.

    Usage:
        with trace_request("morning_recommendation", location="Manila"):
            # Your code here
            result = process_recommendation()

    Args:
        operation: Name of the operation being traced
        **metadata: Additional metadata to log
    """
    # Generate trace ID
    trace_id = str(uuid.uuid4())[:8]
    TraceContext.set_trace_id(trace_id)

    logger = get_logger()
    start_time = time.time()

    # Log request start
    metadata_str = ", ".join(f"{k}={v}" for k, v in metadata.items())
    logger.info(f"→ START {operation} | {metadata_str}")

    success = False
    try:
        yield trace_id
        success = True
        logger.info(f"✓ SUCCESS {operation} | Duration: {time.time() - start_time:.2f}s")
    except Exception as e:
        logger.error(f"✗ FAILED {operation} | Error: {str(e)} | Duration: {time.time() - start_time:.2f}s")
        get_metrics_collector().record_error(type(e).__name__)
        raise
    finally:
        # Record metrics
        response_time = time.time() - start_time
        get_metrics_collector().record_request(success, response_time)

        # Clear trace context
        TraceContext.clear_trace_id()


@contextmanager
def trace_component(component_name: str, **metadata):
    """
    Context manager for tracing a component execution within a request.

    Usage:
        with trace_component("WeatherAgent", location="Manila"):
            weather_data = fetch_weather()

    Args:
        component_name: Name of the component being traced
        **metadata: Additional metadata to log
    """
    logger = get_logger()
    start_time = time.time()

    metadata_str = ", ".join(f"{k}={v}" for k, v in metadata.items())
    logger.info(f"  → {component_name} | {metadata_str}")

    try:
        yield
        duration = time.time() - start_time
        logger.debug(f"  ✓ {component_name} completed | Duration: {duration:.2f}s")

        # Record agent execution
        get_metrics_collector().record_agent_call(component_name)
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"  ✗ {component_name} failed | Error: {str(e)} | Duration: {duration:.2f}s")
        raise


def log_api_call(api_name: str, endpoint: str, params: Dict[str, Any] = None):
    """
    Log an API call.

    Args:
        api_name: Name of the API (e.g., "OpenWeather", "Google Calendar")
        endpoint: API endpoint being called
        params: Optional parameters being sent
    """
    logger = get_logger()

    # Mask sensitive data in params
    safe_params = _mask_sensitive_data(params) if params else {}

    logger.debug(f"  API Call: {api_name} → {endpoint} | Params: {safe_params}")

    # Record metric
    get_metrics_collector().record_api_call(api_name)


def log_decision(decision: str, reasoning: str, data: Dict[str, Any] = None):
    """
    Log an agent decision point.

    Args:
        decision: The decision being made
        reasoning: Why this decision was made
        data: Optional supporting data
    """
    logger = get_logger()

    logger.info(f"  DECISION: {decision}")
    logger.debug(f"    Reasoning: {reasoning}")

    if data:
        logger.debug(f"    Data: {json.dumps(data, indent=2)}")


def log_data_flow(source: str, destination: str, data_type: str, summary: str = ""):
    """
    Log data flowing between components.

    Args:
        source: Where the data is coming from
        destination: Where the data is going to
        data_type: Type of data being passed
        summary: Optional summary of the data
    """
    logger = get_logger()

    message = f"  DATA FLOW: {source} → {destination} | Type: {data_type}"
    if summary:
        message += f" | {summary}"

    logger.debug(message)


def _mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data like API keys in logs."""
    sensitive_keys = {'api_key', 'apikey', 'token', 'password', 'secret'}

    masked_data = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            masked_data[key] = "***MASKED***"
        else:
            masked_data[key] = value

    return masked_data


def display_metrics():
    """Display current metrics to console."""
    print(get_metrics_collector().format_metrics())


def reset_metrics():
    """Reset all metrics."""
    get_metrics_collector().reset()
    get_logger().info("Metrics have been reset")
