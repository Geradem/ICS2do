import os
import requests

def get_card_id_by_name(api_key, token, list_id, card_name):
    """
    Busca una tarjeta en Trello por su nombre.
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

def get_cover_color_from_branch(branch_name):
    """
    Determina el color de la portada basado en las tres primeras letras del nombre de la rama.
    """
    prefix = branch_name[:3].lower()  # Obtiene las tres primeras letras en minúsculas
    color_mapping = {
        "fea": "pink",
        "dev": "yellow",
        "rls": "green",
        "fix": "orange",
        "mtr": "sky"
    }
    # Devuelve el color correspondiente o 'purple' si no coincide con ningún prefijo
    return color_mapping.get(prefix, "purple")

def create_card(api_key, token, list_id, card_name, card_desc, branch_name):
    """
    Crea una tarjeta en Trello y asigna un color de portada basado en el nombre de la rama.
    """
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
        card_id = response.json()["id"]
        print(f"Tarjeta '{card_name}' creada exitosamente.")

        # Determinar el color de la portada basado en el nombre de la rama
        cover_color = get_cover_color_from_branch(branch_name)
        set_card_cover(api_key, token, card_id, cover_color)

        return card_id
    else:
        print(f"Error al crear tarjeta: {response.status_code} - {response.text}")
        return None

def set_card_cover(api_key, token, card_id, color):
    """
    Asigna un color de portada a una tarjeta con tamaño completo.
    """
    url = f"https://api.trello.com/1/cards/{card_id}"
    query = {
        "key": api_key,
        "token": token
    }
    body = {
        "cover": {
            "color": color,
            "size": "full"  # Configurar la portada como tamaño completo
        }
    }
    response = requests.put(url, params=query, json=body)
    if response.status_code == 200:
        print(f"Portada de la tarjeta configurada con color '{color}' y tamaño completo.")
    else:
        print(f"Error al configurar la portada: {response.status_code} - {response.text}")

def main():
    """
    Punto de entrada principal para crear una tarjeta en Trello basada en el nombre de la rama.
    """
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    list_id = os.getenv("TRELLO_LIST_ID")
    branch_name = os.getenv("BRANCH_NAME")

    if not branch_name:
        print("No se proporcionó BRANCH_NAME.")
        return

    # Buscar tarjeta por nombre de la rama
    card_id = get_card_id_by_name(api_key, token, list_id, branch_name)
    if not card_id:
        # Crear la tarjeta con el color basado en el nombre de la rama
        card_desc = f"Tarjeta creada automáticamente para la rama '{branch_name}'."
        create_card(api_key, token, list_id, branch_name, card_desc, branch_name)

if __name__ == "__main__":
    main()