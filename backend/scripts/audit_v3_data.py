import asyncio
from marina.db.session import AsyncSessionLocal
from sqlalchemy import select, func
from marina.models.player import Player
from marina.models.match import Match, MatchLineup, MatchEvent
from marina.models.statistics import PlayerMatchStatistic, TeamMatchStatistic
from marina.models.team import Team

async def audit():
    async with AsyncSessionLocal() as db:
        players = {p.id: p for p in (await db.execute(select(Player))).scalars().all()}
        print(f"Total Players in DB: {len(players)}")
        
        matches = {m.id: m for m in (await db.execute(select(Match).order_by(Match.match_number))).scalars().all()}
        finished = [m for m in matches.values() if m.match_status.value == "FINISHED"]
        print(f"Total Matches: {len(matches)}, Finished: {len(finished)}")
        for m in finished:
            print(f"  M#{m.match_number}: {m.home_score}-{m.away_score} (id={m.id})")

        lineups = (await db.execute(select(MatchLineup))).scalars().all()
        print(f"\nTotal MatchLineup records: {len(lineups)}")
        roles = set(l.lineup_role.value if hasattr(l.lineup_role, 'value') else str(l.lineup_role) for l in lineups)
        print(f"Lineup roles present: {roles}")
        
        starters = [l for l in lineups if "START" in str(l.lineup_role).upper()]
        subs = [l for l in lineups if "SUB" in str(l.lineup_role).upper() or "BENCH" in str(l.lineup_role).upper()]
        print(f"Starters: {len(starters)}, Subs/Bench: {len(subs)}")
        
        for l in lineups[:15]:
            p = players.get(l.player_id)
            p_name = p.known_name or f"{p.first_name} {p.last_name}" if p else str(l.player_id)
            m = matches.get(l.match_id)
            m_num = m.match_number if m else "?"
            print(f"  Lineup: M#{m_num} {p_name} | role={l.lineup_role} | pos={l.position} | mins={l.minutes_played} | sub_out={l.sub_out_minute}")

        p_stats = (await db.execute(select(PlayerMatchStatistic))).scalars().all()
        print(f"\nTotal PlayerMatchStatistic records: {len(p_stats)}")
        has_tackles = [p for p in p_stats if (p.tackles_total or 0) > 0 or (p.tackles_won or 0) > 0]
        has_interceptions = [p for p in p_stats if (p.interceptions or 0) > 0]
        has_clearances = [p for p in p_stats if (p.clearances or 0) > 0]
        has_blocks = [p for p in p_stats if (p.blocks or 0) > 0]
        has_aerial = [p for p in p_stats if (p.aerial_duels_total or 0) > 0]
        has_ground = [p for p in p_stats if (p.ground_duels_total or 0) > 0]
        print(f"PStats with tackles: {len(has_tackles)}, interc: {len(has_interceptions)}, clear: {len(has_clearances)}, blocks: {len(has_blocks)}, aerial: {len(has_aerial)}, ground: {len(has_ground)}")
        
        # Sample defensive stats
        for ps in p_stats[:10]:
            p = players.get(ps.player_id)
            p_name = p.known_name or f"{p.first_name} {p.last_name}" if p else str(ps.player_id)
            m = matches.get(ps.match_id)
            m_num = m.match_number if m else "?"
            print(f"  PStat M#{m_num} {p_name}: mins={ps.minutes_played}, t_won={ps.tackles_won}/{ps.tackles_total}, int={ps.interceptions}, clr={ps.clearances}, blk={ps.blocks}, aer={ps.aerial_duels_won}/{ps.aerial_duels_total}")

        events = (await db.execute(select(MatchEvent))).scalars().all()
        print(f"\nTotal MatchEvent records: {len(events)}")
        event_types = set(e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type) for e in events)
        print(f"Event types present: {event_types}")
        sub_events = [e for e in events if "SUB" in str(e.event_type).upper()]
        print(f"Substitution events: {len(sub_events)}")
        for e in sub_events:
            p1 = players.get(e.primary_player_id)
            p2 = players.get(e.secondary_player_id)
            p1_name = p1.known_name or f"{p1.first_name} {p1.last_name}" if p1 else str(e.primary_player_id)
            p2_name = p2.known_name or f"{p2.first_name} {p2.last_name}" if p2 else str(e.secondary_player_id)
            m = matches.get(e.match_id)
            m_num = m.match_number if m else "?"
            print(f"  Sub M#{m_num} min {e.minute}: {p1_name} for {p2_name} | desc={e.description}")

if __name__ == "__main__":
    asyncio.run(audit())
