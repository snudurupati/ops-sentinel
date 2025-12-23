from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.langchain import LangchainInstrumentor
from opentelemetry.sdk.resources import Resource

def setup_telemetry():
    """
    Initializes OpenTelemetry to send traces to Jarger.
    """
    # 1. Define the Service Resource (Who Am I?)
    resource = Resource.create({
        "service.name": "aether-v2-agent",
        "service.version": "2.0.0",
    })
        
    # 2. Initialize the Tracer Provider with the Resource
    provider = TracerProvider(resource=resource)
    
    # 3. Configure the Explorer (Where to send data?)
    # It defaults to localhost:4317, or reads OTEL_EXPORTER_OLTP_ENDPOINT env var
    oltp_exporter = OTLPSpanExporter(insecure=True)

    # 4. Add the Explorer to the Tracer Provider
    provider.add_span_processor(BatchSpanProcessor(oltp_exporter))

    # 5. Set the Tracer Provider as the global provider
    trace.set_tracer_provider(provider)

    # 6. AUTO-Instrument LangChain
    # This automatically traces every Chain, Tool, and LLM call!
    LangchainInstrumentor().instrument(tracer_provider=provider)

    print("🔭 OpenTelemetry initialized. Tracing to Jaeger.")
    
    