import json
import os
import re
from typing import Optional
from bs4 import BeautifulSoup
from scrapper.fetcher import fetch_html

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
        age_td = row.select_one('td[data-col="ae"]')
        age = None
        if age_td and age_td.get_text(strip=True).isdigit():
            age = int(age_td.get_text(strip=True))

        # Height (in cm)
        hi_td = row.select_one('td[data-col="hi"]')
        height = 180
        if hi_td:
            hi_match = re.search(r"(\d+)cm", hi_td.get_text(strip=True))
            if hi_match:
                height = int(hi_match.group(1))

        # Overall rating
        oa_td = row.select_one('td[data-col="oa"]')
        overall = int(oa_td.get_text(strip=True)) if oa_td and oa_td.get_text(strip=True).isdigit() else 70

        # Potential rating
        pt_td = row.select_one('td[data-col="pt"]')
        potential = int(pt_td.get_text(strip=True)) if pt_td and pt_td.get_text(strip=True).isdigit() else overall

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
            "height": height,
            "overall": overall,
            "potential": potential,
            "team_name": row_team_name or "Free Agent",
        }

        # Add position-specific default attributes proportional to overall rating
        if position_enum_str == "GOALKEEPER":
            player_dict.update({
                "diving": overall,
                "handling": max(40, overall - 2),
                "kicking": max(40, overall - 5),
                "reflexes": overall,
                "speed": max(30, overall - 20),
                "positioning": max(40, overall - 1),
            })
        else:
            player_dict.update({
                "pace": max(40, overall - 5),
                "shooting": max(40, overall - 8),
                "passing": max(40, overall - 3),
                "dribbling": max(40, overall - 4),
                "defending": max(40, overall - 10),
                "physical": max(40, overall - 6),
                "heading": max(40, overall - 7),
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

        url = f"https://sofifa.com/team/{team_id}/?showCol%5B%5D=hi"
        print(f"[{idx}/{len(teams)}] Fetching squad for {team_name} (ID: {team_id})...")

        html = fetch_html(url)
        if not html:
            print(f"Skipping {team_name} due to fetch error.")
            continue

        players = parse_players_from_table(html, team_name=team_name)
        print(f"  Found {len(players)} players for {team_name}.")
        all_players.extend(players)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_players, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved {len(all_players)} players to {output_file}")
    return all_players


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    scrape_players_for_teams(teams_file="data/teams.json", output_file="data/players.json", max_teams=3)
