#!/usr/bin/env python3
"""
Simple HTTP server for streaming viewer page
Run this on your mini PC to serve the index.html file
"""
import http.server
import socketserver
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PUBLIC_IP = os.getenv('PUBLIC_IP', 'YOUR_PUBLIC_IP')

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for WebRTC
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Stream viewer page running at:")
        print(f"   Local:  http://localhost:{PORT}")
        print(f"   Public: http://{PUBLIC_IP}:{PORT}")
        print(f"\n📺 Send this link to your friends:")
        print(f"   http://{PUBLIC_IP}:{PORT}")
        print(f"\nPress Ctrl+C to stop")
        httpd.serve_forever()
