import requests
from bs4 import BeautifulSoup
import os
import sys

# --- Nastavení ---
# Klíč se načítá z proměnné prostředí (GitHub Secret)
API_KEY = os.getenv("JUU51KANCHA3PSWDAIGYADVEES9EXV0K5XVUE6X86GHNNIS48DT03NMB66QI0HJBIHLOKAU8PVSYM4B0") 

if not API_KEY:
    # Ukončí skript, pokud klíč není nastaven (na GitHub Actions by neměl být problém)
    print("CHYBA: API klíč SCRAPINGBEE_API_KEY nebyl nalezen v proměnném prostředí!")
    sys.exit(1)

TARGET_URL = "https://tracker.gg/bf6/profile/3186869623/modes"
SCRAPING_BEE_ENDPOINT = "https://app.scrapingbee.com/api/v1/"

# --- Funkce pro komunikaci s ScrapingBee ---
def get_page_content_api(target_url, api_key):
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

# --- Funkce pro parsování dat ---
def parse_stats(html_content):
    print("[*] Analyzuji HTML obsah...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    wins_data = {'BR Quads Wins': 'Nenalezeno', 'BR Duo Wins': 'Nenalezeno'}
    
    mode_sections = soup.find_all('div', class_='name', string=['BR Quads', 'BR Duos'])
    
    for section_title in mode_sections:
        mode_name = section_title.text.strip()
        mode_container = section_title.find_parent('div', class_='stat-group')
        
        if mode_container:
            wins_label = mode_container.find('div', class_='name', string='Wins')
            
            if wins_label:
                wins_value_element = wins_label.find_parent('div', class_='stat-card__stat').find('div', class_='value')
                if wins_value_element:
                    wins_value = wins_value_element.text.strip()
                    
                    if mode_name == 'BR Quads':
                        wins_data['BR Quads Wins'] = wins_value
                    elif mode_name == 'BR Duos':
                        wins_data['BR Duo Wins'] = wins_value
                        
    return wins_data


if __name__ == "__main__":
    html_content = get_page_content_api(TARGET_URL, API_KEY)
    
    if html_content:
        results = parse_stats(html_content)
        
        print("\n--- ✅ Výsledky Scrapování ---")
        print(f"BR Quads Wins: {results.get('BR Quads Wins')}")
        print(f"BR Duo Wins: {results.get('BR Duo Wins')}")
        print("----------------------------")
    else:
        print("\n[!!!] Scrapování selhalo. Obsah stránky nebyl získán.")
