import os
import requests
import json
import sys

def main():
    # Parámetros de entrada
    k6_result_path = sys.argv[1] if len(sys.argv) > 1 else 'k6_result.json'
    slack_token = os.environ.get('SLACK_BOT_TOKEN')
    slack_channel = os.environ.get('REPORT_CANAL_ID')

    if not slack_token or not slack_channel:
        print('Faltan variables de entorno SLACK_BOT_TOKEN o REPORT_CANAL_ID')
        sys.exit(1)

    # Leer resultados de k6
    try:
        with open(k6_result_path, 'r', encoding='utf-8') as f:
            k6_data = json.load(f)
    except Exception as e:
        print(f'Error leyendo el archivo de resultados de k6: {e}')
        sys.exit(1)

    # Extraer métricas principales
    metrics = k6_data.get('metrics', {})
    duration = k6_data.get('state', {}).get('testRunDurationMs', 0) / 1000
    vus = k6_data.get('options', {}).get('vus', 'N/A')
    http_req_duration = metrics.get('http_req_duration', {})
    http_req_failed = metrics.get('http_req_failed', {})
    checks = metrics.get('checks', {})

    # Formatear mensaje
    mensaje = (
        f'*Reporte de prueba de carga k6*\n'
        f'- Duración: {duration:.1f} segundos\n'
        f'- VUs: {vus}\n'
        f'- Total requests: {metrics.get('http_reqs', {}).get('count', 'N/A')}\n'
        f'- 95% req < {http_req_duration.get('thresholds', {}).get('p(95)', 'N/A')} ms\n'
        f'- % requests fallidas: {http_req_failed.get('rate', 'N/A')*100:.2f}%\n'
        f'- Checks pasados: {checks.get('passes', 'N/A')} / {checks.get('passes', 0) + checks.get('fails', 0)}\n'
    )

    # Enviar mensaje a Slack
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {slack_token}',
        'Content-type': 'application/json; charset=utf-8'
    }
    data = {
        'channel': slack_channel,
        'text': mensaje
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200 or not response.json().get('ok'):
        print(f'Error enviando mensaje a Slack: {response.text}')
        sys.exit(1)
    print('Reporte de k6 enviado a Slack correctamente.')

if __name__ == '__main__':
    main()
