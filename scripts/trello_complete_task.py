import os
import re
import requests

def parse_commit_message(commit_message):
    """
    Extrae el número de historia y tarea del mensaje de commit.
    Formato esperado: |historia|tarea|terminada ...
    """
    match = re.search(r"\|(\d+)\|(\d+)\|terminada", commit_message, re.IGNORECASE)
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

def complete_checklist_item(api_key, token, card_id, checklist_id, tarea_num):
    """
    Marca como completada la tarea cuyo nombre empieza con el número de tarea.
    """
    url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems"
    params = {"key": api_key, "token": token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        for item in response.json():
            if item["name"].startswith(f"{tarea_num}|"):
                checkitem_id = item["id"]
                url_check = f"https://api.trello.com/1/cards/{card_id}/checkItem/{checkitem_id}"
                params_check = {"key": api_key, "token": token, "state": "complete"}
                resp = requests.put(url_check, params=params_check)
                if resp.status_code == 200:
                    print(f"Tarea {tarea_num} marcada como terminada.")
                    return True
    return False

def get_card_progress(api_key, token, card_id):
    checklists = get_checklists(api_key, token, card_id)
    total_items = 0
    completed_items = 0
    for checklist in checklists:
        for item in checklist["checkItems"]:
            total_items += 1
            if item["state"] == "complete":
                completed_items += 1
    if total_items == 0:
        return 0
    porcentaje = (completed_items / total_items) * 100
    print(f"Progreso de la tarjeta: {porcentaje:.2f}%")
    return porcentaje

def move_card_to_list(api_key, token, card_id, list_id):
    url = f"https://api.trello.com/1/cards/{card_id}"
    params = {"key": api_key, "token": token, "idList": list_id}
    response = requests.put(url, params=params)
    if response.status_code == 200:
        print(f"Tarjeta movida a la lista {list_id}.")
    else:
        print(f"Error al mover la tarjeta: {response.status_code} - {response.text}")

def main():
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID")
    list_todo = os.getenv("TRELLO_LIST_TODO_ID")
    list_doing = os.getenv("TRELLO_LIST_DOING_ID")
    list_done = os.getenv("TRELLO_LIST_DONE_ID")
    commit_message = os.getenv("COMMIT_MESSAGE")

    historia_num, tarea_num = parse_commit_message(commit_message)
    print(f"Historia extraída del commit: '{historia_num}'")

    if not historia_num or not tarea_num:
        print("El commit no contiene el formato esperado para historia y tarea.")
        return

    card_id = get_card_by_prefix(api_key, token, board_id, historia_num)
    if not card_id:
        print(f"No se encontró la tarjeta para la historia {historia_num}.")
        return

    checklists = get_checklists(api_key, token, card_id)
    for checklist in checklists:
        if complete_checklist_item(api_key, token, card_id, checklist["id"], tarea_num):
            break

    # Calcular el progreso y mover la tarjeta si corresponde
    progreso = get_card_progress(api_key, token, card_id)
    if progreso == 0:
        destino = list_todo
        print("La tarjeta debe estar en To Do.")
    elif progreso == 100:
        destino = list_done
        print("La tarjeta debe estar en Done.")
    else:
        destino = list_doing
        print("La tarjeta debe estar en Doing.")

    move_card_to_list(api_key, token, card_id, destino)

if __name__ == "__main__":
    main()