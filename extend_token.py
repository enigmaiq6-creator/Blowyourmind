import os
import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("FACEBOOK_APP_ID")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
SHORT_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

def extend():
    print("Iniciando extension de token...")
    
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": SHORT_TOKEN
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Error en paso 1: " + response.text)
        return

    long_lived_token = response.json().get("access_token")
    print("Token de larga duracion obtenido (Paso 1).")
    
    url_pages = "https://graph.facebook.com/v19.0/me/accounts"
    params_pages = {
        "access_token": long_lived_token
    }
    
    response_pages = requests.get(url_pages, params=params_pages)
    if response_pages.status_code != 200:
        print("Error en paso 2: " + response_pages.text)
        return
    
    pages_data = response_pages.json().get("data", [])
    target_page = next((p for p in pages_data if p["id"] == PAGE_ID), None)
    
    if target_page:
        final_token = target_page["access_token"]
        print("EXITO! Tu Long-Lived Page Token es:")
        print("--------------------------------------------------")
        print(final_token)
        print("--------------------------------------------------")
        return final_token
    else:
        print("No se encontro la pagina con ID " + str(PAGE_ID))
        if pages_data:
            print("Paginas encontradas: " + str([p.get("name") for p in pages_data]))

if __name__ == "__main__":
    extend()
