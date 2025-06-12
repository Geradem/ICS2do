import json
import os

K6_SUMMARY = "k6-summary.json"
THRESHOLD_MS = 800  # tiempo máximo de respuesta aceptable


def main():
    if not os.path.exists(K6_SUMMARY):
        print("No se encontró el resumen de k6.")
        return

    with open(K6_SUMMARY) as f:
        data = json.load(f)

    http_req_duration = data["metrics"]["http_req_duration"].get("p(95)")
    http_req_failed = data["metrics"]["http_req_failed"].get("rate")

    http_req_url = data["metrics"].get("http_req_url", {})
    if "values" in http_req_url and len(http_req_url["values"]) > 1:
        print("Se detectaron múltiples dominios en la prueba de k6. No se notificará outage automáticamente.")
        return

    if http_req_duration is None:
        print("No se encontró el valor p(95) en http_req_duration.")
        http_req_duration = 0
    if http_req_failed is None:
        print("No se encontró el valor rate en http_req_failed.")
        http_req_failed = 0

    print(f"p95 de respuesta: {http_req_duration} ms")
    print(f"Tasa de fallos: {http_req_failed}")
    print("No se enviarán notificaciones de outage. Solo se reporta el resultado.")


if __name__ == "__main__":
    main()
