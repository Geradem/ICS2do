import os
import requests

def send_message_to_slack(token, channel_id, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "channel": channel_id,
        "text": text
    }
    response = requests.post(url, headers=headers, json=body)
    response_data = response.json()
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
    slack_token = os.getenv("SLACK_TOKEN")
    fuera_servicio_channel = os.getenv("SLACK_FUERA_DE_SERVICIO")
    normal_channel = os.getenv("SLACK_CANAL_NORMAL")
    despliegue_ok = os.getenv("DEPLOY_OK")

    if despliegue_ok == "1" and normal_channel:
        message = "✅ El sitio se desplegó exitosamente."
        send_message_to_slack(slack_token, normal_channel, message)
        return

    if fuera_servicio_channel:
        message = "El sitio está FUERA DE SERVICIO: los tests fallaron y se desplegó la página de mantenimiento."
        send_message_to_slack(slack_token, fuera_servicio_channel, message)
    else:
        print("No se proporcionó SLACK_FUERA_DE_SERVICIO. No se enviará mensaje de error.")

if __name__ == "__main__":
    main()