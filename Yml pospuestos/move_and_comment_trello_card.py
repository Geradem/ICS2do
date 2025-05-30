import os
import requests

def get_card_id_by_name(api_key, token, list_id, card_name):
    """
    Busca una tarjeta en Trello por su nombre dentro de una lista específica.
    """
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

def move_card_to_list(api_key, token, card_id, list_id):
    """
    Mueve una tarjeta a otra lista en Trello.
    """
    url = f"https://api.trello.com/1/cards/{card_id}"
    query = {
        "key": api_key,
        "token": token,
        "idList": list_id
    }
    response = requests.put(url, params=query)
    if response.status_code == 200:
        print(f"Tarjeta movida exitosamente a la lista con ID '{list_id}'.")
    else:
        print(f"Error al mover la tarjeta: {response.status_code} - {response.text}")

def add_comment_to_card(api_key, token, card_id, comment):
    """
    Agrega un comentario a una tarjeta en Trello.
    """
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    query = {
        "key": api_key,
        "token": token
    }
    body = {
        "text": comment
    }
    response = requests.post(url, params=query, json=body)
    if response.status_code == 200:
        print(f"Comentario agregado exitosamente a la tarjeta.")
    else:
        print(f"Error al agregar comentario: {response.status_code} - {response.text}")

def main():
    """
    Punto de entrada principal para mover una tarjeta y agregar un comentario.
    """
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    board_id = os.getenv("TRELLO_BOARD_ID")
    todo_list_id = os.getenv("TODO_LIST_ID")
    doing_list_id = os.getenv("DOING_LIST_ID")
    branch_name = os.getenv("BRANCH_NAME")
    commit_message = os.getenv("COMMIT_MESSAGE")

    if not branch_name or not commit_message:
        print("No se proporcionaron BRANCH_NAME o COMMIT_MESSAGE.")
        return

    # Buscar tarjeta en la lista To Do
    card_id = get_card_id_by_name(api_key, token, todo_list_id, branch_name)
    if card_id:
        # Mover la tarjeta a la lista Doing
        move_card_to_list(api_key, token, card_id, doing_list_id)
        # Agregar comentario
        add_comment_to_card(api_key, token, card_id, commit_message)
        return

    # Si no está en To Do, buscar en Doing
    card_id = get_card_id_by_name(api_key, token, doing_list_id, branch_name)
    if card_id:
        # Solo agregar comentario
        add_comment_to_card(api_key, token, card_id, commit_message)
        return

    print(f"No se encontró una tarjeta con el nombre '{branch_name}' en las listas To Do o Doing.")

if __name__ == "__main__":
    main()