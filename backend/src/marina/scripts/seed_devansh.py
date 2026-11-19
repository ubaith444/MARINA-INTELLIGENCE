import sqlite3
import uuid

conn = sqlite3.connect('backend/marina.db')
c = conn.cursor()

c.execute("SELECT id FROM players WHERE first_name = 'Devansh' AND last_name = 'Dabas'")
if not c.fetchone():
    p_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'chennaiyin-fc-devansh-dabas'))
    c.execute("""
        INSERT INTO players (id, slug, first_name, last_name, known_name, squad_number, primary_position, nationality, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (p_id, 'devansh-dabas', 'Devansh', 'Dabas', 'Devansh Dabas', 44, 'GK', 'India'))
    
    # Also register in squad_registrations for 2026-27
    c.execute("SELECT id FROM seasons WHERE is_current = 1")
    s_row = c.fetchone()
    season_id = s_row[0] if s_row else None
    c.execute("SELECT id FROM teams WHERE slug = 'chennaiyin-fc'")
    t_row = c.fetchone()
    team_id = t_row[0] if t_row else None
    
    if season_id and team_id:
        reg_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{team_id}-{season_id}-{p_id}'))
        c.execute("""
            INSERT INTO squad_registrations (id, team_id, season_id, player_id, jersey_number, squad_status, is_active, registered_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, 44, 'FIRST_TEAM', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (reg_id, team_id, season_id, p_id))
    conn.commit()
    print("Added Devansh Dabas successfully.")
else:
    print("Devansh Dabas already exists.")
conn.close()
