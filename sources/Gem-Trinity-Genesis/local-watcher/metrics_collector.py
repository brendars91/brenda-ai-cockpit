"""
Metrics Collector v2.0 - Prometheus-style Metrics
Comprehensive metrics collection for Gem-Trinity Genesis monitoring.
"""
import time
import psutil
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"          # Incrementing value
    GAUGE = "gauge"            # Current value
    HISTOGRAM = "histogram"     # Distribution
    SUMMARY = "summary"         # Count, sum, min, max, avg, quantiles

@dataclass
class Metric:
    """A single metric data point"""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_prometheus(self) -> str:
        """Convert to Prometheus text format"""
        label_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        return f"{self.name}{{{label_str}}} {self.value}"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "labels": self.labels,
            "timestamp": self.timestamp
        }

class MetricsCollector:
    """
    Centralized metrics collector for Gem-Trinity Genesis.

    Features:
    - System metrics (CPU, memory, disk)
    - Application metrics (requests, errors, timings)
    - Custom metrics registration
    - Prometheus export format
    - Real-time metric callbacks
    - Thread-safe operations
    """

    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.lock = threading.Lock()

        # Callbacks for metric updates
        self.callbacks: List[Callable] = []

        # Start time
        self.start_time = time.time()

    def register_callback(self, callback: Callable[[Metric], None]):
        """
        Register a callback to be notified of new metrics.

        Args:
            callback: Function that receives Metric objects
        """
        self.callbacks.append(callback)

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Amount to increment (default 1.0)
            labels: Additional labels

        Returns:
            Metric ID reference
        """
        metric_id = f"cnt_{name}_{int(time.time() * 1000)}"

        metric = Metric(
            name=name,
            type=MetricType.COUNTER,
            value=value,
            labels=labels or {},
            timestamp=time.time()
        )

        self._add_metric(metric)
        return metric_id

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Set a gauge metric to a value.

        Args:
            name: Metric name
            value: Current value
            labels: Additional labels

        Returns:
            Metric ID reference
        """
        metric_id = f"gauge_{name}_{int(time.time() * 1000)}"

        metric = Metric(
            name=name,
            type=MetricType.GAUGE,
            value=value,
            labels=labels or {},
            timestamp=time.time()
        )

        self._add_metric(metric)
        return metric_id

    def record_timing(
        self,
        name: str,
        duration: float,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Record a timing value (in seconds).

        Args:
            name: Metric name
            duration: Duration in seconds
            labels: Additional labels

        Returns:
            Metric ID reference
        """
        metric_id = f"hist_{name}_{int(time.time() * 1000)}"

        metric = Metric(
            name=f"{name}_duration",
            type=MetricType.HISTOGRAM,
            value=duration,
            labels=labels or {},
            timestamp=time.time()
        )

        self._add_metric(metric)
        return metric_id

    def observe(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> str:
        """
        Observe a value for summary statistics.

        Args:
            name: Metric name
            value: Value to observe
            labels: Additional labels

        Returns:
            Metric ID reference
        """
        metric_id = f"sum_{name}_{int(time.time() * 1000)}"

        metric = Metric(
            name=name,
            type=MetricType.SUMMARY,
            value=value,
            labels=labels or {},
            timestamp=time.time()
        )

        self._add_metric(metric)
        return metric_id

    def _add_metric(self, metric: Metric):
        """Add metric and notify callbacks"""
        with self.lock:
            self.metrics[metric.name].append(metric)

        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(metric)
            except Exception as e:
                logger.error(f"[Metrics] Callback error: {e}")

    def get_metrics(self, name: Optional[str] = None) -> List[Metric]:
        """
        Get metrics by name or all metrics.

        Args:
            name: Optional metric name filter

        Returns:
            List of metrics
        """
        with self.lock:
            if name:
                return self.metrics.get(name, [])
            return [m for metrics in self.metrics.values() for m in metrics]

    def get_prometheus_export(self) -> str:
        """
        Get all metrics in Prometheus text format.

        Returns:
            Prometheus text format
        """
        with self.lock:
            lines = []

            for metric_name, metrics in self.metrics.items():
                for metric in metrics:
                    lines.append(metric.to_prometheus())

        return "\n".join(lines)

    def get_stats_summary(self) -> Dict[str, Any]:
        """
        Get statistics summary of all metrics.

        Returns:
            Dictionary with metric statistics
        """
        with self.lock:
            summary = {}

            for metric_name, metrics in self.metrics.items():
                if not metrics:
                    continue

                values = [m.value for m in metrics]

                summary[metric_name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "last": values[-1] if values else 0
                }

            # Add system info
            summary["uptime_seconds"] = time.time() - self.start_time
            summary["metric_count"] = len(self.metrics)

            return summary

    def clear_metrics(self, name: Optional[str] = None):
        """
        Clear metrics by name or all metrics.

        Args:
            name: Optional metric name to clear
        """
        with self.lock:
            if name:
                if name in self.metrics:
                    del self.metrics[name]
                    logger.info(f"[Metrics] Cleared metric: {name}")
            else:
                self.metrics.clear()
                logger.info("[Metrics] Cleared all metrics")

class SystemMetricsCollector:
    """
    System-level metrics collector.

    Collects:
    - CPU usage
    - Memory usage
    - Disk usage
    - Network I/O
    - Process count
    """

    def __init__(self):
        self.last_cpu = psutil.cpu_percent()
        self.last_memory = 0
        self.last_disk = 0

    def collect(self) -> Dict[str, Any]:
        """
        Collect current system metrics.

        Returns:
            Dictionary with system metrics
        """
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            memory_percent = (memory.used / memory.total) * 100

            # Disk
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024 ** 3)
            disk_percent = (disk.used / disk.total) * 100

            # Network
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent
            bytes_recv = net_io.bytes_recv

            # Load average
            load_avg = psutil.getloadavg()

            return {
                "cpu_percent": cpu_percent,
                "memory_mb": round(memory_mb, 2),
                "memory_percent": round(memory_percent, 2),
                "disk_used_gb": round(disk_used_gb, 2),
                "disk_percent": round(disk_percent, 2),
                "network_sent_mb": round(bytes_sent / (1024 * 1024), 2),
                "network_recv_mb": round(bytes_recv / (1024 * 1024), 2),
                "load_avg_1m": round(load_avg[0], 2),
                "load_avg_5m": round(load_avg[1], 2),
                "load_avg_15m": round(load_avg[2], 2),
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"[SystemMetrics] Failed to collect: {e}")
            return {}

class ApplicationMetricsCollector:
    """
    Application-level metrics collector.

    Collects:
    - Request counts
    - Error counts
    - Response times
    - Active connections
    """

    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector

    def track_request(
        self,
        endpoint: str,
        method: str = "GET",
        status: int = 200,
        duration: float = 0
    ):
        """Track an API request"""
        self.collector.increment(
            name="api_requests_total",
            value=1.0,
            labels={
                "endpoint": endpoint,
                "method": method,
                "status": str(status)
            }
        )

        # Track response time
        self.collector.record_timing(
            name="api_request_duration",
            duration=duration,
            labels={"endpoint": endpoint, "method": method}
        )

        # Track status code
        if status >= 400:
            self.collector.increment(
                name="api_errors_total",
                value=1.0,
                labels={"endpoint": endpoint, "status": str(status)}
            )

    def track_llm_call(
        self,
        provider: str,
        model: str,
        cached: bool = False,
        tokens: int = 0,
        duration: float = 0
    ):
        """Track an LLM API call"""
        self.collector.increment(
            name="llm_requests_total",
            value=1.0,
            labels={
                "provider": provider,
                "model": model,
                "cached": str(cached).lower()
            }
        )

        self.collector.observe(
            name="llm_tokens",
            value=tokens,
            labels={"provider": provider, "model": model}
        )

        self.collector.record_timing(
            name="llm_request_duration",
            duration=duration,
            labels={"provider": provider, "model": model}
        )

    def track_cache_hit(self, cache_type: str, hit: bool = True):
        """Track a cache hit or miss"""
        self.collector.increment(
            name="cache_requests_total",
            value=1.0,
            labels={"type": cache_type, "result": "hit" if hit else "miss"}
        )

    def track_workflow(
        self,
        stage: str,
        status: str,
        duration: float = 0
    ):
        """Track a workflow stage"""
        self.collector.increment(
            name="workflow_stages_total",
            value=1.0,
            labels={"stage": stage, "status": status}
        )

        self.collector.record_timing(
            name="workflow_stage_duration",
            duration=duration,
            labels={"stage": stage}
        )

# Singleton instances
_metrics_collector: Optional[MetricsCollector] = None
_system_collector: Optional[SystemMetricsCollector] = None
_app_collector: Optional[ApplicationMetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get singleton metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def get_system_collector() -> SystemMetricsCollector:
    """Get singleton system metrics collector instance"""
    global _system_collector
    if _system_collector is None:
        _system_collector = SystemMetricsCollector()
    return _system_collector

def get_app_collector() -> ApplicationMetricsCollector:
    """Get singleton application metrics collector instance"""
    global _app_collector
    if _app_collector is None:
        _metrics_collector = get_metrics_collector()
        _system_collector = get_system_collector()
        _app_collector = ApplicationMetricsCollector(_metrics_collector)
    return _app_collector
