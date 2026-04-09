import http.server
import socketserver
import argparse
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Range')
        self.send_header('Access-Control-Expose-Headers', 'Content-Length, Content-Range')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        start_time = time.time()
        # The base SimpleHTTPRequestHandler will handle the file serving and Range requests natively,
        # but Python 3.8+ handles Range requests automatically in SimpleHTTPRequestHandler?
        # Actually Python's built-in doesn't fully support 206 Partial Content out of the box until Python 3.8+? Wait, no, SimpleHTTPRequestHandler doesn't support Byte ranges properly. 
        # But DASH uses small .m4s segment files natively! It doesn't use byte ranges on a large file. So default GET is perfectly fine.
        super().do_GET()
        elapsed = time.time() - start_time
        logging.info(f"Served {self.path} in {elapsed:.4f}s")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CORS enabled static server for dash segments')
    parser.add_argument('--port', type=int, default=8001, help='Port to run on')
    parser.add_argument('--dir', type=str, default='.', help='Directory to serve')
    args = parser.parse_args()

    import os
    os.chdir(args.dir)

    # Use ThreadingTCPServer to avoid blocking on single connections
    class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True

    server_address = ("", args.port)
    with ThreadedHTTPServer(server_address, CORSRequestHandler) as httpd:
        print(f"Serving {args.dir} at port {args.port} with CORS enabled")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
