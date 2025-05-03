import os
import requests

def get_card_id_by_name(api_key, token, list_id, card_name):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    query = {
        "key": api_key,
        "token": token
    }
    response = requests.get(url, params=query)
    if response.status_code == 200:
        cards = response.json()
        for card in cards:
            if card["name"] == card_name:
                return card["id"]
    else:
        print(f"Error al obtener tarjetas: {response.status_code} - {response.text}")
    return None

def create_card(api_key, token, list_id, card_name, card_desc):
    url = "https://api.trello.com/1/cards"
    query = {
        "key": api_key,
        "token": token,
        "idList": list_id,
        "name": card_name,
        "desc": card_desc
    }
    response = requests.post(url, params=query)
    if response.status_code == 200:
        print(f"Tarjeta '{card_name}' creada exitosamente.")
        return response.json()["id"]
    else:
        print(f"Error al crear tarjeta: {response.status_code} - {response.text}")
    return None

def add_comment_to_card(api_key, token, card_id, comment):
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    query = {
        "key": api_key,
        "token": token,
        "text": comment
    }
    response = requests.post(url, params=query)
    if response.status_code == 200:
        print("Comentario agregado exitosamente.")
    else:
        print(f"Error al agregar comentario: {response.status_code} - {response.text}")

def main():
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    list_id = os.getenv("TRELLO_LIST_ID")
    branch_name = os.getenv("BRANCH_NAME")
    commit_message = os.getenv("COMMIT_MESSAGE")

    if not branch_name or not commit_message:
        print("No se proporcionaron BRANCH_NAME o COMMIT_MESSAGE.")
        return

    # Buscar tarjeta por nombre de la rama
    card_id = get_card_id_by_name(api_key, token, list_id, branch_name)
    if not card_id:
        # Crear tarjeta si no existe
        card_desc = f"Tarjeta creada automáticamente para la rama '{branch_name}'."
        card_id = create_card(api_key, token, list_id, branch_name, card_desc)

    if card_id:
        # Agregar comentario con el mensaje del commit
        add_comment_to_card(api_key, token, card_id, f"Nuevo commit: {commit_message}")

if __name__ == "__main__":
    main()