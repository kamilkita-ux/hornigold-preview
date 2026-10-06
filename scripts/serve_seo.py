"""Loopback-only artifact QA, never a production server."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import argparse,json
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['preview','production-ready'],required=True);p.add_argument('--port',type=int,required=True);a=p.parse_args()
root=R/('_site' if a.mode=='preview' else '_production_ready');release=json.loads((root/'release.json').read_text());base=release['base']
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
    def translate_path(self,path):
        u=urlsplit(path)
        if not u.path.startswith(base):return str(root/'__qa_not_found__')
        return super().translate_path('/'+u.path[len(base):])
    def end_headers(self):
        if a.mode=='preview':self.send_header('X-Robots-Tag','noindex, nofollow, noarchive')
        self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
    def log_message(self,*args):pass
print('Local QA: http://127.0.0.1:'+str(a.port)+base,flush=True)
class QAServer(ThreadingHTTPServer):
    request_queue_size=128
QAServer(('127.0.0.1',a.port),Handler).serve_forever()
