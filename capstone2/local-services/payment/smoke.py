import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
received = []
class Capture(BaseHTTPRequestHandler):
    def do_POST(self):
        received.append((self.path,self.rfile.read(int(self.headers['Content-Length']))))
        self.send_response(200)
        self.end_headers()
    def log_message(self,*args): pass
server = HTTPServer(('127.0.0.1',4318),Capture)
threading.Thread(target=server.serve_forever,daemon=True).start()
import payment
client = payment.app.test_client()
assert client.get('/health').status_code == 200
assert client.get('/metrics').status_code == 200
body = client.get('/metrics').data.decode()
assert 'http_server_requests_total{service="payment",status="200"}' in body
assert 'http_server_request_duration_seconds_bucket' in body
assert payment.countItems([{'sku':'one','qty':2},{'sku':'SHIP','qty':1}]) == 2
from opentelemetry import trace
assert trace.get_tracer_provider().force_flush(timeout_millis=5000)
assert received and received[0][0] == '/v1/traces' and received[0][1]
server.shutdown()
print('PAYMENT_HEALTH_RED_BUSINESS_UNIT_OTLP_EXPORT_PASS')
