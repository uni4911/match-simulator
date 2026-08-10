import json
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, joinedload
from src.db.database import (
    SessionLocal,
    ConfederationModel,
    CountryModel,
    LeagueModel,
    TeamModel,
    PlayerModel,
    PlayerStatsModel,
    GoalkeeperStatsModel,
)

CONFEDERATIONS_DATA = [
    {"name": "Union of European Football Associations", "code": "UEFA"},
    {"name": "Confederación Sudamericana de Fútbol", "code": "CONMEBOL"},
    {"name": "Confederation of North, Central America and Caribbean Association Football", "code": "CONCACAF"},
    {"name": "Confederation of African Football", "code": "CAF"},
    {"name": "Asian Football Confederation", "code": "AFC"},
    {"name": "Oceania Football Confederation", "code": "OFC"},
]

COUNTRIES_DATA = [

    {"name": "Albania", "code": "ALB", "confederation": "UEFA"},
    {"name": "Andorra", "code": "AND", "confederation": "UEFA"},
    {"name": "Armenia", "code": "ARM", "confederation": "UEFA"},
    {"name": "Austria", "code": "AUT", "confederation": "UEFA"},
    {"name": "Azerbaijan", "code": "AZE", "confederation": "UEFA"},
    {"name": "Belarus", "code": "BLR", "confederation": "UEFA"},
    {"name": "Belgium", "code": "BEL", "confederation": "UEFA"},
    {"name": "Bosnia and Herzegovina", "code": "BIH", "confederation": "UEFA"},
    {"name": "Bulgaria", "code": "BUL", "confederation": "UEFA"},
    {"name": "Croatia", "code": "CRO", "confederation": "UEFA"},
    {"name": "Cyprus", "code": "CYP", "confederation": "UEFA"},
    {"name": "Czechia", "code": "CZE", "confederation": "UEFA"},
    {"name": "Denmark", "code": "DEN", "confederation": "UEFA"},
    {"name": "England", "code": "ENG", "confederation": "UEFA"},
    {"name": "Estonia", "code": "EST", "confederation": "UEFA"},
    {"name": "Faroe Islands", "code": "FRO", "confederation": "UEFA"},
    {"name": "Finland", "code": "FIN", "confederation": "UEFA"},
    {"name": "France", "code": "FRA", "confederation": "UEFA"},
    {"name": "Georgia", "code": "GEO", "confederation": "UEFA"},
    {"name": "Germany", "code": "GER", "confederation": "UEFA"},
    {"name": "Gibraltar", "code": "GIB", "confederation": "UEFA"},
    {"name": "Greece", "code": "GRE", "confederation": "UEFA"},
    {"name": "Hungary", "code": "HUN", "confederation": "UEFA"},
    {"name": "Iceland", "code": "ISL", "confederation": "UEFA"},
    {"name": "Israel", "code": "ISR", "confederation": "UEFA"},
    {"name": "Italy", "code": "ITA", "confederation": "UEFA"},
    {"name": "Kazakhstan", "code": "KAZ", "confederation": "UEFA"},
    {"name": "Kosovo", "code": "KOS", "confederation": "UEFA"},
    {"name": "Latvia", "code": "LVA", "confederation": "UEFA"},
    {"name": "Liechtenstein", "code": "LIE", "confederation": "UEFA"},
    {"name": "Lithuania", "code": "LTU", "confederation": "UEFA"},
    {"name": "Luxembourg", "code": "LUX", "confederation": "UEFA"},
    {"name": "Malta", "code": "MLT", "confederation": "UEFA"},
    {"name": "Moldova", "code": "MDA", "confederation": "UEFA"},
    {"name": "Montenegro", "code": "MNE", "confederation": "UEFA"},
    {"name": "Netherlands", "code": "NED", "confederation": "UEFA"},
    {"name": "North Macedonia", "code": "MKD", "confederation": "UEFA"},
    {"name": "Northern Ireland", "code": "NIR", "confederation": "UEFA"},
    {"name": "Norway", "code": "NOR", "confederation": "UEFA"},
    {"name": "Poland", "code": "POL", "confederation": "UEFA"},
    {"name": "Portugal", "code": "POR", "confederation": "UEFA"},
    {"name": "Republic of Ireland", "code": "IRL", "confederation": "UEFA"},
    {"name": "Romania", "code": "ROU", "confederation": "UEFA"},
    {"name": "Russia", "code": "RUS", "confederation": "UEFA"},
    {"name": "San Marino", "code": "SMR", "confederation": "UEFA"},
    {"name": "Scotland", "code": "SCO", "confederation": "UEFA"},
    {"name": "Serbia", "code": "SRB", "confederation": "UEFA"},
    {"name": "Slovakia", "code": "SVK", "confederation": "UEFA"},
    {"name": "Slovenia", "code": "SVN", "confederation": "UEFA"},
    {"name": "Spain", "code": "ESP", "confederation": "UEFA"},
    {"name": "Sweden", "code": "SWE", "confederation": "UEFA"},
    {"name": "Switzerland", "code": "SUI", "confederation": "UEFA"},
    {"name": "Turkey", "code": "TUR", "confederation": "UEFA"},
    {"name": "Ukraine", "code": "UKR", "confederation": "UEFA"},
    {"name": "Wales", "code": "WAL", "confederation": "UEFA"},


    {"name": "Argentina", "code": "ARG", "confederation": "CONMEBOL"},
    {"name": "Bolivia", "code": "BOL", "confederation": "CONMEBOL"},
    {"name": "Brazil", "code": "BRA", "confederation": "CONMEBOL"},
    {"name": "Chile", "code": "CHI", "confederation": "CONMEBOL"},
    {"name": "Colombia", "code": "COL", "confederation": "CONMEBOL"},
    {"name": "Ecuador", "code": "ECU", "confederation": "CONMEBOL"},
    {"name": "Paraguay", "code": "PAR", "confederation": "CONMEBOL"},
    {"name": "Peru", "code": "PER", "confederation": "CONMEBOL"},
    {"name": "Uruguay", "code": "URU", "confederation": "CONMEBOL"},
    {"name": "Venezuela", "code": "VEN", "confederation": "CONMEBOL"},


    {"name": "Anguilla", "code": "AIA", "confederation": "CONCACAF"},
    {"name": "Antigua and Barbuda", "code": "ATG", "confederation": "CONCACAF"},
    {"name": "Aruba", "code": "ARU", "confederation": "CONCACAF"},
    {"name": "Bahamas", "code": "BAH", "confederation": "CONCACAF"},
    {"name": "Barbados", "code": "BRB", "confederation": "CONCACAF"},
    {"name": "Belize", "code": "BLZ", "confederation": "CONCACAF"},
    {"name": "Bermuda", "code": "BER", "confederation": "CONCACAF"},
    {"name": "British Virgin Islands", "code": "VGB", "confederation": "CONCACAF"},
    {"name": "Canada", "code": "CAN", "confederation": "CONCACAF"},
    {"name": "Cayman Islands", "code": "CAY", "confederation": "CONCACAF"},
    {"name": "Costa Rica", "code": "CRC", "confederation": "CONCACAF"},
    {"name": "Cuba", "code": "CUB", "confederation": "CONCACAF"},
    {"name": "Curaçao", "code": "CUW", "confederation": "CONCACAF"},
    {"name": "Dominica", "code": "DMA", "confederation": "CONCACAF"},
    {"name": "Dominican Republic", "code": "DOM", "confederation": "CONCACAF"},
    {"name": "El Salvador", "code": "SLV", "confederation": "CONCACAF"},
    {"name": "Grenada", "code": "GRN", "confederation": "CONCACAF"},
    {"name": "Guatemala", "code": "GUA", "confederation": "CONCACAF"},
    {"name": "Guyana", "code": "GUY", "confederation": "CONCACAF"},
    {"name": "Haiti", "code": "HAI", "confederation": "CONCACAF"},
    {"name": "Honduras", "code": "HON", "confederation": "CONCACAF"},
    {"name": "Jamaica", "code": "JAM", "confederation": "CONCACAF"},
    {"name": "Mexico", "code": "MEX", "confederation": "CONCACAF"},
    {"name": "Montserrat", "code": "MSR", "confederation": "CONCACAF"},
    {"name": "Nicaragua", "code": "NCA", "confederation": "CONCACAF"},
    {"name": "Panama", "code": "PAN", "confederation": "CONCACAF"},
    {"name": "Puerto Rico", "code": "PUR", "confederation": "CONCACAF"},
    {"name": "Saint Kitts and Nevis", "code": "SKN", "confederation": "CONCACAF"},
    {"name": "Saint Lucia", "code": "LCA", "confederation": "CONCACAF"},
    {"name": "Saint Vincent and the Grenadines", "code": "VIN", "confederation": "CONCACAF"},
    {"name": "Suriname", "code": "SUR", "confederation": "CONCACAF"},
    {"name": "Trinidad and Tobago", "code": "TRI", "confederation": "CONCACAF"},
    {"name": "Turks and Caicos Islands", "code": "TCA", "confederation": "CONCACAF"},
    {"name": "United States", "code": "USA", "confederation": "CONCACAF"},
    {"name": "US Virgin Islands", "code": "VIR", "confederation": "CONCACAF"},

    {"name": "Algeria", "code": "ALG", "confederation": "CAF"},
    {"name": "Angola", "code": "ANG", "confederation": "CAF"},
    {"name": "Benin", "code": "BEN", "confederation": "CAF"},
    {"name": "Botswana", "code": "BOT", "confederation": "CAF"},
    {"name": "Burkina Faso", "code": "BFA", "confederation": "CAF"},
    {"name": "Burundi", "code": "BDI", "confederation": "CAF"},
    {"name": "Cabo Verde", "code": "CPV", "confederation": "CAF"},
    {"name": "Cameroon", "code": "CMR", "confederation": "CAF"},
    {"name": "Central African Republic", "code": "CTA", "confederation": "CAF"},
    {"name": "Chad", "code": "CHA", "confederation": "CAF"},
    {"name": "Comoros", "code": "COM", "confederation": "CAF"},
    {"name": "Congo", "code": "CGO", "confederation": "CAF"},
    {"name": "Congo DR", "code": "COD", "confederation": "CAF"},
    {"name": "Côte d'Ivoire", "code": "CIV", "confederation": "CAF"},
    {"name": "Djibouti", "code": "DJI", "confederation": "CAF"},
    {"name": "Egypt", "code": "EGY", "confederation": "CAF"},
    {"name": "Equatorial Guinea", "code": "EQG", "confederation": "CAF"},
    {"name": "Eritrea", "code": "ERI", "confederation": "CAF"},
    {"name": "Eswatini", "code": "SWZ", "confederation": "CAF"},
    {"name": "Ethiopia", "code": "ETH", "confederation": "CAF"},
    {"name": "Gabon", "code": "GAB", "confederation": "CAF"},
    {"name": "Gambia", "code": "GAM", "confederation": "CAF"},
    {"name": "Ghana", "code": "GHA", "confederation": "CAF"},
    {"name": "Guinea", "code": "GUI", "confederation": "CAF"},
    {"name": "Guinea-Bissau", "code": "GNB", "confederation": "CAF"},
    {"name": "Kenya", "code": "KEN", "confederation": "CAF"},
    {"name": "Lesotho", "code": "LES", "confederation": "CAF"},
    {"name": "Liberia", "code": "LBR", "confederation": "CAF"},
    {"name": "Libya", "code": "LBY", "confederation": "CAF"},
    {"name": "Madagascar", "code": "MAD", "confederation": "CAF"},
    {"name": "Malawi", "code": "MWI", "confederation": "CAF"},
    {"name": "Mali", "code": "MLI", "confederation": "CAF"},
    {"name": "Mauritania", "code": "MTN", "confederation": "CAF"},
    {"name": "Mauritius", "code": "MRI", "confederation": "CAF"},
    {"name": "Morocco", "code": "MAR", "confederation": "CAF"},
    {"name": "Mozambique", "code": "MOZ", "confederation": "CAF"},
    {"name": "Namibia", "code": "NAM", "confederation": "CAF"},
    {"name": "Niger", "code": "NIG", "confederation": "CAF"},
    {"name": "Nigeria", "code": "NGA", "confederation": "CAF"},
    {"name": "Rwanda", "code": "RWA", "confederation": "CAF"},
    {"name": "São Tomé and Príncipe", "code": "STP", "confederation": "CAF"},
    {"name": "Senegal", "code": "SEN", "confederation": "CAF"},
    {"name": "Seychelles", "code": "SEY", "confederation": "CAF"},
    {"name": "Sierra Leone", "code": "SLE", "confederation": "CAF"},
    {"name": "Somalia", "code": "SOM", "confederation": "CAF"},
    {"name": "South Africa", "code": "RSA", "confederation": "CAF"},
    {"name": "South Sudan", "code": "SSD", "confederation": "CAF"},
    {"name": "Sudan", "code": "SUD", "confederation": "CAF"},
    {"name": "Tanzania", "code": "TAN", "confederation": "CAF"},
    {"name": "Togo", "code": "TOG", "confederation": "CAF"},
    {"name": "Tunisia", "code": "TUN", "confederation": "CAF"},
    {"name": "Uganda", "code": "UGA", "confederation": "CAF"},
    {"name": "Zambia", "code": "ZAM", "confederation": "CAF"},
    {"name": "Zimbabwe", "code": "ZIM", "confederation": "CAF"},

    {"name": "Afghanistan", "code": "AFG", "confederation": "AFC"},
    {"name": "Australia", "code": "AUS", "confederation": "AFC"},
    {"name": "Bahrain", "code": "BHR", "confederation": "AFC"},
    {"name": "Bangladesh", "code": "BAN", "confederation": "AFC"},
    {"name": "Bhutan", "code": "BHU", "confederation": "AFC"},
    {"name": "Brunei Darussalam", "code": "BRU", "confederation": "AFC"},
    {"name": "Cambodia", "code": "CAM", "confederation": "AFC"},
    {"name": "China PR", "code": "CHN", "confederation": "AFC"},
    {"name": "Chinese Taipei", "code": "TPE", "confederation": "AFC"},
    {"name": "DPR Korea", "code": "PRK", "confederation": "AFC"},
    {"name": "Guam", "code": "GUM", "confederation": "AFC"},
    {"name": "Hong Kong", "code": "HKG", "confederation": "AFC"},
    {"name": "India", "code": "IND", "confederation": "AFC"},
    {"name": "Indonesia", "code": "IDN", "confederation": "AFC"},
    {"name": "Iran", "code": "IRN", "confederation": "AFC"},
    {"name": "Iraq", "code": "IRQ", "confederation": "AFC"},
    {"name": "Japan", "code": "JPN", "confederation": "AFC"},
    {"name": "Jordan", "code": "JOR", "confederation": "AFC"},
    {"name": "Kuwait", "code": "KUW", "confederation": "AFC"},
    {"name": "Kyrgyz Republic", "code": "KGZ", "confederation": "AFC"},
    {"name": "Laos", "code": "LAO", "confederation": "AFC"},
    {"name": "Lebanon", "code": "LBN", "confederation": "AFC"},
    {"name": "Macau", "code": "MAC", "confederation": "AFC"},
    {"name": "Malaysia", "code": "MAS", "confederation": "AFC"},
    {"name": "Maldives", "code": "MDV", "confederation": "AFC"},
    {"name": "Mongolia", "code": "MGL", "confederation": "AFC"},
    {"name": "Myanmar", "code": "MYA", "confederation": "AFC"},
    {"name": "Nepal", "code": "NEP", "confederation": "AFC"},
    {"name": "Oman", "code": "OMA", "confederation": "AFC"},
    {"name": "Pakistan", "code": "PAK", "confederation": "AFC"},
    {"name": "Palestine", "code": "PLE", "confederation": "AFC"},
    {"name": "Philippines", "code": "PHI", "confederation": "AFC"},
    {"name": "Qatar", "code": "QAT", "confederation": "AFC"},
    {"name": "Republic of Korea", "code": "KOR", "confederation": "AFC"},
    {"name": "Saudi Arabia", "code": "KSA", "confederation": "AFC"},
    {"name": "Singapore", "code": "SGP", "confederation": "AFC"},
    {"name": "Sri Lanka", "code": "SRI", "confederation": "AFC"},
    {"name": "Syria", "code": "SYR", "confederation": "AFC"},
    {"name": "Tajikistan", "code": "TJK", "confederation": "AFC"},
    {"name": "Thailand", "code": "THA", "confederation": "AFC"},
    {"name": "Timor-Leste", "code": "TLS", "confederation": "AFC"},
    {"name": "Turkmenistan", "code": "TKM", "confederation": "AFC"},
    {"name": "United Arab Emirates", "code": "UAE", "confederation": "AFC"},
    {"name": "Uzbekistan", "code": "UZB", "confederation": "AFC"},
    {"name": "Vietnam", "code": "VIE", "confederation": "AFC"},
    {"name": "Yemen", "code": "YEM", "confederation": "AFC"},

    {"name": "American Samoa", "code": "ASA", "confederation": "OFC"},
    {"name": "Cook Islands", "code": "COK", "confederation": "OFC"},
    {"name": "Fiji", "code": "FIJ", "confederation": "OFC"},
    {"name": "New Caledonia", "code": "NCL", "confederation": "OFC"},
    {"name": "New Zealand", "code": "NZL", "confederation": "OFC"},
    {"name": "Papua New Guinea", "code": "PNG", "confederation": "OFC"},
    {"name": "Samoa", "code": "SAM", "confederation": "OFC"},
    {"name": "Solomon Islands", "code": "SOL", "confederation": "OFC"},
    {"name": "Tahiti", "code": "TAH", "confederation": "OFC"},
    {"name": "Tonga", "code": "TGA", "confederation": "OFC"},
    {"name": "Vanuatu", "code": "VAN", "confederation": "OFC"},

    {"name": "Martinique", "code": "MTQ", "confederation": "CONCACAF"},
    {"name": "Guadeloupe", "code": "GLP", "confederation": "CONCACAF"},
    {"name": "French Guiana", "code": "GUF", "confederation": "CONCACAF"},
    {"name": "Jersey", "code": "JEY", "confederation": "UEFA"},
    {"name": "Guernsey", "code": "GGY", "confederation": "UEFA"},
    {"name": "Curaçao", "code": "CUW", "confederation": "CONCACAF"},
]

def seed_confederations_and_countries(db: Session) -> dict[str, CountryModel]:
    existing_confeds = {c.code: c for c in db.scalars(select(ConfederationModel)).all()}
    for conf_data in CONFEDERATIONS_DATA:
        if conf_data["code"] not in existing_confeds:
            conf = ConfederationModel(name=conf_data["name"], code=conf_data["code"])
            db.add(conf)
            existing_confeds[conf_data["code"]] = conf
    db.flush()

    existing_countries = {c.name: c for c in db.scalars(select(CountryModel)).all()}
    for c_data in COUNTRIES_DATA:
        if c_data["name"] not in existing_countries:
            conf = existing_confeds.get(c_data["confederation"])
            country = CountryModel(name=c_data["name"], code=c_data["code"], confederation=conf)
            db.add(country)
            existing_countries[c_data["name"]] = country
    db.commit()

    return existing_countries


TEAM_COUNTRIES = {
    'Amatorzy HTML': 'Poland',
    'CF Java': 'Spain',
    'Python FC': 'England',
    'Galacticos Rust': 'Spain',
    'AC C++': 'Italy',
    'TypeScript United': 'England',
    'Golang FC': 'Germany',
    'Real SQL': 'Spain',
    'FC Docker': 'Netherlands',
    'Inter Kotlin': 'Italy',
    'Athletic Swift': 'United States',
    'Dynamo JavaScript': 'Ukraine',
    'Sporting PHP': 'Portugal',
    'C# Dynamo': 'Czechia',
    'Vim SV': 'Sweden',
    'Git Atletico': 'Argentina',
    'Boca Assembly': 'Argentina',
    'Linux Rovers': 'Scotland',
    'AI Neural FC': 'Japan',
    'CSS Selectors': 'France'
}


def seed_leagues(db: Session, country_map: dict[str, CountryModel]) -> LeagueModel:
    stmt = select(LeagueModel).where(LeagueModel.name == "Developer Super League")
    league = db.execute(stmt).scalar_one_or_none()
    if not league:
        poland = country_map.get("Poland")
        league = LeagueModel(name="Developer Super League", country=poland)
        db.add(league)
        db.commit()
        db.refresh(league)
    return league


NATIONALITY_CLEAN_MAP = {
    'Bośnia i Herc.': 'Bosnia and Herzegovina',
    'Bo\u015bnia i Herc.': 'Bosnia and Herzegovina',
    'Demokr. Rep. Konga': 'Congo DR',
    'Rep. Środkowoafryk.': 'Central African Republic',
    'Rep. \u015arodkowoafryk.': 'Central African Republic',
    'St Vincent i Grenad.': 'Saint Vincent and the Grenadines',
    'W-y Ziel. Przylądka': 'Cabo Verde',
    'W-y Ziel. Przyl\u0105dka': 'Cabo Verde',
    'Curacao': 'Curaçao',
    'Cura\u00e7ao': 'Curaçao',
    'Côte d\'Ivoire': 'Côte d\'Ivoire',
    'C\u00f4te d\'Ivoire': 'Côte d\'Ivoire',
    'Ivory Coast': 'Côte d\'Ivoire',
}


def seed_teams_and_players(db: Session, file_name: str = "data.json") -> tuple[int, int]:
    country_map = seed_confederations_and_countries(db)
    league = seed_leagues(db, country_map)

    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    teams_path = os.path.join(base_dir, "data", "teams.json")
    players_path = os.path.join(base_dir, "data", "players.json")
    legacy_path = file_name if os.path.isabs(file_name) or os.path.exists(file_name) else os.path.join(base_dir, "data", file_name)

    seeded_teams_count = 0
    seeded_players_count = 0

    existing_teams = {
        t.name: t
        for t in db.scalars(
            select(TeamModel).options(
                selectinload(TeamModel.players).joinedload(PlayerModel.stats),
                selectinload(TeamModel.players).joinedload(PlayerModel.goalkeeper_stats),
            )
        ).all()
    }

    existing_leagues = {
        l.name: l
        for l in db.scalars(select(LeagueModel)).all()
    }

    if os.path.exists(teams_path) and os.path.exists(players_path):
        with open(teams_path, "r", encoding="utf-8") as f:
            teams_data = json.load(f)
        with open(players_path, "r", encoding="utf-8") as f:
            players_data = json.load(f)

        for t_info in teams_data:
            team_name = t_info["name"]
            raw_league = t_info.get("league") or "Developer Super League"
            team_country_name = t_info.get("country") or TEAM_COUNTRIES.get(team_name, "England")
            team_country = country_map.get(team_country_name)
            team_country_id = team_country.id if team_country else None

            if raw_league not in existing_leagues:
                target_league = LeagueModel(name=raw_league, country_id=team_country_id)
                db.add(target_league)
                db.flush()
                existing_leagues[raw_league] = target_league
            else:
                target_league = existing_leagues[raw_league]
                if target_league.country_id is None and team_country_id:
                    target_league.country_id = team_country_id

            team_model = existing_teams.get(team_name)
            team_formation = t_info.get("formation", "4-3-3")

            if not team_model:
                team_model = TeamModel(name=team_name, league_id=target_league.id, country_id=team_country_id, formation=team_formation)
                db.add(team_model)
                db.flush()
                existing_teams[team_name] = team_model
                seeded_teams_count += 1
            else:
                team_model.league_id = target_league.id
                team_model.country_id = team_country_id
                team_model.formation = team_formation

        for p_data in players_data:
            team_name = p_data.get("team_name")
            team_model = existing_teams.get(team_name)
            if not team_model:
                continue

            existing_players_map = {p.full_name: p for p in team_model.players}
            full_name = p_data.get("full_name") or p_data.get("short_name", "Unknown")
            short_name = p_data.get("short_name") or full_name

            raw_nationality = p_data.get("nationality", "Unknown")
            clean_nationality = NATIONALITY_CLEAN_MAP.get(raw_nationality, raw_nationality)
            player_country = country_map.get(clean_nationality, team_model.country)
            player_country_id = player_country.id if player_country else team_model.country_id
            overall_val = p_data.get("overall")
            position_str = p_data.get("position", "CENTRAL_MIDFIELDER")

            if full_name in existing_players_map:
                existing_p = existing_players_map[full_name]
                existing_p.nationality = clean_nationality
                existing_p.country_id = player_country_id
                existing_p.overall = overall_val
                existing_p.age = p_data.get("age", 24)
                existing_p.height = p_data.get("height", 180)
                if position_str == "GOALKEEPER":
                    if existing_p.goalkeeper_stats:
                        existing_p.goalkeeper_stats.diving = p_data.get("diving") or 50
                        existing_p.goalkeeper_stats.handling = p_data.get("handling") or 50
                        existing_p.goalkeeper_stats.kicking = p_data.get("kicking") or 50
                        existing_p.goalkeeper_stats.reflexes = p_data.get("reflexes") or 50
                        existing_p.goalkeeper_stats.speed = p_data.get("speed") or 50
                        existing_p.goalkeeper_stats.positioning = p_data.get("positioning") or 50
                    else:
                        existing_p.goalkeeper_stats = GoalkeeperStatsModel(
                            diving=p_data.get("diving") or 50,
                            handling=p_data.get("handling") or 50,
                            kicking=p_data.get("kicking") or 50,
                            reflexes=p_data.get("reflexes") or 50,
                            speed=p_data.get("speed") or 50,
                            positioning=p_data.get("positioning") or 50,
                        )
                    existing_p.stats = None
                else:
                    def_val = (p_data.get("defending") if p_data.get("defending") is not None else p_data.get("defence")) or 50
                    if existing_p.stats:
                        existing_p.stats.pace = p_data.get("pace") or 50
                        existing_p.stats.shooting = p_data.get("shooting") or 50
                        existing_p.stats.passing = p_data.get("passing") or 50
                        existing_p.stats.dribbling = p_data.get("dribbling") or 50
                        existing_p.stats.defence = def_val
                        existing_p.stats.physical = p_data.get("physical") or 50
                        existing_p.stats.heading = p_data.get("heading") or 50
                    else:
                        existing_p.stats = PlayerStatsModel(
                            pace=p_data.get("pace") or 50,
                            shooting=p_data.get("shooting") or 50,
                            passing=p_data.get("passing") or 50,
                            dribbling=p_data.get("dribbling") or 50,
                            defence=def_val,
                            physical=p_data.get("physical") or 50,
                            heading=p_data.get("heading") or 50,
                        )
                    existing_p.goalkeeper_stats = None
                continue

            if position_str == "GOALKEEPER":
                player_model = PlayerModel(
                    team=team_model,
                    country_id=player_country_id,
                    full_name=full_name,
                    short_name=short_name,
                    position=position_str,
                    age=p_data.get("age", 24),
                    nationality=clean_nationality,
                    overall=overall_val,
                    fitness=1.0,
                    form=1.0,
                    height=p_data.get("height", 180),
                    goalkeeper_stats=GoalkeeperStatsModel(
                        diving=p_data.get("diving") or 50,
                        handling=p_data.get("handling") or 50,
                        kicking=p_data.get("kicking") or 50,
                        reflexes=p_data.get("reflexes") or 50,
                        speed=p_data.get("speed") or 50,
                        positioning=p_data.get("positioning") or 50,
                    ),
                )
            else:
                def_val = (p_data.get("defending") if p_data.get("defending") is not None else p_data.get("defence")) or 50
                player_model = PlayerModel(
                    team=team_model,
                    country_id=player_country_id,
                    full_name=full_name,
                    short_name=short_name,
                    position=position_str,
                    age=p_data.get("age", 24),
                    nationality=clean_nationality,
                    overall=overall_val,
                    fitness=1.0,
                    form=1.0,
                    height=p_data.get("height", 180),
                    stats=PlayerStatsModel(
                        pace=p_data.get("pace") or 50,
                        shooting=p_data.get("shooting") or 50,
                        passing=p_data.get("passing") or 50,
                        dribbling=p_data.get("dribbling") or 50,
                        defence=def_val,
                        physical=p_data.get("physical") or 50,
                        heading=p_data.get("heading") or 50,
                    ),
                )
            db.add(player_model)
            seeded_players_count += 1

        db.commit()
        return seeded_teams_count, seeded_players_count

    # Fallback to legacy single file
    if not os.path.exists(legacy_path):
        print(f"Error: {legacy_path} not found.")
        return 0, 0

    with open(legacy_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for team_name, players_list in data.items():
        team_model = existing_teams.get(team_name)
        team_country_name = TEAM_COUNTRIES.get(team_name, "Poland")
        team_country = country_map.get(team_country_name)
        team_country_id = team_country.id if team_country else None

        if not team_model:
            team_model = TeamModel(name=team_name, league_id=league.id, country_id=team_country_id)
            db.add(team_model)
            db.flush()
            existing_teams[team_name] = team_model
            seeded_teams_count += 1
        else:
            team_model.league_id = league.id
            team_model.country_id = team_country_id

        existing_players_map = {p.full_name: p for p in team_model.players}

        for p_data in players_list:
            full_name = p_data.get("full_name") or p_data.get("name", "Unknown")
            short_name = p_data.get("short_name") or p_data.get("name", full_name)
            raw_nationality = p_data.get("nationality", "Unknown")
            clean_nationality = NATIONALITY_CLEAN_MAP.get(raw_nationality, raw_nationality)
            player_country = country_map.get(clean_nationality, team_country)
            player_country_id = player_country.id if player_country else team_country_id
            position_str = p_data.get("position", "CENTRAL_MIDFIELDER")
            overall_val = p_data.get("overall", 50)

            if full_name in existing_players_map:
                existing_p = existing_players_map[full_name]
                existing_p.nationality = clean_nationality
                existing_p.country_id = player_country_id
                existing_p.overall = overall_val
                existing_p.age = p_data.get("age", 20)
                existing_p.height = p_data.get("height", 180)
                if position_str == "GOALKEEPER":
                    if existing_p.goalkeeper_stats:
                        existing_p.goalkeeper_stats.diving = p_data.get("diving") or 50
                        existing_p.goalkeeper_stats.handling = p_data.get("handling") or 50
                        existing_p.goalkeeper_stats.kicking = p_data.get("kicking") or 50
                        existing_p.goalkeeper_stats.reflexes = p_data.get("reflexes") or 50
                        existing_p.goalkeeper_stats.speed = p_data.get("speed") or 50
                        existing_p.goalkeeper_stats.positioning = p_data.get("positioning") or 50
                    else:
                        existing_p.goalkeeper_stats = GoalkeeperStatsModel(
                            diving=p_data.get("diving") or 50,
                            handling=p_data.get("handling") or 50,
                            kicking=p_data.get("kicking") or 50,
                            reflexes=p_data.get("reflexes") or 50,
                            speed=p_data.get("speed") or 50,
                            positioning=p_data.get("positioning") or 50,
                        )
                    existing_p.stats = None
                else:
                    def_val = (p_data.get("defending") if p_data.get("defending") is not None else p_data.get("defence")) or 50
                    if existing_p.stats:
                        existing_p.stats.pace = p_data.get("pace") or 50
                        existing_p.stats.shooting = p_data.get("shooting") or 50
                        existing_p.stats.passing = p_data.get("passing") or 50
                        existing_p.stats.dribbling = p_data.get("dribbling") or 50
                        existing_p.stats.defence = def_val
                        existing_p.stats.physical = p_data.get("physical") or 50
                        existing_p.stats.heading = p_data.get("heading") or 50
                    else:
                        existing_p.stats = PlayerStatsModel(
                            pace=p_data.get("pace") or 50,
                            shooting=p_data.get("shooting") or 50,
                            passing=p_data.get("passing") or 50,
                            dribbling=p_data.get("dribbling") or 50,
                            defence=def_val,
                            physical=p_data.get("physical") or 50,
                            heading=p_data.get("heading") or 50,
                        )
                    existing_p.goalkeeper_stats = None
                continue

            if position_str == "GOALKEEPER":
                player_model = PlayerModel(
                    team=team_model,
                    country_id=player_country_id,
                    full_name=full_name,
                    short_name=short_name,
                    position=position_str,
                    age=p_data.get("age", 20),
                    nationality=clean_nationality,
                    overall=overall_val,
                    fitness=1.0,
                    form=1.0,
                    height=p_data.get("height", 180),
                    goalkeeper_stats=GoalkeeperStatsModel(
                        diving=p_data.get("diving") or 50,
                        handling=p_data.get("handling") or 50,
                        kicking=p_data.get("kicking") or 50,
                        reflexes=p_data.get("reflexes") or 50,
                        speed=p_data.get("speed") or 50,
                        positioning=p_data.get("positioning") or 50,
                    ),
                )
            else:
                def_val = (p_data.get("defending") if p_data.get("defending") is not None else p_data.get("defence")) or 50
                player_model = PlayerModel(
                    team=team_model,
                    country_id=player_country_id,
                    full_name=full_name,
                    short_name=short_name,
                    position=position_str,
                    age=p_data.get("age", 20),
                    nationality=clean_nationality,
                    overall=overall_val,
                    fitness=1.0,
                    form=1.0,
                    height=p_data.get("height", 180),
                    stats=PlayerStatsModel(
                        pace=p_data.get("pace") or 50,
                        shooting=p_data.get("shooting") or 50,
                        passing=p_data.get("passing") or 50,
                        dribbling=p_data.get("dribbling") or 50,
                        defence=def_val,
                        physical=p_data.get("physical") or 50,
                        heading=p_data.get("heading") or 50,
                    ),
                )
            db.add(player_model)
            seeded_players_count += 1

    db.commit()
    return seeded_teams_count, seeded_players_count


def seed_all(db: Session) -> None:
    from src.db.migrate import init_db
    init_db()
    c_map = seed_confederations_and_countries(db)
    league = seed_leagues(db, c_map)
    teams_count, players_count = seed_teams_and_players(db)
    print("Seeding completed successfully!")
    print(f"Confederations: {len(CONFEDERATIONS_DATA)}")
    print(f"Countries: {len(c_map)}")
    print(f"League: {league.name}")
    print(f"Teams in DB: {db.query(TeamModel).count()} (Newly seeded: {teams_count})")
    print(f"Players in DB: {db.query(PlayerModel).count()} (Newly seeded: {players_count})")
    print(f"Player Stats in DB: {db.query(PlayerStatsModel).count()}")
    print(f"Goalkeeper Stats in DB: {db.query(GoalkeeperStatsModel).count()}")


if __name__ == "__main__":
    with SessionLocal() as db:
        seed_all(db)

    