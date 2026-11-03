from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  if self.path.split('?')[0]=='/config.js':
   b=b'/* isolated workbench: fixture supplies the recorded worlds */';self.send_response(200);self.send_header('Content-Type','application/javascript');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  else:super().do_GET()
ThreadingHTTPServer(('127.0.0.1',6987),partial(Handler,directory='/Volumes/Data/Projects/Universe69/web')).serve_forever()
