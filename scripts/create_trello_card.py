import os
import requests

def create_trello_card():
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    list_id = os.getenv("TRELLO_LIST_ID")
    card_name = f"🚀 Nueva tarea en Trello - {os.getenv('GITHUB_HEAD_COMMIT_MESSAGE', 'Sin mensaje')}"
    card_desc = f"Commit por {os.getenv('GITHUB_ACTOR')} en {os.getenv('GITHUB_REPOSITORY')}. Revisar cambios en Trello."

    url = f"https://api.trello.com/1/cards"
    query = {
        "key": api_key,
        "token": token,
        "idList": list_id,
        "name": card_name,
        "desc": card_desc
    }

    response = requests.post(url, json=query)
    if response.status_code == 200:
        print("Tarjeta creada exitosamente en Trello.")
    else:
        print(f"Error al crear la tarjeta: {response.status_code} - {response.text}")

if __name__ == "__main__":
    create_trello_card()