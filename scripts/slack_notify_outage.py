import os
import requests

def send_message_to_slack(token, channel_id, text):
    print(f"Intentando enviar mensaje a canal: {channel_id}")
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "channel": channel_id,
        "text": text
    }
    print(f"Payload: {body}")
    response = requests.post(url, headers=headers, json=body)
    print(f"Código de estado HTTP: {response.status_code}")
    try:
        response_data = response.json()
        print(f"Respuesta de Slack: {response_data}")
    except Exception as e:
        print(f"No se pudo decodificar la respuesta JSON: {e}")
        response_data = {}
    if response.status_code == 200 and response_data.get("ok"):
        print("Mensaje enviado exitosamente a Slack.")
    else:
        print(f"Error al enviar mensaje a Slack: {response_data.get('error')}")
        if response_data.get("error") == "not_in_channel":
            print(f"El bot no está en el canal con ID '{channel_id}'. Asegúrate de invitarlo.")
        elif response_data.get("error") == "channel_not_found":
            print(f"El canal con ID '{channel_id}' no existe. Verifica el ID del canal.")
        elif response_data.get("error") == "invalid_auth":
            print("El token de autenticación es inválido. Verifica tu SLACK_TOKEN.")

def main():
    print("Iniciando script de notificación de outage a Slack...")
    slack_token = os.getenv("SLACK_TOKEN")
    channel_id = os.getenv("SLACK_FUERA_DE_SERVICIO")
    mensaje = os.getenv("SLACK_MENSAJE_ERROR", "El sitio está FUERA DE SERVICIO: los tests fallaron y se desplegó la página de mantenimiento.")

    print(f"SLACK_TOKEN definido: {'Sí' if slack_token else 'No'}")
    print(f"SLACK_FUERA_DE_SERVICIO: {channel_id}")
    print(f"Mensaje a enviar: {mensaje}")

    if not slack_token or not channel_id:
        print("Faltan variables de entorno SLACK_TOKEN o SLACK_FUERA_DE_SERVICIO.")
        return

    send_message_to_slack(slack_token, channel_id, mensaje)

if __name__ == "__main__":
    main()
