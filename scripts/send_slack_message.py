import os
import requests

def get_channel_id_from_branch(branch_name):
    """
    Determina el canal de Slack basado en las tres primeras letras del nombre de la rama.
    """
    prefix = branch_name[:3].lower()  # Obtiene las tres primeras letras en minúsculas
    channel_mapping = {
        "fea": os.getenv("FEATURE_CHANNEL_ID"),  # Canal para 'feature'
        "dev": os.getenv("DEVELOP_CHANNEL_ID"),  # Canal para 'develop'
        "rls": os.getenv("RELEASE_CHANNEL_ID"),  # Canal para 'release'
        "fix": os.getenv("HOTFIX_CHANNEL_ID"),   # Canal para 'hotfix'
        "mtr": os.getenv("MASTER_CHANNEL_ID")    # Canal para 'master'
    }
    # Devuelve el canal correspondiente o el canal 'otros' si no coincide con ningún prefijo
    return channel_mapping.get(prefix, os.getenv("OTHER_CHANNEL_ID"))

def send_message_to_slack(token, channel_id, text):
    """
    Envía un mensaje a un canal de Slack.
    """
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
    if response.status_code == 200 and response.json().get("ok"):
        print("Mensaje enviado exitosamente a Slack.")
    else:
        print(f"Error al enviar mensaje a Slack: {response.status_code} - {response.text}")

def main():
    """
    Punto de entrada principal para enviar un mensaje a Slack basado en el nombre de la rama.
    """
    slack_token = os.getenv("SLACK_TOKEN")
    branch_name = os.getenv("BRANCH_NAME")
    commit_message = os.getenv("COMMIT_MESSAGE")

    if not branch_name or not commit_message:
        print("No se proporcionaron BRANCH_NAME o COMMIT_MESSAGE.")
        return

    # Determinar el canal basado en las tres primeras letras del nombre de la rama
    channel_id = get_channel_id_from_branch(branch_name)
    if not channel_id:
        print(f"No se encontró un canal para el prefijo de la rama '{branch_name[:3]}'.")
        return

    # Enviar el mensaje a Slack
    message = f"Nuevo commit en la rama '{branch_name}': {commit_message}"
    send_message_to_slack(slack_token, channel_id, message)

if __name__ == "__main__":
    main()