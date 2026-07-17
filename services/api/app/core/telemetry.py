"""
OpenTelemetry setup — traces every request and pipeline hop to Jaeger.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.core.config import settings


def setup_telemetry(app) -> None:
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=settings.OTEL_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)


# Module-level tracer — import and use in any service
tracer = trace.get_tracer("voice-assistant")
