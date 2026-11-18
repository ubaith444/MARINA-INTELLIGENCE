"""Initial normalized schema for MARINA INTELLIGENCE.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-18 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from marina.db.base import GUID

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Competitions
    op.create_table(
        "competitions",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("country", sa.String(length=64), nullable=False),
        sa.Column("federation", sa.String(length=64), nullable=False),
        sa.Column("tier", sa.Integer(), nullable=False),
        sa.Column("competition_type", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_competitions_code", "competitions", ["code"], unique=True)

    # 2. Seasons
    op.create_table(
        "seasons",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("competition_id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["competition_id"], ["competitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("competition_id", "name", name="uq_season_competition_name"),
        sa.UniqueConstraint("competition_id", "slug", name="uq_season_competition_slug"),
    )
    op.create_index("ix_seasons_competition_id", "seasons", ["competition_id"], unique=False)
    op.create_index("ix_seasons_slug", "seasons", ["slug"], unique=False)

    # 3. Venues
    op.create_table(
        "venues",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("city", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=64), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("surface", sa.String(length=32), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_venues_city", "venues", ["city"], unique=False)
    op.create_index("ix_venues_name", "venues", ["name"], unique=True)

    # 4. Teams
    op.create_table(
        "teams",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("short_name", sa.String(length=32), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("primary_venue_id", GUID(), nullable=True),
        sa.Column("primary_color", sa.String(length=16), nullable=True),
        sa.Column("secondary_color", sa.String(length=16), nullable=True),
        sa.Column("website_url", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["primary_venue_id"], ["venues.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teams_name", "teams", ["name"], unique=True)
    op.create_index("ix_teams_short_name", "teams", ["short_name"], unique=False)
    op.create_index("ix_teams_slug", "teams", ["slug"], unique=True)
    op.create_index("ix_teams_primary_venue_id", "teams", ["primary_venue_id"], unique=False)

    # 5. Players (Identity decoupled from clubs)
    op.create_table(
        "players",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("known_name", sa.String(length=128), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(length=64), nullable=False),
        sa.Column("secondary_nationality", sa.String(length=64), nullable=True),
        sa.Column("primary_position", sa.String(length=32), nullable=False),
        sa.Column("secondary_position", sa.String(length=32), nullable=True),
        sa.Column("height_cm", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Integer(), nullable=True),
        sa.Column("preferred_foot", sa.String(length=16), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_players_slug", "players", ["slug"], unique=True)
    op.create_index("ix_players_known_name", "players", ["known_name"], unique=False)
    op.create_index("ix_players_nationality", "players", ["nationality"], unique=False)

    # 6. Squad Registrations (Season & Club bindings)
    op.create_table(
        "squad_registrations",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("season_id", GUID(), nullable=False),
        sa.Column("jersey_number", sa.Integer(), nullable=True),
        sa.Column("squad_status", sa.String(length=32), nullable=False),
        sa.Column("registered_at", sa.Date(), nullable=True),
        sa.Column("deregistered_at", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season_id", "team_id", "player_id", name="uq_squad_registration_player_season"),
    )
    op.create_index("ix_squad_registrations_player_id", "squad_registrations", ["player_id"], unique=False)
    op.create_index("ix_squad_registrations_team_id", "squad_registrations", ["team_id"], unique=False)
    op.create_index("ix_squad_registrations_season_id", "squad_registrations", ["season_id"], unique=False)
    op.create_index("ix_squad_reg_lookup", "squad_registrations", ["season_id", "team_id", "jersey_number"], unique=False)

    # 7. Matches
    op.create_table(
        "matches",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("season_id", GUID(), nullable=False),
        sa.Column("home_team_id", GUID(), nullable=False),
        sa.Column("away_team_id", GUID(), nullable=False),
        sa.Column("venue_id", GUID(), nullable=True),
        sa.Column("match_number", sa.Integer(), nullable=True),
        sa.Column("scheduled_kickoff", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_kickoff", sa.DateTime(timezone=True), nullable=True),
        sa.Column("match_status", sa.String(length=32), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("home_penalty_score", sa.Integer(), nullable=True),
        sa.Column("away_penalty_score", sa.Integer(), nullable=True),
        sa.Column("attendance", sa.Integer(), nullable=True),
        sa.Column("referee", sa.String(length=128), nullable=True),
        sa.Column("pitch_condition", sa.String(length=64), nullable=True),
        sa.Column("weather_summary", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["season_id"], ["seasons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["venue_id"], ["venues.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matches_season_id", "matches", ["season_id"], unique=False)
    op.create_index("ix_matches_home_team_id", "matches", ["home_team_id"], unique=False)
    op.create_index("ix_matches_away_team_id", "matches", ["away_team_id"], unique=False)
    op.create_index("ix_matches_venue_id", "matches", ["venue_id"], unique=False)
    op.create_index("ix_matches_scheduled_kickoff", "matches", ["scheduled_kickoff"], unique=False)
    op.create_index("ix_matches_match_status", "matches", ["match_status"], unique=False)
    op.create_index("ix_matches_match_number", "matches", ["match_number"], unique=False)
    op.create_index("ix_matches_season_status", "matches", ["season_id", "match_status"], unique=False)
    op.create_index("ix_matches_teams", "matches", ["home_team_id", "away_team_id"], unique=False)

    # 8. Data Sources
    op.create_table(
        "data_sources",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("provider_type", sa.String(length=32), nullable=False),
        sa.Column("base_url", sa.String(length=255), nullable=True),
        sa.Column("api_version", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("trust_score", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_sources_code", "data_sources", ["code"], unique=True)

    # 9. Import History
    op.create_table(
        "import_history",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("data_source_id", GUID(), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("batch_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("records_imported", sa.Integer(), nullable=False),
        sa.Column("records_failed", sa.Integer(), nullable=False),
        sa.Column("error_payload", sa.Text(), nullable=True),
        sa.Column("checksum_hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_import_history_data_source_id", "import_history", ["data_source_id"], unique=False)
    op.create_index("ix_import_history_entity_type", "import_history", ["entity_type"], unique=False)
    op.create_index("ix_import_history_batch_id", "import_history", ["batch_id"], unique=False)
    op.create_index("ix_import_history_source_batch", "import_history", ["data_source_id", "batch_id"], unique=False)

    # 10. Lineups
    op.create_table(
        "lineups",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=False),
        sa.Column("squad_registration_id", GUID(), nullable=True),
        sa.Column("lineup_role", sa.String(length=32), nullable=False),
        sa.Column("position", sa.String(length=32), nullable=True),
        sa.Column("tactical_formation", sa.String(length=32), nullable=True),
        sa.Column("jersey_number", sa.Integer(), nullable=True),
        sa.Column("is_captain", sa.Boolean(), nullable=False),
        sa.Column("minutes_played", sa.Integer(), nullable=True),
        sa.Column("is_substitute_in", sa.Boolean(), nullable=False),
        sa.Column("sub_in_minute", sa.Integer(), nullable=True),
        sa.Column("sub_out_minute", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["squad_registration_id"], ["squad_registrations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "player_id", name="uq_match_player_lineup"),
    )
    op.create_index("ix_lineups_match_id", "lineups", ["match_id"], unique=False)
    op.create_index("ix_lineups_team_id", "lineups", ["team_id"], unique=False)
    op.create_index("ix_lineups_player_id", "lineups", ["player_id"], unique=False)

    # 11. Match Events
    op.create_table(
        "match_events",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=True),
        sa.Column("primary_player_id", GUID(), nullable=True),
        sa.Column("secondary_player_id", GUID(), nullable=True),
        sa.Column("data_source_id", GUID(), nullable=True),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("period", sa.String(length=32), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("stoppage_minute", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("raw_metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["primary_player_id"], ["players.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["secondary_player_id"], ["players.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_match_events_match_id", "match_events", ["match_id"], unique=False)
    op.create_index("ix_match_events_team_id", "match_events", ["team_id"], unique=False)
    op.create_index("ix_match_events_event_type", "match_events", ["event_type"], unique=False)
    op.create_index("ix_match_events_primary_player_id", "match_events", ["primary_player_id"], unique=False)
    op.create_index("ix_match_events_secondary_player_id", "match_events", ["secondary_player_id"], unique=False)
    op.create_index("ix_match_events_timeline", "match_events", ["match_id", "minute", "period"], unique=False)

    # 12. Team Match Statistics (Strictly nullable metrics, no zero-filling)
    op.create_table(
        "team_match_statistics",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("data_source_id", GUID(), nullable=False),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("possession_pct", sa.Float(), nullable=True),
        sa.Column("shots_total", sa.Integer(), nullable=True),
        sa.Column("shots_on_target", sa.Integer(), nullable=True),
        sa.Column("shots_off_target", sa.Integer(), nullable=True),
        sa.Column("blocked_shots", sa.Integer(), nullable=True),
        sa.Column("expected_goals", sa.Float(), nullable=True),
        sa.Column("expected_goals_conceded", sa.Float(), nullable=True),
        sa.Column("big_chances_created", sa.Integer(), nullable=True),
        sa.Column("big_chances_missed", sa.Integer(), nullable=True),
        sa.Column("passes_total", sa.Integer(), nullable=True),
        sa.Column("passes_completed", sa.Integer(), nullable=True),
        sa.Column("pass_accuracy_pct", sa.Float(), nullable=True),
        sa.Column("touches", sa.Integer(), nullable=True),
        sa.Column("tackles_total", sa.Integer(), nullable=True),
        sa.Column("tackles_won", sa.Integer(), nullable=True),
        sa.Column("interceptions", sa.Integer(), nullable=True),
        sa.Column("clearances", sa.Integer(), nullable=True),
        sa.Column("saves", sa.Integer(), nullable=True),
        sa.Column("corners", sa.Integer(), nullable=True),
        sa.Column("offsides", sa.Integer(), nullable=True),
        sa.Column("fouls_committed", sa.Integer(), nullable=True),
        sa.Column("yellow_cards", sa.Integer(), nullable=True),
        sa.Column("red_cards", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "team_id", "data_source_id", name="uq_team_match_stat_source"),
    )
    op.create_index("ix_team_match_statistics_match_id", "team_match_statistics", ["match_id"], unique=False)
    op.create_index("ix_team_match_statistics_team_id", "team_match_statistics", ["team_id"], unique=False)
    op.create_index("ix_team_match_stats_lookup", "team_match_statistics", ["team_id", "match_id"], unique=False)

    # 13. Player Match Statistics (Strictly nullable metrics, no zero-filling)
    op.create_table(
        "player_match_statistics",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("match_id", GUID(), nullable=False),
        sa.Column("player_id", GUID(), nullable=False),
        sa.Column("team_id", GUID(), nullable=False),
        sa.Column("data_source_id", GUID(), nullable=False),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("minutes_played", sa.Integer(), nullable=True),
        sa.Column("goals", sa.Integer(), nullable=True),
        sa.Column("assists", sa.Integer(), nullable=True),
        sa.Column("shots_total", sa.Integer(), nullable=True),
        sa.Column("shots_on_target", sa.Integer(), nullable=True),
        sa.Column("expected_goals", sa.Float(), nullable=True),
        sa.Column("expected_assists", sa.Float(), nullable=True),
        sa.Column("key_passes", sa.Integer(), nullable=True),
        sa.Column("dribbles_attempted", sa.Integer(), nullable=True),
        sa.Column("dribbles_succeeded", sa.Integer(), nullable=True),
        sa.Column("passes_total", sa.Integer(), nullable=True),
        sa.Column("passes_completed", sa.Integer(), nullable=True),
        sa.Column("pass_accuracy_pct", sa.Float(), nullable=True),
        sa.Column("crosses_total", sa.Integer(), nullable=True),
        sa.Column("crosses_successful", sa.Integer(), nullable=True),
        sa.Column("tackles_total", sa.Integer(), nullable=True),
        sa.Column("tackles_won", sa.Integer(), nullable=True),
        sa.Column("interceptions", sa.Integer(), nullable=True),
        sa.Column("clearances", sa.Integer(), nullable=True),
        sa.Column("blocks", sa.Integer(), nullable=True),
        sa.Column("aerial_duels_total", sa.Integer(), nullable=True),
        sa.Column("aerial_duels_won", sa.Integer(), nullable=True),
        sa.Column("ground_duels_total", sa.Integer(), nullable=True),
        sa.Column("ground_duels_won", sa.Integer(), nullable=True),
        sa.Column("fouls_committed", sa.Integer(), nullable=True),
        sa.Column("fouls_drawn", sa.Integer(), nullable=True),
        sa.Column("yellow_cards", sa.Integer(), nullable=True),
        sa.Column("red_cards", sa.Integer(), nullable=True),
        sa.Column("saves", sa.Integer(), nullable=True),
        sa.Column("goals_conceded", sa.Integer(), nullable=True),
        sa.Column("clean_sheet", sa.Boolean(), nullable=True),
        sa.Column("distance_covered_km", sa.Float(), nullable=True),
        sa.Column("sprints_count", sa.Integer(), nullable=True),
        sa.Column("top_speed_kmh", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["data_source_id"], ["data_sources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id", "player_id", "data_source_id", name="uq_player_match_stat_source"),
    )
    op.create_index("ix_player_match_statistics_match_id", "player_match_statistics", ["match_id"], unique=False)
    op.create_index("ix_player_match_statistics_player_id", "player_match_statistics", ["player_id"], unique=False)
    op.create_index("ix_player_match_statistics_team_id", "player_match_statistics", ["team_id"], unique=False)
    op.create_index("ix_player_match_stats_lookup", "player_match_statistics", ["player_id", "match_id"], unique=False)


def downgrade() -> None:
    op.drop_table("player_match_statistics")
    op.drop_table("team_match_statistics")
    op.drop_table("match_events")
    op.drop_table("lineups")
    op.drop_table("import_history")
    op.drop_table("data_sources")
    op.drop_table("matches")
    op.drop_table("squad_registrations")
    op.drop_table("players")
    op.drop_table("teams")
    op.drop_table("venues")
    op.drop_table("seasons")
    op.drop_table("competitions")
