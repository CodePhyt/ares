"""
Metrics and monitoring for ARES API.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from loguru import logger
import time


class MetricsCollector:
    """Collect and track API metrics."""

    def __init__(self, max_history: int = 1000):
        """
        Initialize metrics collector.

        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.request_times: deque = deque(maxlen=max_history)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.query_times: deque = deque(maxlen=max_history)
        self.upload_times: deque = deque(maxlen=max_history)
        self.start_time = datetime.now()

    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record a request metric."""
        self.request_times.append(duration)
        self.request_counts[endpoint] += 1
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1

    def record_query(self, duration: float):
        """Record a query operation."""
        self.query_times.append(duration)

    def record_upload(self, duration: float):
        """Record an upload operation."""
        self.upload_times.append(duration)

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        
        stats = {
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 0.0,
            "requests_per_endpoint": dict(self.request_counts),
            "errors_per_endpoint": dict(self.error_counts),
        }
        
        # Request timing statistics
        if self.request_times:
            request_times_list = list(self.request_times)
            stats["request_timing"] = {
                "avg_ms": sum(request_times_list) / len(request_times_list) * 1000,
                "min_ms": min(request_times_list) * 1000,
                "max_ms": max(request_times_list) * 1000,
                "p95_ms": self._percentile(request_times_list, 0.95) * 1000,
                "p99_ms": self._percentile(request_times_list, 0.99) * 1000,
            }
        
        # Query timing statistics
        if self.query_times:
            query_times_list = list(self.query_times)
            stats["query_timing"] = {
                "avg_ms": sum(query_times_list) / len(query_times_list) * 1000,
                "min_ms": min(query_times_list) * 1000,
                "max_ms": max(query_times_list) * 1000,
                "p95_ms": self._percentile(query_times_list, 0.95) * 1000,
            }
        
        # Upload timing statistics
        if self.upload_times:
            upload_times_list = list(self.upload_times)
            stats["upload_timing"] = {
                "avg_ms": sum(upload_times_list) / len(upload_times_list) * 1000,
                "min_ms": min(upload_times_list) * 1000,
                "max_ms": max(upload_times_list) * 1000,
            }
        
        return stats

    @staticmethod
    def _percentile(data: list, percentile: float) -> float:
        """Calculate percentile of a list."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def reset(self):
        """Reset all metrics."""
        self.request_times.clear()
        self.request_counts.clear()
        self.error_counts.clear()
        self.query_times.clear()
        self.upload_times.clear()
        self.start_time = datetime.now()
        logger.info("Metrics reset")


# Global metrics collector instance
metrics_collector = MetricsCollector()
