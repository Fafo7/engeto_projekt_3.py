# Volebné výsledky - Web Scraper

Tento skript slúži na získavanie výsledkov volieb do Poslaneckej snemovne Parlamentu Českej republiky z roku 2017. Script sťahuje a spracováva dáta z oficiálneho webu volby.cz.

## Funkcionalita

- Sťahuje volebné výsledky pre všetky obce vo vybranom okrese
- Spracováva údaje o počte voličov, vydaných obálkach a platných hlasoch
- Zbiera výsledky všetkých politických strán
- Ukladá dáta do CSV súboru s oddeľovačom ";"

## Požiadavky

Pre správne fungovanie skriptu potrebujete:

```bash
pip install requests
pip install beautifulsoup4
```

## Použitie

Script sa spúšťa z príkazového riadku s dvoma povinnými parametrami:

```bash
python main.py <URL> <vystupny_subor.csv>
```

Kde:
- `<URL>` je odkaz na stránku okresu (napr. "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103")
- `<vystupny_subor.csv>` je názov súboru, do ktorého sa majú uložiť výsledky (napr. "vysledky_kladno.csv")

### Príklad použitia

```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103" "vysledky_kladno.csv"
```

## Výstupný formát

Skript vytvorí CSV súbor s nasledujúcimi stĺpcami:
- kód_obce
- názov_obce
- voliči_v_zozname
- vydané_obálky
- platné_hlasy
- [názvy všetkých politických strán]

## Priebeh spracovania

1. Načítanie vstupnej stránky okresu
2. Získanie zoznamu všetkých obcí v okrese
3. Pre každú obec:
   - Stiahnutie detailných výsledkov
   - Spracovanie počtu voličov, obálok a platných hlasov
   - Spracovanie výsledkov jednotlivých strán
4. Uloženie všetkých dát do výstupného CSV súboru

## Poznámky

- Script používa knižnicu requests pre sťahovanie dát
- BeautifulSoup4 sa používa na parsovanie HTML
- Výstupný CSV súbor používa kódovanie UTF-8
- Progress je zobrazovaný v konzole počas spracovania

## Chybové hlásenia

Script obsahuje ošetrenie základných chýb:
- Nesprávny počet argumentov
- Nesprávna URL adresa
- Problémy pri sťahovaní dát

Pri výskyte chyby sa zobrazí príslušné chybové hlásenie a script sa ukončí s nenulovým návratovým kódom.
