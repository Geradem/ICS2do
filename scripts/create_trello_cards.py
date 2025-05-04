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

def get_unused_label_color(api_key, token, board_id):
    """
    Obtiene un color no utilizado en el tablero.
    """
    url = f"https://api.trello.com/1/boards/{board_id}/labels"
    query = {
        "key": api_key,
        "token": token
    }
    response = requests.get(url, params=query)
    if response.status_code == 200:
        labels = response.json()
        used_colors = {label["color"] for label in labels if label["color"]}
        all_colors = {
            "green", "yellow", "orange", "red", "purple", "blue", "sky", "lime", "pink", "black"
        }
        # Determinar los colores no usados
        unused_colors = all_colors - used_colors
        return unused_colors.pop() if unused_colors else None
    else:
        print(f"Error al obtener etiquetas del tablero: {response.status_code} - {response.text}")
        return None

def get_unused_cover_color(api_key, token, list_id):
    """
    Obtiene un color de portada no utilizado en las tarjetas de la lista, excluyendo el color rojo.
    """
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    query = {
        "key": api_key,
        "token": token
    }
    response = requests.get(url, params=query)
    if response.status_code == 200:
        cards = response.json()
        used_colors = {card.get("cover", {}).get("color") for card in cards if card.get("cover", {}).get("color")}
        all_colors = {
            "green", "yellow", "orange", "purple", "blue", "sky", "lime", "pink", "black"  # Excluir "red"
        }
        # Determinar los colores no usados
        unused_colors = all_colors - used_colors
        return unused_colors.pop() if unused_colors else None
    else:
        print(f"Error al obtener tarjetas de la lista: {response.status_code} - {response.text}")
        return None

def create_card(api_key, token, list_id, card_name, card_desc, cover_color=None):
    """
    Crea una tarjeta en Trello y asigna un color de portada único si se proporciona.
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

        # Asignar color de portada si se proporciona
        if cover_color:
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

def create_label(api_key, token, board_id, color):
    """
    Busca una etiqueta existente con el color especificado. Si no existe, crea una nueva.
    """
    if not board_id:
        print("Error: El ID del tablero (board_id) no es válido.")
        return None

    # Verificar si ya existe una etiqueta con el color especificado
    url = f"https://api.trello.com/1/boards/{board_id}/labels"
    query = {
        "key": api_key,
        "token": token
    }
    response = requests.get(url, params=query)
    if response.status_code == 200:
        labels = response.json()
        for label in labels:
            if label["color"] == color:
                print(f"Etiqueta con color '{color}' ya existe. Reutilizando etiqueta.")
                return label["id"]

    # Si no existe, crear una nueva etiqueta
    print(f"Creando nueva etiqueta con color '{color}'.")
    url = f"https://api.trello.com/1/labels"
    query = {
        "key": api_key,
        "token": token,
        "name": f"Etiqueta {color}",
        "color": color,
        "idBoard": board_id
    }
    response = requests.post(url, params=query)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print(f"Error al crear etiqueta: {response.status_code} - {response.text}")
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

    if not branch_name:
        print("No se proporcionó BRANCH_NAME.")
        return

    # Buscar tarjeta por nombre de la rama
    card_id = get_card_id_by_name(api_key, token, list_id, branch_name)
    if not card_id:
        # Obtener un color único para la portada de la nueva tarjeta
        cover_color = get_unused_cover_color(api_key, token, list_id)
        card_desc = f"Tarjeta creada automáticamente para la rama '{branch_name}'."
        create_card(api_key, token, list_id, branch_name, card_desc, cover_color)

if __name__ == "__main__":
    main()

name: Crear Tarjeta en Trello al Crear Rama

on:
  push:
    branches:
      - '*'  # Monitorea todas las ramas
  create:
    branches:
      - '*'  # Monitorea la creación de ramas

jobs:
  create_card:
    if: ${{ github.event_name == 'create' || github.event.created }}  # Ejecuta si es un nuevo branch
    runs-on: windows-latest

    steps:
      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Verificar archivos en el directorio
        run: |
          dir

      - name: Crear Tarjeta en Trello
        env:
          TRELLO_API_KEY: ${{ secrets.TRELLO_API_KEY }}
          TRELLO_TOKEN: ${{ secrets.TRELLO_TOKEN }}
          TRELLO_LIST_ID: ${{ secrets.TRELLO_LIST_ID }}
          BRANCH_NAME: ${{ github.ref_name }}  # Captura el nombre de la rama
        run: |
          python scripts/create_trello_card.py