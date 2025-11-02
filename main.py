import csv
import re
import sys
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Set

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"

def ziskaj_html(url: str) -> str:
    """Načíta HTML stránku a vráti jej obsah ako text."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        print(f"Chyba pri načítaní {url}: {e}", file=sys.stderr)
        sys.exit(1)

def ziskaj_odkazy_obci(url: str) -> List[Tuple[str, str, str]]:
    """Získa zoznam obcí (kód, názov, URL) z okresnej stránky."""
    soup = BeautifulSoup(ziskaj_html(url), 'html.parser')
    obce: List[Tuple[str, str, str]] = []

    for tabulka in soup.find_all('table'):
        for riadok in tabulka.find_all('tr')[2:]:
            bunky = riadok.find_all('td')
            if len(bunky) >= 2:
                kod = bunky[0].text.strip()
                nazov = bunky[1].text.strip()
                odkaz = bunky[0].find('a')
                if odkaz and odkaz.get('href'):
                    href = odkaz['href']
                    plna_url = requests.compat.urljoin(BASE_URL, href)
                    obce.append((kod, nazov, plna_url))
    return obce

def ziskaj_vysledky_obce(url: str) -> Tuple[int, int, int, Dict[str, int]]:
    """Získa výsledky hlasovania pre danú obec."""
    soup = BeautifulSoup(ziskaj_html(url), 'html.parser')

    def najdi_podla_header(vzor: str) -> int:
        """Nájde číselnú hodnotu podľa vzoru v atribúte 'headers'."""
        bunka = soup.find("td", headers=re.compile(vzor))
        if bunka:
            cislo = bunka.text.replace('\xa0', '').replace(' ', '')
            cislo = cislo.replace(',', '.')
            try:
                return int(float(cislo))
            except ValueError:
                return 0
        return 0

    volici = najdi_podla_header("sa2")
    obalky = najdi_podla_header("sa3")
    platne = najdi_podla_header("sa6")

    strany: Dict[str, int] = {}
    for tab in soup.find_all('table', class_='table'):
        for riadok in tab.find_all('tr')[2:]:
            bunky = riadok.find_all('td')
            if len(bunky) >= 3:
                nazov_strany = bunky[1].text.strip()
                hlasy_text = bunky[2].text.strip()
                hlasy_text = hlasy_text.replace('\xa0', '').replace(' ', '')
                hlasy_text = hlasy_text.replace(',', '.')
                try:
                    pocet_hlasov = int(float(hlasy_text))
                except ValueError:
                    pocet_hlasov = 0
                if nazov_strany:
                    strany[nazov_strany] = pocet_hlasov

    return volici, obalky, platne, strany

def uloz_csv(
    subor: str,
    data: List[Dict[str, int]],
    strany: Set[str]
) -> None:
    """Uloží výsledky do CSV súboru."""
    zakladne_stlpce = [
        "kód_obce", "názov_obce", "voliči_v_zozname",
        "vydané_obálky", "platné_hlasy"
    ]

    nazvy_stran = [
        nazov for nazov in strany
        if isinstance(nazov, str) and any(not c.isdigit() for c in nazov)
    ]

    hlavicka = zakladne_stlpce + sorted(nazvy_stran)

    with open(subor, 'w', newline='', encoding='utf-8') as f:
        zapis = csv.DictWriter(f, fieldnames=hlavicka, delimiter=';')
        zapis.writeheader()
        for riadok in data:
            ocisteny_riadok = {
                k: v for k, v in riadok.items() if k in hlavicka
            }
            zapis.writerow(ocisteny_riadok)

def main() -> None:
    """Hlavná funkcia: načíta URL, spracuje obce, uloží výsledky."""
    if len(sys.argv) != 3:
        print("Použitie: python main.py <URL> <vystupny_subor.csv>")
        sys.exit(1)

    url, vystup = sys.argv[1], sys.argv[2]

    if not url.startswith(BASE_URL):
        print(f"URL musí začínať na {BASE_URL}")
        sys.exit(1)

    obce = ziskaj_odkazy_obci(url)
    celkovy_pocet = len(obce)
    print(f"\U0001F3E0  Nájdených obcí: {celkovy_pocet}")

    vysledky: List[Dict[str, int]] = []
    vsetky_strany: Set[str] = set()

    for i, (kod, nazov, detail_url) in enumerate(obce, 1):
        percent = round(i / celkovy_pocet * 100)
        print(f"➡️  [{i}/{celkovy_pocet}] {nazov:<30} ({percent}%)")

        volici, obalky, platne, strany = ziskaj_vysledky_obce(detail_url)
        vsetky_strany.update(strany.keys())

        riadok: Dict[str, int] = {
            "kód_obce": kod,
            "názov_obce": nazov,
            "voliči_v_zozname": volici,
            "vydané_obálky": obalky,
            "platné_hlasy": platne
        }
        riadok.update(strany)
        vysledky.append(riadok)

    uloz_csv(vystup, vysledky, vsetky_strany)
    print(f"\n✅ Hotovo! Výsledky uložené do: {vystup}")

if __name__ == "__main__":
    main()