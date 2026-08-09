import argparse
import json
import os
import re
from typing import Optional
from bs4 import BeautifulSoup
from scrapper.fetcher import fetch_html

BASE_URL = "https://sofifa.com/teams"

SOFIFA_FORMATION_NAME_MAP = {
    "4-3-3 Flat": "4-3-3",
    "4-2-3-1 Wide": "4-2-3-1",
    "4-4-2 Flat": "4-4-2",
    "4-5-1 Flat": "4-5-1",
    "3-4-3 Flat": "3-4-3",
    "5-4-1 Flat": "5-4-1",
    "4-4-1-1 Midfield": "4-4-1-1",
    "4-1-2-1-2 Narrow": "4-1-2-1-2",
}

def normalize_sofifa_formation(raw: str) -> str:
    """
    Normalizes SoFIFA tactical formation names into standard domain formation names.
    """
    cleaned = raw.strip()
    if not cleaned:
        return "4-3-3"
    return SOFIFA_FORMATION_NAME_MAP.get(cleaned, cleaned)

def parse_teams_page(html: str) -> list[dict]:
    """
    Parses a single page of SoFIFA teams table and returns a list of team dicts (with in-memory sofifa_id).
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody tr")
    teams = []

    for row in rows:
        team_link = row.select_one('a[href^="/team/"]')
        if not team_link:
            continue

        href = team_link.get("href", "")
        id_match = re.search(r"/team/(\d+)/", href)
        sofifa_id = int(id_match.group(1)) if id_match else None
        name = team_link.get_text(strip=True)

        league_link = row.select_one('a[href^="/league/"]')
        league_name = league_link.get_text(strip=True) if league_link else ""

        flag_img = row.select_one('img.flag')
        raw_country = flag_img.get("title", "") if flag_img else ""
        from scrapper.players import SOFIFA_NATIONALITY_MAP
        country = SOFIFA_NATIONALITY_MAP.get(raw_country, raw_country)

        if league_name and country:
            full_league_name = f"{league_name} ({country})"
        else:
            full_league_name = league_name

        oa_td = row.select_one('td[data-col="oa"]')
        at_td = row.select_one('td[data-col="at"]')
        md_td = row.select_one('td[data-col="md"]')
        df_td = row.select_one('td[data-col="df"]')
        fm_td = row.select_one('td[data-col="fm"]')

        overall = int(oa_td.get_text(strip=True)) if oa_td and oa_td.get_text(strip=True).isdigit() else None
        attack = int(at_td.get_text(strip=True)) if at_td and at_td.get_text(strip=True).isdigit() else None
        midfield = int(md_td.get_text(strip=True)) if md_td and md_td.get_text(strip=True).isdigit() else None
        defense = int(df_td.get_text(strip=True)) if df_td and df_td.get_text(strip=True).isdigit() else None
        
        raw_formation = fm_td.get_text(strip=True) if fm_td else ""
        formation = normalize_sofifa_formation(raw_formation) if raw_formation else "4-3-3"

        teams.append({
            "sofifa_id": sofifa_id,
            "name": name,
            "league": full_league_name,
            "raw_league": league_name,
            "country": country,
            "overall": overall,
            "attack": attack,
            "midfield": midfield,
            "defense": defense,
            "formation": formation
        })

    return teams

POSITION_STANDARD_MAP = {
    "GK": "GK", "BR": "GK", "GOALKEEPER": "GK",
    "LB": "LB", "LO": "LB", "LEFT_BACK": "LB",
    "CB": "CB", "ŚO": "CB", "LŚO": "CB", "PŚO": "CB", "LCB": "CB", "RCB": "CB", "CENTRE_BACK": "CB",
    "RB": "RB", "PO": "RB", "RIGHT_BACK": "RB",
    "LWB": "LWB", "CLO": "LWB", "LEFT_WING_BACK": "LWB",
    "RWB": "RWB", "CPO": "RWB", "RIGHT_WING_BACK": "RWB",
    "CDM": "CDM", "ŚPD": "CDM", "LDP": "CDM", "PDP": "CDM", "LDM": "CDM", "RDM": "CDM", "CENTRAL_DEFENSIVE_MIDFIELDER": "CDM",
    "CM": "CM", "ŚP": "CM", "LCM": "CM", "RCM": "CM", "LŚP": "CM", "PŚP": "CM", "CENTRAL_MIDFIELDER": "CM",
    "CAM": "CAM", "ŚPO": "CAM", "LAM": "CAM", "RAM": "CAM", "CENTRAL_ATTACKING_MIDFIELDER": "CAM",
    "LM": "LM", "LP": "LM", "LEFT_MIDFIELDER": "LM",
    "RM": "RM", "PP": "RM", "RIGHT_MIDFIELDER": "RM",
    "LW": "LW", "LS": "LW", "LEFT_WING": "LW",
    "RW": "RW", "PS": "RW", "RIGHT_WING": "RW",
    "CF": "CF", "ŚN": "CF", "LF": "CF", "RF": "CF", "CENTRAL_FORWARD": "CF",
    "ST": "ST", "N": "ST", "STRIKER": "ST"
}

def determine_formation_from_positions(starting_positions: list[str]) -> str:
    """
    Determines formation from a list of starting player position badges,
    differentiating 4-3-3 types (Narrow, Holding, Attack, Defend, False 9, Flat)
    as well as other common tactical formations.
    """
    std_positions = []
    for p in starting_positions:
        norm = POSITION_STANDARD_MAP.get(p.upper(), "")
        if not norm:
            p_upper = p.upper()
            if "GK" in p_upper or "BR" in p_upper: norm = "GK"
            elif "CB" in p_upper or "ŚO" in p_upper: norm = "CB"
            elif "LB" in p_upper or "LO" in p_upper: norm = "LB"
            elif "RB" in p_upper or "PO" in p_upper: norm = "RB"
            elif "CDM" in p_upper or "SPD" in p_upper or "DP" in p_upper: norm = "CDM"
            elif "CAM" in p_upper or "SPO" in p_upper: norm = "CAM"
            elif "CM" in p_upper or "SP" in p_upper: norm = "CM"
            elif "LM" in p_upper or "LP" in p_upper: norm = "LM"
            elif "RM" in p_upper or "PP" in p_upper: norm = "RM"
            elif "LW" in p_upper or "LS" in p_upper: norm = "LW"
            elif "RW" in p_upper or "PS" in p_upper: norm = "RW"
            elif "CF" in p_upper or "SN" in p_upper: norm = "CF"
            elif "ST" in p_upper or "N" in p_upper: norm = "ST"
            else: norm = "CM"
        if norm != "GK":
            std_positions.append(norm)

    def_count = sum(1 for p in std_positions if p in ["LB", "CB", "RB", "LWB", "RWB"])
    mid_count = sum(1 for p in std_positions if p in ["CDM", "CM", "CAM", "LM", "RM"])
    att_count = sum(1 for p in std_positions if p in ["LW", "RW", "CF", "ST"])

    cdm_count = std_positions.count("CDM")
    cm_count = std_positions.count("CM")
    cam_count = std_positions.count("CAM")
    wide_mid_count = std_positions.count("LM") + std_positions.count("RM")
    winger_count = std_positions.count("LW") + std_positions.count("RW")
    cf_count = std_positions.count("CF")
    st_count = std_positions.count("ST")
    strikers_total = cf_count + st_count

    # 4 Defenders
    if def_count == 4:
        if (mid_count == 3 and att_count == 3) or (mid_count >= 3 and winger_count >= 2):
            if winger_count == 0 and (cam_count >= 2 or (cam_count >= 1 and cf_count >= 1)):
                return "4-3-3 Narrow"
            elif cdm_count >= 2:
                return "4-3-3 Defend"
            elif cdm_count == 1 and cam_count == 0:
                if cf_count >= 1:
                    return "4-3-3 False 9"
                return "4-3-3 Holding"
            elif cam_count >= 1 and cdm_count == 0:
                return "4-3-3 Attack"
            elif cf_count >= 1 and cdm_count >= 1:
                return "4-3-3 False 9"
            else:
                return "4-3-3"
        elif winger_count == 0 and att_count >= 2 and (mid_count + cam_count >= 5):
            return "4-3-3 Narrow"
        elif mid_count == 4 and att_count == 2:
            if cdm_count >= 1 and cam_count >= 1 and wide_mid_count >= 1:
                return "4-1-2-1-2 Wide"
            elif cdm_count >= 1 and cam_count >= 1:
                return "4-1-2-1-2"
            elif cdm_count >= 1 and cam_count == 0 and wide_mid_count == 0:
                return "4-4-2 Diamond"
            else:
                return "4-4-2"
        elif mid_count == 5 and att_count == 1:
            if winger_count == 0 and cam_count >= 2:
                return "4-2-3-1 Narrow"
            elif cdm_count == 1 and wide_mid_count >= 2:
                return "4-1-4-1"
            elif cm_count >= 3 and wide_mid_count >= 2:
                return "4-5-1"
            else:
                return "4-2-3-1"
        elif mid_count == 4 and strikers_total == 2 and winger_count == 0:
            return "4-3-1-2"
        elif mid_count == 2 and att_count == 4:
            return "4-2-4"
        else:
            if att_count >= 3:
                return "4-3-3 Narrow" if winger_count == 0 else "4-3-3"
            elif att_count == 2:
                return "4-4-2"
            else:
                return "4-2-3-1"

    # 3 Defenders
    elif def_count == 3:
        if mid_count == 5 and att_count == 2:
            if cam_count >= 1 and wide_mid_count >= 2:
                return "3-4-1-2"
            return "3-5-2"
        elif mid_count == 4 and att_count == 3:
            if cam_count >= 2 or cf_count >= 2:
                return "3-4-2-1"
            return "3-4-3"
        elif att_count >= 3:
            return "3-4-3"
        else:
            return "3-5-2"

    # 5 Defenders
    elif def_count == 5:
        if mid_count == 4 and att_count == 1:
            return "5-4-1"
        elif mid_count == 2 and att_count == 3:
            return "5-2-3"
        else:
            return "5-3-2"

    # Default fallback
    else:
        if def_count == 3:
            return "3-5-2"
        elif def_count == 5:
            return "5-3-2"
        elif att_count >= 3:
            return "4-3-3"
        else:
            return "4-4-2"

def detect_formation_from_squad_html(html: str) -> str:
    """
    Parses squad HTML table to get starting 11 positions and returns formation string.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody tr")
    starting_positions = []
    for r in rows[:11]:
        pos_span = r.select_one("td.pos span, span.pos, a.pos, td[data-col='pos'] span, .pos")
        pos_text = pos_span.get_text(strip=True) if pos_span else "CM"
        starting_positions.append(pos_text)
    return determine_formation_from_positions(starting_positions)

def clean_team_for_export(team: dict) -> dict:
    """
    Removes internal scraper IDs and metadata (sofifa_id, league_id, squad_size).
    """
    return {
        "name": team["name"],
        "league": team["league"],
        "country": team.get("country", ""),
        "overall": team["overall"],
        "attack": team["attack"],
        "midfield": team["midfield"],
        "defense": team["defense"],
        "formation": team.get("formation", "4-3-3")
    }

def scrape_teams(max_pages: Optional[int] = None, output_file: str = "data/teams.json", fetch_formations: bool = True) -> list[dict]:
    all_teams = []
    page = 0
    pages_limit_str = f"up to {max_pages} page(s)" if max_pages is not None else "all available pages"
    print(f"Starting to scrape {pages_limit_str} of teams from SoFIFA (with formations)...")

    while True:
        if max_pages is not None and page >= max_pages:
            print(f"Reached max pages limit ({max_pages}). Stopping pagination.")
            break

        offset = page * 60
        url = f"{BASE_URL}?type=club&showCol%5B%5D=ti&showCol%5B%5D=oa&showCol%5B%5D=at&showCol%5B%5D=md&showCol%5B%5D=df&showCol%5B%5D=fm&offset={offset}&hl=en-US"
        print(f"Fetching page {page + 1}: {url}")
        html = fetch_html(url)
        if not html:
            print(f"Failed to fetch page {page + 1}, stopping.")
            break

        teams = parse_teams_page(html)
        if not teams:
            print(f"No teams found on page {page + 1}. Reached end of list.")
            break

        print(f"Page {page + 1}: found {len(teams)} teams.")
        all_teams.extend(teams)
        page += 1

    clean_teams = [clean_team_for_export(t) for t in all_teams]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clean_teams, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved {len(clean_teams)} clean teams to {output_file}")
    return all_teams

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="SoFIFA Teams Scraper")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum number of pages to scrape (default: all pages)")
    parser.add_argument("--out", type=str, default="data/teams.json", help="Output file path")
    args = parser.parse_args()

    scrape_teams(max_pages=args.max_pages, output_file=args.out)

