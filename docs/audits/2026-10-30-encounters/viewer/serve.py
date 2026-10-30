from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
class Local(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory='/Volumes/Data/Projects/Universe69/web',**kw)
 def do_GET(self):
  if self.path.split('?')[0]=='/config.js':
   body=b'// local mode\n';self.send_response(200);self.send_header('Content-Type','text/javascript');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  else:super().do_GET()
ThreadingHTTPServer(('127.0.0.1',6975),Local).serve_forever()
