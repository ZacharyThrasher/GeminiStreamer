from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(('0.0.0.0', port), CORSHTTPRequestHandler)
    print(f'Server running on http://0.0.0.0:{port}')
    print(f'Local: http://localhost:{port}')
    print(f'Network: http://104.6.177.38:{port}')
    server.serve_forever()
