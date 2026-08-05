import argparse
from scrapper.teams import scrape_teams
from scrapper.players import scrape_players_for_teams

def main():
    parser = argparse.ArgumentParser(description="SoFIFA Teams & Players Scraper")
    parser.add_argument("--teams-pages", type=int, default=None, help="Number of team list pages to scrape (60 teams/page; default: all pages)")
    parser.add_argument("--max-teams", type=int, default=None, help="Limit number of teams to scrape players for (default: all teams in teams.json)")
    parser.add_argument("--teams-out", type=str, default="data/teams.json", help="Output path for teams JSON")
    parser.add_argument("--players-out", type=str, default="data/players.json", help="Output path for players JSON")

    args = parser.parse_args()

    print("=== Step 1: Scraping Teams ===")
    scrape_teams(max_pages=args.teams_pages, output_file=args.teams_out)

    print("\n=== Step 2: Scraping Squad Players ===")
    scrape_players_for_teams(teams_file=args.teams_out, output_file=args.players_out, max_teams=args.max_teams)

    print("\n=== All Scrapes Completed Successfully! ===")

if __name__ == "__main__":
    main()
