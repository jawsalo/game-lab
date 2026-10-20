"""Optional OpenTelemetry SDK setup for the Game Lab API."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

HEALTH_CHECK_URLS = r"/api/health/(live|ready)"


def signal_endpoint(environment: Mapping[str, str], signal: str) -> str | None:
    """Return a signal-specific OTLP endpoint or the shared OTLP endpoint."""
    signal_endpoint = environment.get(f"OTEL_EXPORTER_OTLP_{signal.upper()}_ENDPOINT")
    shared_endpoint = environment.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    return signal_endpoint or shared_endpoint or None


def configured_signal_endpoint(
    environment: Mapping[str, str],
    signal: str,
) -> str | None:
    """Return an OTLP endpoint only when that signal selects the OTLP exporter."""
    exporter = environment.get(f"OTEL_{signal.upper()}_EXPORTER", "otlp")
    if exporter.strip().lower() != "otlp":
        return None
    return signal_endpoint(environment, signal)


def resource_attributes(environment: Mapping[str, str]) -> dict[str, str]:
    """Build stable resource identity from application environment variables."""
    return {
        "service.name": environment.get("OTEL_SERVICE_NAME", "game-lab-api"),
        "service.version": environment.get("APP_VERSION", "dev"),
        "deployment.environment.name": environment.get("APP_ENV", "development"),
    }


def configure_telemetry(
    app: FastAPI,
    environment: Mapping[str, str] | None = None,
) -> tuple[TracerProvider | None, MeterProvider | None]:
    """Instrument HTTP and SQLite operations, exporting only when OTLP is configured.

    Endpoints use the OTLP/gRPC exporter convention. With no configured endpoint,
    FastAPI uses OpenTelemetry's no-op providers and makes no export attempts.
    """
    settings = os.environ if environment is None else environment
    if settings.get("OTEL_SDK_DISABLED", "").strip().lower() == "true":
        FastAPIInstrumentor.instrument_app(app, excluded_urls=HEALTH_CHECK_URLS)
        return None, None

    traces_endpoint = configured_signal_endpoint(settings, "traces")
    metrics_endpoint = configured_signal_endpoint(settings, "metrics")
    if not traces_endpoint and not metrics_endpoint:
        FastAPIInstrumentor.instrument_app(app, excluded_urls=HEALTH_CHECK_URLS)
        return None, None

    resource = Resource.create(resource_attributes(settings))
    tracer_provider: TracerProvider | None = None
    meter_provider: MeterProvider | None = None

    if traces_endpoint:
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=traces_endpoint))
        )
        trace.set_tracer_provider(tracer_provider)

    if metrics_endpoint:
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=metrics_endpoint)
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
        excluded_urls=HEALTH_CHECK_URLS,
    )
    if tracer_provider is not None:
        # This creates child spans for SQLite statements inside the HTTP request span.
        SQLite3Instrumentor().instrument(tracer_provider=tracer_provider)

    return tracer_provider, meter_provider


def shutdown_telemetry(
    providers: tuple[TracerProvider | None, MeterProvider | None],
) -> None:
    """Flush and close configured exporters during a graceful API shutdown."""
    tracer_provider, meter_provider = providers
    if meter_provider is not None:
        meter_provider.shutdown()
    if tracer_provider is not None:
        tracer_provider.shutdown()
