import json
import os
import re
from typing import Optional
from bs4 import BeautifulSoup
from scrapper.fetcher import fetch_html
from scrapper.teams import detect_formation_from_squad_html

# Mapping of SoFIFA position badges to domain Position enum names
SOFIFA_POSITION_MAP = {
    "GK": "GOALKEEPER",
    "BR": "GOALKEEPER",
    "LB": "LEFT_BACK",
    "LO": "LEFT_BACK",
    "CB": "CENTRE_BACK",
    "ŚO": "CENTRE_BACK",
    "RB": "RIGHT_BACK",
    "PO": "RIGHT_BACK",
    "LWB": "LEFT_WING_BACK",
    "CLO": "LEFT_WING_BACK",
    "RWB": "RIGHT_WING_BACK",
    "CPO": "RIGHT_WING_BACK",
    "CDM": "CENTRAL_DEFENSIVE_MIDFIELDER",
    "ŚPD": "CENTRAL_DEFENSIVE_MIDFIELDER",
    "CM": "CENTRAL_MIDFIELDER",
    "ŚP": "CENTRAL_MIDFIELDER",
    "CAM": "CENTRAL_ATTACKING_MIDFIELDER",
    "ŚPO": "CENTRAL_ATTACKING_MIDFIELDER",
    "LM": "LEFT_MIDFIELDER",
    "LP": "LEFT_MIDFIELDER",
    "RM": "RIGHT_MIDFIELDER",
    "PP": "RIGHT_MIDFIELDER",
    "LW": "LEFT_WING",
    "LS": "LEFT_WING",
    "CF": "CENTRAL_FORWARD",
    "ŚN": "CENTRAL_FORWARD",
    "RW": "RIGHT_WING",
    "PS": "RIGHT_WING",
    "ST": "STRIKER",
    "N": "STRIKER",
}

SOFIFA_NATIONALITY_MAP = {
    # UEFA
    "Albania": "Albania",
    "Andora": "Andorra",
    "Armenia": "Armenia",
    "Austria": "Austria",
    "Azerbejdżan": "Azerbaijan",
    "Białoruś": "Belarus",
    "Belgia": "Belgium",
    "Bośnia i Hercegowina": "Bosnia and Herzegovina",
    "Bośnia i Herc.": "Bosnia and Herzegovina",
    "Bułgaria": "Bulgaria",
    "Chorwacja": "Croatia",
    "Cypr": "Cyprus",
    "Czechy": "Czechia",
    "Republika Czeska": "Czechia",
    "Dania": "Denmark",
    "Anglia": "England",
    "Estonia": "Estonia",
    "Wyspy Owcze": "Faroe Islands",
    "Finlandia": "Finland",
    "Francja": "France",
    "Gruzja": "Georgia",
    "Niemcy": "Germany",
    "Gibraltar": "Gibraltar",
    "Grecja": "Greece",
    "Węgry": "Hungary",
    "Islandia": "Iceland",
    "Izrael": "Israel",
    "Włochy": "Italy",
    "Kazachstan": "Kazakhstan",
    "Kosowo": "Kosovo",
    "Łotwa": "Latvia",
    "Liechtenstein": "Liechtenstein",
    "Litwa": "Lithuania",
    "Luksemburg": "Luxembourg",
    "Malta": "Malta",
    "Mołdawia": "Moldova",
    "Czarnogóra": "Montenegro",
    "Holandia": "Netherlands",
    "Macedonia Północna": "North Macedonia",
    "Irlandia Północna": "Northern Ireland",
    "Norwegia": "Norway",
    "Polska": "Poland",
    "Portugalia": "Portugal",
    "Irlandia": "Republic of Ireland",
    "Republika Irlandii": "Republic of Ireland",
    "Rumunia": "Romania",
    "Rosja": "Russia",
    "San Marino": "San Marino",
    "Szkocja": "Scotland",
    "Serbia": "Serbia",
    "Słowacja": "Slovakia",
    "Słowenia": "Slovenia",
    "Hiszpania": "Spain",
    "Szwecja": "Sweden",
    "Szwajcaria": "Switzerland",
    "Turcja": "Turkey",
    "Ukraina": "Ukraine",
    "Walia": "Wales",

    # CONMEBOL
    "Argentyna": "Argentina",
    "Boliwia": "Bolivia",
    "Brazylia": "Brazil",
    "Chile": "Chile",
    "Kolumbia": "Colombia",
    "Ekwador": "Ecuador",
    "Paragwaj": "Paraguay",
    "Peru": "Peru",
    "Urugwaj": "Uruguay",
    "Wenezuela": "Venezuela",

    # CONCACAF
    "Anguilla": "Anguilla",
    "Antigua i Barbuda": "Antigua and Barbuda",
    "Aruba": "Aruba",
    "Bahamy": "Bahamas",
    "Barbados": "Barbados",
    "Belize": "Belize",
    "Bermudy": "Bermuda",
    "Brytyjskie Wyspy Dziewicze": "British Virgin Islands",
    "Kanada": "Canada",
    "Kajmany": "Cayman Islands",
    "Kostaryka": "Costa Rica",
    "Kuba": "Cuba",
    "Curaçao": "Curaçao",
    "Dominika": "Dominica",
    "Dominikana": "Dominican Republic",
    "Salwador": "El Salvador",
    "Grenada": "Grenada",
    "Gwatemala": "Guatemala",
    "Gujana": "Guyana",
    "Haiti": "Haiti",
    "Honduras": "Honduras",
    "Jamajka": "Jamaica",
    "Meksyk": "Mexico",
    "Montserrat": "Montserrat",
    "Nikaragua": "Nicaragua",
    "Panama": "Panama",
    "Portoryko": "Puerto Rico",
    "Puerto Rico": "Puerto Rico",
    "Saint Kitts i Nevis": "Saint Kitts and Nevis",
    "Saint Lucia": "Saint Lucia",
    "Saint Vincent i Grenadyny": "Saint Vincent and the Grenadines",
    "Surinam": "Suriname",
    "Trynidad i Tobago": "Trinidad and Tobago",
    "Turks i Caicos": "Turks and Caicos Islands",
    "Stany Zjednoczone": "United States",
    "USA": "United States",
    "Wyspy Dziewicze Stanów Zjednoczonych": "US Virgin Islands",

    # CAF
    "Algieria": "Algeria",
    "Angola": "Angola",
    "Benin": "Benin",
    "Botswana": "Botswana",
    "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi",
    "Zielony Przylądek": "Cabo Verde",
    "Wyspy Zielonego Przylądka": "Cabo Verde",
    "Kamerun": "Cameroon",
    "Republika Środkowoafrykańska": "Central African Republic",
    "Rep. Środkowoafryk.": "Central African Republic",
    "Czad": "Chad",
    "Komory": "Comoros",
    "Kongo": "Congo",
    "Demokratyczna Republika Konga": "Congo DR",
    "Demokr. Rep. Konga": "Congo DR",
    "DR Kongo": "Congo DR",
    "Wybrzeże Kości Słoniowej": "Côte d'Ivoire",
    "WKS": "Côte d'Ivoire",
    "Ivory Coast": "Côte d'Ivoire",
    "Zielony Przylądek": "Cabo Verde",
    "Wyspy Zielonego Przylądka": "Cabo Verde",
    "W-y Ziel. Przylądka": "Cabo Verde",
    "Saint Vincent i Grenadyny": "Saint Vincent and the Grenadines",
    "St Vincent i Grenad.": "Saint Vincent and the Grenadines",
    "Dżibuti": "Djibouti",
    "Egipt": "Egypt",
    "Gwinea Równikowa": "Equatorial Guinea",
    "Erytrea": "Eritrea",
    "Eswatini": "Eswatini",
    "Suazi": "Eswatini",
    "Etiopia": "Ethiopia",
    "Gabon": "Gabon",
    "Gambia": "Gambia",
    "Ghana": "Ghana",
    "Gwinea": "Guinea",
    "Gwinea Bissau": "Guinea-Bissau",
    "Gwinea-Bissau": "Guinea-Bissau",
    "Kenia": "Kenya",
    "Lesotho": "Lesotho",
    "Liberia": "Liberia",
    "Libia": "Libya",
    "Madagaskar": "Madagascar",
    "Malawi": "Malawi",
    "Mali": "Mali",
    "Mauretania": "Mauritania",
    "Mauritius": "Mauritius",
    "Maroko": "Morocco",
    "Mozambik": "Mozambique",
    "Namibia": "Namibia",
    "Niger": "Niger",
    "Nigeria": "Nigeria",
    "Rwanda": "Rwanda",
    "Wyspy Świętego Tomasza i Książęca": "São Tomé and Príncipe",
    "Senegal": "Senegal",
    "Seszele": "Seychelles",
    "Sierra Leone": "Sierra Leone",
    "Somalia": "Somalia",
    "RPA": "South Africa",
    "Republika Południowej Afryki": "South Africa",
    "Sudan Południowy": "South Sudan",
    "Sudan": "Sudan",
    "Tanzania": "Tanzania",
    "Togo": "Togo",
    "Tunezja": "Tunisia",
    "Uganda": "Uganda",
    "Zambia": "Zambia",
    "Zimbabwe": "Zimbabwe",

    # AFC
    "Afganistan": "Afghanistan",
    "Australia": "Australia",
    "Bahrajn": "Bahrain",
    "Bangladesz": "Bangladesh",
    "Bhutan": "Bhutan",
    "Brunei": "Brunei Darussalam",
    "Kambodża": "Cambodia",
    "Chiny": "China PR",
    "Chińskie Tajpej": "Chinese Taipei",
    "Tajwan": "Chinese Taipei",
    "Korea Północna": "DPR Korea",
    "Guam": "Guam",
    "Hongkong": "Hong Kong",
    "Indie": "India",
    "Indonezja": "Indonesia",
    "Iran": "Iran",
    "Irak": "Iraq",
    "Japonia": "Japan",
    "Jordania": "Jordan",
    "Kuwejt": "Kuwait",
    "Kirgistan": "Kyrgyz Republic",
    "Laos": "Laos",
    "Liban": "Lebanon",
    "Makau": "Macau",
    "Malezja": "Malaysia",
    "Malediwy": "Maldives",
    "Mongolia": "Mongolia",
    "Mjanma": "Myanmar",
    "Birma": "Myanmar",
    "Nepal": "Nepal",
    "Oman": "Oman",
    "Pakistan": "Pakistan",
    "Palestyna": "Palestine",
    "Filipiny": "Philippines",
    "Katar": "Qatar",
    "Korea Południowa": "Republic of Korea",
    "Korea Płd.": "Republic of Korea",
    "Arabia Saudyjska": "Saudi Arabia",
    "Singapur": "Singapore",
    "Sri Lanka": "Sri Lanka",
    "Syria": "Syria",
    "Tadżykistan": "Tajikistan",
    "Tajlandia": "Thailand",
    "Timor Wschodni": "Timor-Leste",
    "Turkmenistan": "Turkmenistan",
    "Zjednoczone Emiraty Arabskie": "United Arab Emirates",
    "ZEA": "United Arab Emirates",
    "Uzbekistan": "Uzbekistan",
    "Wietnam": "Vietnam",
    "Jemen": "Yemen",

    # OFC
    "Samoa Amerykańskie": "American Samoa",
    "Wyspy Kuka": "Cook Islands",
    "Fidżi": "Fiji",
    "Nowa Kaledonia": "New Caledonia",
    "Nowa Zelandia": "New Zealand",
    "Papua-Nowa Gwinea": "Papua New Guinea",
    "Samoa": "Samoa",
    "Wyspy Salomona": "Solomon Islands",
    "Tahiti": "Tahiti",
    "Tonga": "Tonga",
    "Vanuatu": "Vanuatu",
}

def map_position(pos_str: str) -> str:
    cleaned = pos_str.strip().upper()
    return SOFIFA_POSITION_MAP.get(cleaned, "CENTRAL_MIDFIELDER")

def fetch_team_id_map(max_pages: int = 15) -> dict[str, int]:
    """
    Fetches team list pages to resolve team_name -> sofifa_id on the fly.
    """
    name_to_id = {}
    print("Resolving SoFIFA team IDs for player scraping...")
    for page in range(max_pages):
        url = f"https://sofifa.com/teams?type=club&offset={page * 60}"
        html = fetch_html(url)
        if not html:
            break
        soup = BeautifulSoup(html, "html.parser")
        links = soup.select('a[href^="/team/"]')
        if not links:
            break
        for link in links:
            href = link.get("href", "")
            match = re.search(r"/team/(\d+)/", href)
            if match:
                name = link.get_text(strip=True)
                name_to_id[name] = int(match.group(1))
    return name_to_id

def get_col_int(row, col_name: str) -> Optional[int]:
    td = row.select_one(f'td[data-col="{col_name}"]')
    if td:
        text = td.get_text(strip=True)
        if text.isdigit():
            return int(text)
    return None

def parse_players_from_table(html: str, team_name: Optional[str] = None) -> list[dict]:
    """
    Parses player rows from a SoFIFA squad table.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody tr")
    players = []

    for row in rows:
        player_link = row.select_one('a[href^="/player/"]')
        if not player_link:
            continue

        short_name = player_link.get_text(strip=True)
        full_name = player_link.get("data-tippy-content") or player_link.get("title") or short_name

        # Position
        pos_element = row.select_one("span.pos")
        pos_code = pos_element.get_text(strip=True) if pos_element else "CM"
        position_enum_str = map_position(pos_code)

        # Age
        age = get_col_int(row, "ae")

        # Height (in cm)
        hi_td = row.select_one('td[data-col="hi"]')
        height = 180
        if hi_td:
            hi_match = re.search(r"(\d+)cm", hi_td.get_text(strip=True))
            if hi_match:
                height = int(hi_match.group(1))

        # Overall & Potential ratings
        overall = get_col_int(row, "oa") or 70
        potential = get_col_int(row, "pt") or overall

        # Scraped detailed attributes
        pac_val = get_col_int(row, "pac")
        sho_val = get_col_int(row, "sho")
        pas_val = get_col_int(row, "pas")
        dri_val = get_col_int(row, "dri")
        def_val = get_col_int(row, "def")
        phy_val = get_col_int(row, "phy")
        he_val  = get_col_int(row, "he")

        gd_val  = get_col_int(row, "gd")
        gh_val  = get_col_int(row, "gh")
        gk_val  = get_col_int(row, "gk")
        gr_val  = get_col_int(row, "gr")
        gp_val  = get_col_int(row, "gp")

        # Nationality / Country
        nationality = "Unknown"
        na_link = row.select_one('a[href*="/players?na="]')
        if na_link:
            na_img = na_link.select_one("img")
            if na_img and na_img.get("title"):
                nationality = na_img.get("title").strip()
            elif na_link.get("title"):
                nationality = na_link.get("title").strip()

        nationality = SOFIFA_NATIONALITY_MAP.get(nationality, nationality)

        # Team name
        row_team_name = team_name
        if not row_team_name:
            team_link = row.select_one('a[href^="/team/"]')
            if team_link:
                row_team_name = team_link.get_text(strip=True)

        player_dict = {
            "short_name": short_name,
            "full_name": full_name,
            "position": position_enum_str,
            "age": age or 24,
            "nationality": nationality,
            "height": height,
            "overall": overall,
            "potential": potential,
            "team_name": row_team_name or "Free Agent",
        }

        if position_enum_str == "GOALKEEPER":
            player_dict.update({
                "diving": gd_val if gd_val is not None else overall,
                "handling": gh_val if gh_val is not None else max(40, overall - 2),
                "kicking": gk_val if gk_val is not None else (pas_val if pas_val is not None else max(40, overall - 5)),
                "reflexes": gr_val if gr_val is not None else overall,
                "speed": def_val if def_val is not None else max(30, overall - 20),
                "positioning": gp_val if gp_val is not None else max(40, overall - 1),
            })
        elif position_enum_str in ("STRIKER", "CENTRAL_FORWARD", "LEFT_WING", "RIGHT_WING"):
            is_cf = position_enum_str in ("STRIKER", "CENTRAL_FORWARD")
            player_dict.update({
                "pace": pac_val if pac_val is not None else max(45, min(99, overall + 3)),
                "shooting": sho_val if sho_val is not None else max(45, min(99, overall + 5)),
                "passing": pas_val if pas_val is not None else max(35, min(99, overall - 8)),
                "dribbling": dri_val if dri_val is not None else max(45, min(99, overall + 2)),
                "defending": def_val if def_val is not None else max(15, min(50, overall - 35)),
                "physical": phy_val if phy_val is not None else max(40, min(99, overall - 5)),
                "heading": he_val if he_val is not None else max(35, min(99, overall + 2 if is_cf else overall - 5)),
            })
        elif position_enum_str in ("CENTRE_BACK", "LEFT_BACK", "RIGHT_BACK", "LEFT_WING_BACK", "RIGHT_WING_BACK"):
            is_cb = position_enum_str == "CENTRE_BACK"
            player_dict.update({
                "pace": pac_val if pac_val is not None else max(40, min(99, overall - 10 if is_cb else overall - 2)),
                "shooting": sho_val if sho_val is not None else max(15, min(45, overall - 35)),
                "passing": pas_val if pas_val is not None else max(35, min(99, overall - 12)),
                "dribbling": dri_val if dri_val is not None else max(30, min(99, overall - 18)),
                "defending": def_val if def_val is not None else max(50, min(99, overall + 6)),
                "physical": phy_val if phy_val is not None else max(50, min(99, overall + 4)),
                "heading": he_val if he_val is not None else max(45, min(99, overall + 4 if is_cb else overall - 5)),
            })
        else:  # Midfielders
            is_cam = position_enum_str == "CENTRAL_ATTACKING_MIDFIELDER"
            is_cdm = position_enum_str == "CENTRAL_DEFENSIVE_MIDFIELDER"
            player_dict.update({
                "pace": pac_val if pac_val is not None else max(40, min(99, overall - 2)),
                "shooting": sho_val if sho_val is not None else max(30, min(99, overall + 2 if is_cam else overall - 12)),
                "passing": pas_val if pas_val is not None else max(45, min(99, overall + 5)),
                "dribbling": dri_val if dri_val is not None else max(45, min(99, overall + 2)),
                "defending": def_val if def_val is not None else max(25, min(99, overall + 5 if is_cdm else overall - 15)),
                "physical": phy_val if phy_val is not None else max(40, min(99, overall - 4)),
                "heading": he_val if he_val is not None else max(30, min(99, overall - 15)),
            })

        players.append(player_dict)

    return players


def scrape_players_for_teams(teams_file: str = "data/teams.json", output_file: str = "data/players.json", max_teams: Optional[int] = None) -> list[dict]:
    """
    Reads teams from teams.json and scrapes squad players for each team.
    """
    if not os.path.exists(teams_file):
        raise FileNotFoundError(f"Teams file '{teams_file}' does not exist. Run teams scraper first.")

    with open(teams_file, "r", encoding="utf-8") as f:
        teams = json.load(f)

    if max_teams is not None:
        teams = teams[:max_teams]

    team_id_map = {}
    all_players = []
    print(f"Scraping players for {len(teams)} team(s)...")

    for idx, team in enumerate(teams, start=1):
        team_name = team["name"]
        team_id = team.get("sofifa_id")

        if not team_id:
            if not team_id_map:
                team_id_map = fetch_team_id_map()
            team_id = team_id_map.get(team_name)

        if not team_id:
            print(f"[{idx}/{len(teams)}] Could not resolve SoFIFA ID for team '{team_name}', skipping.")
            continue

        url = f"https://sofifa.com/team/{team_id}/?showCol%5B%5D=hi&showCol%5B%5D=he&showCol%5B%5D=pac&showCol%5B%5D=sho&showCol%5B%5D=pas&showCol%5B%5D=dri&showCol%5B%5D=def&showCol%5B%5D=phy&showCol%5B%5D=gd&showCol%5B%5D=gh&showCol%5B%5D=gk&showCol%5B%5D=gr&showCol%5B%5D=gp"
        print(f"[{idx}/{len(teams)}] Fetching squad for {team_name} (ID: {team_id})...")

        html = fetch_html(url)
        if not html:
            print(f"Skipping {team_name} due to fetch error.")
            continue

        # Preserve existing formation from teams.json (scraped directly from SoFIFA)
        formation = team.get("formation")
        if not formation:
            formation = detect_formation_from_squad_html(html) if html else "4-3-3"
            team["formation"] = formation
        print(f"  Team {team_name} formation: {team.get('formation', formation)}")

        players = parse_players_from_table(html, team_name=team_name)
        print(f"  Found {len(players)} players for {team_name}.")
        all_players.extend(players)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_players, f, ensure_ascii=False, indent=2)

    # Re-save updated teams with formations
    if os.path.exists(teams_file):
        with open(teams_file, "w", encoding="utf-8") as f:
            json.dump(teams, f, ensure_ascii=False, indent=2)
        print(f"Updated {teams_file} with detected team formations.")

    print(f"Successfully saved {len(all_players)} players to {output_file}")
    return all_players


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    scrape_players_for_teams(teams_file="data/teams.json", output_file="data/players.json", max_teams=3)
