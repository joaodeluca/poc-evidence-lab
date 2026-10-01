#!/usr/bin/env python3
"""Execute a bounded POC rehearsal against the OWN synthetic app only."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import http.client
import io
import json
from pathlib import Path
import threading
from app import make_server

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def execute(version):
    server = make_server(version)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    observations, results = [], []

    def request(path, method='GET', body=None, role='viewer'):
        connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
        encoded = json.dumps(body).encode() if body is not None else None
        try:
            connection.request(method, path, body=encoded, headers={'Content-Type': 'application/json', 'X-Synthetic-Role': role})
            response = connection.getresponse()
            raw = response.read(65537)
            if len(raw) > 65536:
                raise ValueError('Resposta excede limite')
            observed = {'id': f'{version}-http-{len(observations)+1:02}',
                        'at': datetime.now(timezone.utc).isoformat(),
                        'request': {'method': method, 'path': path, 'synthetic_role': role, 'body': body},
                        'response': {'status': response.status, 'content_type': response.getheader('Content-Type'),
                                     'body': raw.decode(), 'sha256': digest(raw)}}
            observations.append(observed)
            return observed
        finally:
            connection.close()

    def result(identifier, passed, ids, detail):
        results.append({'check_id': identifier, 'status': 'passed' if passed else 'failed',
                        'observation_ids': ids, 'detail': detail,
                        'claim_scope': 'Critério local do benchmark, não conformidade integral de requisito público.'})

    try:
        queried = request('/records?category=infraestrutura')
        exported = request('/export.csv?category=infraestrutura')
        expected = sorted(row['id'] for row in json.loads(queried['response']['body']))
        actual = sorted(row['id'] for row in csv.DictReader(io.StringIO(exported['response']['body'])))
        result('BENCH-EXPORT', queried['response']['status'] == exported['response']['status'] == 200 and expected == actual,
               [queried['id'], exported['id']], {'query_ids': expected, 'csv_ids': actual})
        before = request('/records')
        denied = request('/records/P001', 'PATCH', {'title': 'Mudança que deveria ser proibida'})
        after = request('/records')
        result('BENCH-PERMISSION', denied['response']['status'] == 403 and before['response']['body'] == after['response']['body'],
               [before['id'], denied['id'], after['id']], {'attempt_status': denied['response']['status'],
               'state_preserved': before['response']['body'] == after['response']['body']})
        changed = request('/records/P001', 'PATCH', {'title': 'Mudança autorizada de demonstração'}, 'editor')
        audit = request('/audit')
        events = json.loads(audit['response']['body'])
        wanted = {'entity_id': 'P001', 'action': 'update', 'actor': 'editor'}
        result('BENCH-AUDIT', changed['response']['status'] == 200 and wanted in events,
               [changed['id'], audit['id']], {'expected_event': wanted, 'events_observed': events})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    return {'version': version, 'checks': results, 'http_observations': observations}


def run(output):
    if output.exists():
        raise ValueError('Preserve evidência existente; escolha novo arquivo.')
    payload = {
        'classification': 'SYNTHETIC_APP_ACTUALLY_EXECUTED',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'Aplicação própria isolada, dados e falhas deliberados; não software de cliente.',
        'artifacts': {name: digest((HERE / name).read_bytes()) for name in ('PLAN.md', 'app.py', 'run.py')},
        'runs': [execute('broken'), execute('fixed')],
        'not_verified': ['Certificações, hospedagem, SLA, legislação e adequação integral de qualquer edital.',
                         'Software desconhecido, extração automática de todo edital e testes de navegador.',
                         'Authenticação de produção: o papel via cabeçalho é apenas simulação local.'],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        value = run(args.output)
    except (OSError, ValueError, http.client.HTTPException) as error:
        parser.exit(2, f'Execução incompleta: {error}\n')
    for item in value['runs']:
        print(item['version'], {check['check_id']: check['status'] for check in item['checks']})
