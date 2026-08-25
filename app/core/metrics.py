import time
from collections import defaultdict
from threading import Lock

import structlog

logger = structlog.get_logger()


class MetricsCollector:
    def __init__(self):
        self._lock = Lock()
        self._requests: list[float] = []
        self._errors: dict[str, int] = defaultdict(int)
        self._endpoint_hits: dict[str, int] = defaultdict(int)
        self._status_codes: dict[int, int] = defaultdict(int)
        self._active_users: set[str] = set()
        self._ai_latencies: list[float] = []
        self._start_time = time.time()

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        with self._lock:
            self._requests.append(time.time())
            endpoint = f"{method} {path}"
            self._endpoint_hits[endpoint] += 1
            self._status_codes[status_code] += 1

            if status_code >= 500:
                self._errors["server_error"] += 1
            elif status_code >= 400:
                self._errors["client_error"] += 1

    def record_user_activity(self, user_id: str):
        with self._lock:
            self._active_users.add(user_id)

    def record_ai_latency(self, duration_ms: float):
        with self._lock:
            self._ai_latencies.append(duration_ms)
            if len(self._ai_latencies) > 1000:
                self._ai_latencies = self._ai_latencies[-500:]

    def _cleanup_old_requests(self):
        cutoff = time.time() - 60
        self._requests = [t for t in self._requests if t > cutoff]

    def get_metrics(self) -> dict:
        with self._lock:
            self._cleanup_old_requests()
            uptime = time.time() - self._start_time

            avg_ai_latency = 0
            if self._ai_latencies:
                avg_ai_latency = sum(self._ai_latencies) / len(self._ai_latencies)

            return {
                "uptime_seconds": round(uptime, 2),
                "requests_per_minute": len(self._requests),
                "total_endpoint_hits": dict(self._endpoint_hits),
                "status_code_distribution": {
                    str(k): v for k, v in sorted(self._status_codes.items())
                },
                "errors": dict(self._errors),
                "active_users": len(self._active_users),
                "ai_avg_latency_ms": round(avg_ai_latency, 2),
                "ai_total_calls": len(self._ai_latencies),
            }

    def get_prometheus_text(self) -> str:
        metrics = self.get_metrics()
        lines = [
            "# HELP pystreamflow_uptime_seconds Uptime in seconds",
            f"pystreamflow_uptime_seconds {metrics['uptime_seconds']}",
            "# HELP pystreamflow_requests_per_minute Requests in the last minute",
            f"pystreamflow_requests_per_minute {metrics['requests_per_minute']}",
            "# HELP pystreamflow_active_users Current active users",
            f"pystreamflow_active_users {metrics['active_users']}",
            "# HELP pystreamflow_ai_avg_latency_ms Average AI response latency",
            f"pystreamflow_ai_avg_latency_ms {metrics['ai_avg_latency_ms']}",
            "# HELP pystreamflow_ai_total_calls Total AI calls",
            f"pystreamflow_ai_total_calls {metrics['ai_total_calls']}",
        ]
        for code, count in metrics["status_code_distribution"].items():
            lines.append(f'pystreamflow_http_requests_total{{status="{code}"}} {count}')
        for error_type, count in metrics["errors"].items():
            lines.append(f'pystreamflow_errors_total{{type="{error_type}"}} {count}')
        return "\n".join(lines)


metrics_collector = MetricsCollector()
