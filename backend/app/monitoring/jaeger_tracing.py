try:
    from jaeger_client import Config
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    tracer = trace.get_tracer(__name__)
except ImportError:
    tracer = None

from fastapi import Request

async def add_tracing(request: Request, call_next):
    if tracer:
        with tracer.start_as_current_span(request.url.path):
            response = await call_next(request)
        return response
    return await call_next(request)
