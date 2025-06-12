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

    # Extraer métricas principales de forma robusta
    metrics = k6_data.get('metrics', {})
    http_reqs = metrics.get('http_reqs', {}).get('count', 'N/A')
    http_req_duration = metrics.get('http_req_duration', {})
    p95 = http_req_duration.get('p(95)', 'N/A')
    avg = http_req_duration.get('avg', 'N/A')
    min_ = http_req_duration.get('min', 'N/A')
    max_ = http_req_duration.get('max', 'N/A')
    http_req_failed = metrics.get('http_req_failed', {})
    rate_value = http_req_failed.get('rate', 'N/A')
    try:
        rate_percent = f"{float(rate_value)*100:.2f}%"
    except (ValueError, TypeError):
        rate_percent = str(rate_value)
    checks = metrics.get('checks', {})
    checks_passed = checks.get('passes', 'N/A')
    checks_failed = checks.get('fails', 'N/A')
    total_checks = (checks.get('passes', 0) or 0) + (checks.get('fails', 0) or 0)

    # Información de escenarios
    escenarios = k6_data.get('options', {}).get('scenarios', {})
    escenarios_info = []
    for nombre, esc in escenarios.items():
        tipo = esc.get('executor', 'N/A')
        vus = esc.get('vus', esc.get('target', 'N/A'))
        duracion = esc.get('duration', esc.get('stages', 'N/A'))
        escenarios_info.append(f"- {nombre}: tipo={tipo}, vus={vus}, duración={duracion}")
    escenarios_str = '\n'.join(escenarios_info)

    # Formatear mensaje mejorado
    mensaje = (
        f'*Reporte de prueba de carga k6*\n'
        f'{escenarios_str}\n'
        f'- Total de requests: {http_reqs}\n'
        f'- Latencia promedio: {avg} ms\n'
        f'- Latencia p95: {p95} ms\n'
        f'- Latencia mínima: {min_} ms\n'
        f'- Latencia máxima: {max_} ms\n'
        f'- % requests fallidas: {rate_percent}\n'
        f'- Checks pasados: {checks_passed} / {total_checks}\n'
        f'- Checks fallidos: {checks_failed}\n'
    )

    # --- Agrupar métricas por dominio si hay más de un sitio ---
    # Detectar si se probaron varios dominios
    dominios = set()
    http_req_url = metrics.get('http_req_url', {})
    if 'values' in http_req_url:
        for url in http_req_url['values']:
            dominios.add(url)
    else:
        # fallback: solo un dominio
        dominios = set([None])

    reportes = []
    if len(dominios) > 1:
        for dominio in dominios:
            # Filtrar métricas por dominio
            dominio_metrics = {}
            for k, v in metrics.items():
                if isinstance(v, dict) and 'values' in v and dominio in v['values']:
                    dominio_metrics[k] = {kk: vv for kk, vv in v.items() if kk != 'values'}
                    for stat, val in v['values'][dominio].items():
                        dominio_metrics[k][stat] = val
                else:
                    dominio_metrics[k] = v
            # Generar reporte para este dominio
            http_reqs = dominio_metrics.get('http_reqs', {}).get('count', 'N/A')
            http_req_duration = dominio_metrics.get('http_req_duration', {})
            p95 = http_req_duration.get('p(95)', 'N/A')
            avg = http_req_duration.get('avg', 'N/A')
            min_ = http_req_duration.get('min', 'N/A')
            max_ = http_req_duration.get('max', 'N/A')
            http_req_failed = dominio_metrics.get('http_req_failed', {})
            rate_value = http_req_failed.get('rate', 'N/A')
            try:
                rate_percent = f"{float(rate_value)*100:.2f}%"
            except (ValueError, TypeError):
                rate_percent = str(rate_value)
            checks = dominio_metrics.get('checks', {})
            checks_passed = checks.get('passes', 'N/A')
            checks_failed = checks.get('fails', 'N/A')
            total_checks = (checks.get('passes', 0) or 0) + (checks.get('fails', 0) or 0)
            escenarios = k6_data.get('options', {}).get('scenarios', {})
            escenarios_info = []
            for nombre, esc in escenarios.items():
                tipo = esc.get('executor', 'N/A')
                vus = esc.get('vus', esc.get('target', 'N/A'))
                duracion = esc.get('duration', esc.get('stages', 'N/A'))
                escenarios_info.append(f"- {nombre}: tipo={tipo}, vus={vus}, duración={duracion}")
            escenarios_str = '\n'.join(escenarios_info)
            reportes.append(
                f'*Reporte de prueba de carga k6 para {dominio}*\n'
                f'{escenarios_str}\n'
                f'- Total de requests: {http_reqs}\n'
                f'- Latencia promedio: {avg} ms\n'
                f'- Latencia p95: {p95} ms\n'
                f'- Latencia mínima: {min_} ms\n'
                f'- Latencia máxima: {max_} ms\n'
                f'- % requests fallidas: {rate_percent}\n'
                f'- Checks pasados: {checks_passed} / {total_checks}\n'
                f'- Checks fallidos: {checks_failed}\n'
            )
    else:
        reportes.append(mensaje)

    # Enviar mensaje a Slack
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {slack_token}',
        'Content-type': 'application/json; charset=utf-8'
    }
    data = {
        'channel': slack_channel,
        'text': '\n\n'.join(reportes)
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200 or not response.json().get('ok'):
        print(f'Error enviando mensaje a Slack: {response.text}')
        sys.exit(1)
    print('Reporte de k6 enviado a Slack correctamente.')

if __name__ == '__main__':
    main()
