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

def get_channel_name(token, channel_id):
    url = "https://slack.com/api/conversations.info"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "channel": channel_id
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200 and response.json().get("ok"):
        return response.json()["channel"]["name"]
    return f"(ID: {channel_id})"

def find_thread_ts(token, channel_id, branch_name):
    url = "https://slack.com/api/conversations.history"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "channel": channel_id,
        "limit": 200
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200 and response.json().get("ok"):
        messages = response.json().get("messages", [])
        project_name = branch_name[4:].lstrip("_-")
        print(f"Buscando en canal: {get_channel_name(token, channel_id)}")
        print(f"Nombre del proyecto a buscar: '{project_name}'")
        print(f"Cantidad de mensajes recuperados: {len(messages)}")
        for i, msg in enumerate(messages):
            text = msg.get("text", "")
            print(f"[{i+1}] Texto del mensaje: '{text}'")
            if project_name in text:
                print(f"¡Coincidencia encontrada en el mensaje {i+1}!")
                return msg["ts"]
        print("No se encontró coincidencia en los mensajes recuperados.")
    else:
        print(f"Error al obtener mensajes del canal: {response.status_code} - {response.text}")
    return None

def send_commit_to_thread(token, channel_id, thread_ts, commit_message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "channel": channel_id,
        "text": commit_message,
        "thread_ts": thread_ts
    }
    response = requests.post(url, headers=headers, json=body)
    response_data = response.json()
    if response.status_code == 200 and response_data.get("ok"):
        print("Commit publicado en el hilo de Slack.")
    else:
        print(f"Error al publicar commit en Slack: {response_data.get('error')}")

def main():
    slack_token = os.getenv("SLACK_TOKEN")
    branch_name = os.getenv("BRANCH_NAME")
    commit_message = os.getenv("COMMIT_MESSAGE")

    if not branch_name or not commit_message:
        print("No se proporcionó BRANCH_NAME o COMMIT_MESSAGE.")
        return

    channel_id = get_channel_id_from_branch(branch_name)
    channel_name = get_channel_name(slack_token, channel_id)
    print(f"Canal seleccionado para la rama '{branch_name}': {channel_name}")
    if not channel_id:
        print(f"No se encontró un canal para el prefijo de la rama '{branch_name[:3]}'.")
        return

    thread_ts = find_thread_ts(slack_token, channel_id, branch_name)
    if not thread_ts:
        print(f"No se encontró el mensaje principal para la rama '{branch_name}' en el canal '{channel_name}'.")
        return

    send_commit_to_thread(slack_token, channel_id, thread_ts, commit_message)

if __name__ == "__main__":
    main()