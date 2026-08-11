import asyncio
from main import start_match, match_options, match_event_generator
from api.schemas import StartMatchRequest, MatchStatusSchema

def test_match_event_generator_serialization():
    async def _run():
        options = match_options()
        teams = options["teams"]
        req = StartMatchRequest(
            home_team_name=teams[0],
            away_team_name=teams[1],
            home_formation="4-3-3",
            away_formation="4-3-3"
        )
        start_match(req)
        gen = match_event_generator()
        
        # Read first 5 items from generator
        for _ in range(5):
            event_str = await anext(gen)
            assert event_str.startswith("data: ")
            json_data = event_str.replace("data: ", "").strip()
            parsed = MatchStatusSchema.model_validate_json(json_data)
            assert parsed.home_team_name == teams[0]
            assert parsed.away_team_name == teams[1]

    asyncio.run(_run())
