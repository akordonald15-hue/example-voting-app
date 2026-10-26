import time
from flask import g, request
from prometheus_client import Counter, Histogram
from opentelemetry import trace, propagate
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def configure(app):
    provider = TracerProvider(resource=Resource.create({'service.name': 'payment'}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer('robot-shop-payment')
    count = Counter('http_server_requests_total', 'Completed HTTP responses', ['service','status'])
    latency = Histogram('http_server_request_duration_seconds', 'HTTP response latency', ['service'])
    @app.before_request
    def begin():
        if request.path == '/metrics': return
        g.started = time.monotonic()
        g.span = tracer.start_span(request.method + ' ' + str(request.url_rule or 'unmatched'), context=propagate.extract(request.headers), kind=trace.SpanKind.SERVER)
        g.span.set_attribute('http.request.method',request.method)
    @app.after_request
    def finish(response):
        if hasattr(g,'started'):
            count.labels('payment',str(response.status_code)).inc()
            latency.labels('payment').observe(time.monotonic()-g.started)
            g.span.set_attribute('http.response.status_code',response.status_code)
            if response.status_code >= 500: g.span.set_status(trace.Status(trace.StatusCode.ERROR))
            g.span.end()
            app.logger.info('service=payment level=info status=%s',response.status_code)
        return response
