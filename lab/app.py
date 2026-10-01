"""Synthetic local-only app with deliberate defects; NEVER deploy as a service."""
from copy import deepcopy
import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from urllib.parse import parse_qs, urlsplit

SEED = [
    {'id': 'P001', 'title': 'Manutenção de iluminação', 'category': 'infraestrutura', 'status': 'aberto'},
    {'id': 'P002', 'title': 'Aquisição de mobiliário', 'category': 'compras', 'status': 'aberto'},
    {'id': 'P003', 'title': 'Manutenção de rede', 'category': 'infraestrutura', 'status': 'fechado'},
]


def make_server(version):
    if version not in ('broken', 'fixed'):
        raise ValueError('Versão inválida')
    records, events = deepcopy(SEED), []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, code, data, content_type='application/json'):
            body = (json.dumps(data, ensure_ascii=False) if content_type == 'application/json' else data).encode()
            self.send_response(code)
            self.send_header('Content-Type', content_type + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parsed = urlsplit(self.path)
            category = parse_qs(parsed.query).get('category', [None])[0]
            filtered = [r for r in records if category is None or r['category'] == category]
            if parsed.path == '/records':
                return self.respond(200, filtered)
            if parsed.path == '/export.csv':
                stream = io.StringIO(newline='')
                writer = csv.DictWriter(stream, fieldnames=list(SEED[0]))
                writer.writeheader()
                writer.writerows(records if version == 'broken' else filtered)
                return self.respond(200, stream.getvalue(), 'text/csv')
            if parsed.path == '/audit':
                return self.respond(200, events)
            return self.respond(404, {'error': 'not_found'})

        def do_PATCH(self):
            if self.path != '/records/P001':
                return self.respond(404, {'error': 'not_found'})
            role = self.headers.get('X-Synthetic-Role', '')
            if version == 'fixed' and role != 'editor':
                return self.respond(403, {'error': 'forbidden'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length < 2048:
                    raise ValueError()
                value = json.loads(self.rfile.read(length))
                if set(value) != {'title'} or not isinstance(value['title'], str) or len(value['title']) > 200:
                    raise ValueError()
            except (ValueError, TypeError):
                return self.respond(400, {'error': 'invalid'})
            records[0]['title'] = value['title']
            if version == 'fixed':
                events.append({'entity_id': 'P001', 'action': 'update', 'actor': role})
            return self.respond(200, records[0])

    return ThreadingHTTPServer(('127.0.0.1', 0), Handler)
