import os
import re
import requests

def parse_commit_message(commit_message):
    """
    Extrae el número de historia y tarea del mensaje de commit.
    Formato esperado: |historia|tarea|terminada ...
    """
    match = re.match(r"\|(\d+)\|(\d+)\|terminada", commit_message, re.IGNORECASE)
    if match:
        historia_num = match.group(1)
        tarea_num = match.group(2)
        return historia_num, tarea_num
    return None, None

def get_card_by_prefix(api_key, token, board_id, historia_num):
    """
    Busca la tarjeta de Trello cuyo nombre empieza con el número de historia.
    """
    url = f"https://api.trello.com/1/boards/{board_id}/cards"
    params = {"key": api_key, "token": token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        for card in response.json():
            if card["name"].startswith(f"{historia_num}|"):
                return card["id"]
    return None

def get_checklists(api_key, token, card_id):
    url = f"https://api.trello.com/1/cards/{card_id}/checklists"
    params = {"key": api_key, "token": token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

def complete_checklist_item(api_key, token, checklist_id, tarea_num):
    """
    Marca como completada la tarea cuyo nombre empieza con el número de tarea.
    """
    url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems"
    params = {"key": api_key, "token": token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        for item in response.json():
            if item["name"].startswith(f"{tarea_num}|"):
                # Marcar como completada
                checkitem_id = item["id"]
                url_check = f"https://api.trello.com/1/cards/{item['idCard']}/checkItem/{checkitem_id}"
                params_check = {"key": api_key, "token": token, "state": "complete"}
                resp = requests.put(url_check, params=params_check)
                if resp.status_code == 200:
                    print(f"Tarea {tarea_num} marcada como terminada.")
                    return True
    return False

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

def find_thread_ts(token, channel_id, branch_name):
    """
    Busca el mensaje principal en el canal que contiene el nombre de la rama y devuelve su ts.
    """
    url = "https://slack.com/api/conversations.history"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "channel": channel_id,
        "limit": 100  # Ajusta si tienes muchos mensajes
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200 and response.json().get("ok"):
        messages = response.json().get("messages", [])
        for msg in messages:
            if branch_name in msg.get("text", ""):
                return msg["ts"]
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
    if not channel_id:
        print(f"No se encontró un canal para el prefijo de la rama '{branch_name[:3]}'.")
        return

    thread_ts = find_thread_ts(slack_token, channel_id, branch_name)
    if not thread_ts:
        print(f"No se encontró el mensaje principal para la rama '{branch_name}' en el canal.")
        return

    send_commit_to_thread(slack_token, channel_id, thread_ts, commit_message)

    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID")

    historia_num, tarea_num = parse_commit_message(commit_message)
    if not historia_num or not tarea_num:
        print("El commit no contiene el formato esperado para historia y tarea.")
        return

    card_id = get_card_by_prefix(api_key, token, board_id, historia_num)
    if not card_id:
        print(f"No se encontró la tarjeta para la historia {historia_num}.")
        return

    checklists = get_checklists(api_key, token, card_id)
    for checklist in checklists:
        if complete_checklist_item(api_key, token, checklist["id"], tarea_num):
            return

    print(f"No se encontró la tarea {tarea_num} en la historia {historia_num}.")

if __name__ == "__main__":
    main()