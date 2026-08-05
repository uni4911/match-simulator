import argparse
import json
import os
import re
from typing import Optional
from bs4 import BeautifulSoup
from scrapper.fetcher import fetch_html

BASE_URL = "https://sofifa.com/teams"

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

        oa_td = row.select_one('td[data-col="oa"]')
        at_td = row.select_one('td[data-col="at"]')
        md_td = row.select_one('td[data-col="md"]')
        df_td = row.select_one('td[data-col="df"]')

        overall = int(oa_td.get_text(strip=True)) if oa_td and oa_td.get_text(strip=True).isdigit() else None
        attack = int(at_td.get_text(strip=True)) if at_td and at_td.get_text(strip=True).isdigit() else None
        midfield = int(md_td.get_text(strip=True)) if md_td and md_td.get_text(strip=True).isdigit() else None
        defense = int(df_td.get_text(strip=True)) if df_td and df_td.get_text(strip=True).isdigit() else None

        teams.append({
            "sofifa_id": sofifa_id,
            "name": name,
            "league": league_name,
            "overall": overall,
            "attack": attack,
            "midfield": midfield,
            "defense": defense
        })

    return teams

def determine_formation_from_positions(starting_positions: list[str]) -> str:
    """
    Determines formation from a list of starting player position badges.
    """
    field_pos = [p for p in starting_positions if p != "GK"]
    def_count = sum(1 for p in field_pos if p in ["LB", "LO", "CB", "ŚO", "RB", "PO", "LWB", "CLO", "RWB", "CPO"])
    mid_count = sum(1 for p in field_pos if p in ["CDM", "ŚPD", "CM", "ŚP", "CAM", "ŚPO", "LM", "LP", "RM", "PP"])
    att_count = sum(1 for p in field_pos if p in ["LW", "LS", "CF", "ŚN", "RW", "PS", "ST", "N"])

    cdm_count = sum(1 for p in field_pos if p in ["CDM", "ŚPD"])
    cam_count = sum(1 for p in field_pos if p in ["CAM", "ŚPO"])
    winger_count = sum(1 for p in field_pos if p in ["LW", "LS", "RW", "PS"])
    wide_mid_count = sum(1 for p in field_pos if p in ["LM", "LP", "RM", "PP"])

    if def_count == 4 and mid_count == 3 and att_count == 3:
        return "4-3-3"
    elif def_count == 4 and mid_count == 4 and att_count == 2:
        if cam_count >= 1 and (cdm_count >= 1 or cdm_count + mid_count >= 3) and wide_mid_count >= 1:
            return "4-2-3-1"
        elif cdm_count == 1 and cam_count == 1:
            return "4-1-2-1-2"
        else:
            return "4-4-2"
    elif def_count == 3 and mid_count == 5 and att_count == 2:
        return "3-5-2"
    elif def_count == 5 and mid_count == 3 and att_count == 2:
        return "5-3-2"
    elif def_count == 3 and mid_count == 4 and att_count == 3:
        return "3-4-3"
    elif def_count == 4 and (cdm_count >= 1 or cam_count >= 1):
        if att_count == 1 or (att_count == 2 and winger_count == 0):
            return "4-2-3-1"
        return "4-3-3"
    else:
        if def_count == 3:
            return "3-5-2" if att_count <= 2 else "3-4-3"
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
        "overall": team["overall"],
        "attack": team["attack"],
        "midfield": team["midfield"],
        "defense": team["defense"],
        "formation": team.get("formation", "4-3-3")
    }

def scrape_teams(max_pages: Optional[int] = None, output_file: str = "data/teams.json") -> list[dict]:
  
    all_teams = []
    page = 0
    pages_limit_str = f"up to {max_pages} page(s)" if max_pages is not None else "all available pages"
    print(f"Starting to scrape {pages_limit_str} of teams from SoFIFA...")

    while True:
        if max_pages is not None and page >= max_pages:
            print(f"Reached max pages limit ({max_pages}). Stopping pagination.")
            break

        offset = page * 60
        url = f"{BASE_URL}?type=club&offset={offset}"
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

    # Clean teams for JSON storage
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
