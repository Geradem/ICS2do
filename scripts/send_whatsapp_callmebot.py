import os
import requests

def main():
    phone = os.getenv("CALLMEBOT_PHONE")  # Ej: +549XXXXXXXXXX
    apikey = os.getenv("CALLMEBOT_APIKEY")  # El API key que te da CallMeBot
    mensaje = os.getenv("CALLMEBOT_MENSAJE", "El sitio está FUERA DE SERVICIO: los tests fallaron y se desplegó la página de mantenimiento.")

    print(f"CALLMEBOT_PHONE: {phone}")
    print(f"CALLMEBOT_APIKEY definido: {'Sí' if apikey else 'No'}")
    print(f"Mensaje a enviar: {mensaje}")

    if not phone or not apikey:
        print("Faltan variables de entorno CALLMEBOT_PHONE o CALLMEBOT_APIKEY.")
        return

    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={mensaje}&apikey={apikey}"
    print(f"URL: {url}")
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Respuesta: {response.text}")

if __name__ == "__main__":
    main()
