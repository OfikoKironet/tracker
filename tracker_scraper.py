import requests
from bs4 import BeautifulSoup
import os
import sys

# --- Nastavení ---
API_KEY = os.getenv("SCRAPINGBEE_API_KEY") 

if not API_KEY:
    # Tato chyba je v pořádku, pokud je skript spuštěn bez Secretu, ale v Actions to má fungovat.
    print("CHYBA: API klíč SCRAPINGBEE_API_KEY nebyl nalezen v proměnném prostředí!")
    sys.exit(1)

TARGET_URL = "https://tracker.gg/bf6/profile/3186869623/modes"
SCRAPING_BEE_ENDPOINT = "https://app.scrapingbee.com/api/v1/"

# --- Funkce pro komunikaci s ScrapingBee (Beze změny) ---
def get_page_content_api(target_url, api_key):
    # ... (Kód pro komunikaci s ScrapingBee je stejný) ...
    print(f"[*] Odesílám požadavek na ScrapingBee pro URL: {target_url}...")
    
    payload = {
        "api_key": api_key,
        "url": target_url,
        "render_js": "true",
        "forward_headers": "true" 
    }
    
    try:
        response = requests.get(SCRAPING_BEE_ENDPOINT, params=payload, timeout=60)
        response.raise_for_status()
        print("[+] Obsah stránky získán přes API.")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[-] Chyba při komunikaci s Scraping API: {e}")
        return None

# --- ZMĚNĚNÁ Funkce pro parsování dat ---
def parse_stats(html_content):
    """
    Analyzuje HTML a extrahuje Wins pro BR Quads a BR Duos pomocí pořadí prvků.
    Předpokládá, že hledané statistiky jsou první v daném kontejneru.
    """
    print("[*] Analyzuji HTML obsah podle nových selektorů...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    wins_data = {'BR Quads Wins': 'Nenalezeno', 'BR Duo Wins': 'Nenalezeno'}
    
    # NOVÝ SELEKTOR: Cílíme na buňky, které obsahují třídu 'value truncate'
    # Toto by měly být buňky, které zobrazují hodnoty (včetně vašich "13" a "3").
    
    # 1. Najdeme kontejner s tabulkou/seznamem módů (např. třída 'stat-group')
    # Protože neznáme přesnou strukturu, zkusíme najít všechny elementy s hodnotou
    
    # Hledáme všechny SPANy s třídou 'truncate', které jsou uvnitř 'value'
    value_spans = soup.find_all('span', class_='truncate')
    
    # Extrahujeme hodnoty, pokud se jedná o statistiku
    extracted_values = []
    for span in value_spans:
        # Zkontrolujeme, že se nejedná o textové popisky
        # Většina hodnot bude mít pouze číslo a volitelný text
        value = span.text.strip()
        if value and value.replace('.', '', 1).isdigit() or value.isdigit():
             extracted_values.append(value)

    # Nyní přiřazujeme podle pořadí (Rizikové, ale nutné pro danou strukturu)
    
    if len(extracted_values) >= 1:
        # Předpoklad: První nalezena hodnota je BR Quads Wins (ve vašem případě "13")
        wins_data['BR Quads Wins'] = extracted_values[0]

    if len(extracted_values) >= 2:
        # Předpoklad: Druhá nalezena hodnota je BR Duo Wins (ve vašem případě "3")
        wins_data['BR Duo Wins'] = extracted_values[1]
        
    # Pokud se najdou jiné hodnoty (např. K/D, Matches, atd.), budou ignorovány po druhém prvku.
        
    return wins_data


if __name__ == "__main__":
    html_content = get_page_content_api(TARGET_URL, API_KEY)
    
    if html_content:
        # Zde můžete odkomentovat pro lokální ladění a uložení HTML
        # with open("tracker_output.html", "w", encoding="utf-8") as f:
        #    f.write(html_content)

        results = parse_stats(html_content)
        
        print("\n--- ✅ Výsledky Scrapování ---")
        print(f"BR Quads Wins: {results.get('BR Quads Wins')}")
        print(f"BR Duo Wins: {results.get('BR Duo Wins')}")
        print("----------------------------")
    else:
        print("\n[!!!] Scrapování selhalo. Obsah stránky nebyl získán.")
