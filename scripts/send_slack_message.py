import os
import requests

def get_channel_id_from_branch(branch_name):
    prefix = branch_name[:3].lower()
    channel_mapping = {
        "fea": os.getenv("FEATURE_CHANNEL_ID"),
        "dev": os.getenv("DEVELOP_CHANNEL_ID"),
        "rls": os.getenv("RELEASE_CHANNEL_ID"),
        "fix": os.getenv("HOTFIX_CHANNEL_ID"),
        "mtr": os.getenv("MASTER_CHANNEL_ID")
    }
    return channel_mapping.get(prefix, os.getenv("OTHER_CHANNEL_ID"))

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
    branch_name = os.getenv("BRANCH_NAME")

    if not branch_name:
        print("No se proporcionó BRANCH_NAME.")
        return

    channel_id = get_channel_id_from_branch(branch_name)
    if not channel_id:
        print(f"No se encontró un canal para el prefijo de la rama '{branch_name[:3]}'.")
        return

    project_name = branch_name[4:].lstrip("_-")
    message = f"Se establecio el proyecto {project_name}, para verificar su avance recise el hilo de este mensaje"
    send_message_to_slack(slack_token, channel_id, message)

if __name__ == "__main__":
    main()