from app.core.metrics import MetricsCollector


def test_metrics_collector_initial_state():
    m = MetricsCollector()
    metrics = m.get_metrics()
    assert metrics["requests_per_minute"] == 0
    assert metrics["active_users"] == 0
    assert metrics["errors"] == {}


def test_metrics_record_request():
    m = MetricsCollector()
    m.record_request("GET", "/health", 200, 5.0)
    metrics = m.get_metrics()
    assert metrics["requests_per_minute"] == 1
    assert metrics["status_code_distribution"]["200"] == 1


def test_metrics_record_user_activity():
    m = MetricsCollector()
    m.record_user_activity("user_1")
    m.record_user_activity("user_2")
    assert m.get_metrics()["active_users"] == 2


def test_metrics_record_ai_latency():
    m = MetricsCollector()
    m.record_ai_latency(150.0)
    m.record_ai_latency(250.0)
    metrics = m.get_metrics()
    assert metrics["ai_total_calls"] == 2
    assert metrics["ai_avg_latency_ms"] == 200.0


def test_metrics_record_errors():
    m = MetricsCollector()
    m.record_request("GET", "/error", 500, 10.0)
    m.record_request("GET", "/bad", 400, 3.0)
    metrics = m.get_metrics()
    assert metrics["errors"]["server_error"] == 1
    assert metrics["errors"]["client_error"] == 1


def test_metrics_prometheus_format():
    m = MetricsCollector()
    m.record_request("GET", "/test", 200, 5.0)
    m.record_user_activity("user_1")
    text = m.get_prometheus_text()
    assert text.startswith("# HELP")
    assert "pystreamflow_uptime_seconds" in text
    assert "pystreamflow_requests_per_minute" in text
    assert "pystreamflow_active_users" in text
