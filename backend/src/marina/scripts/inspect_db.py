import sqlite3

conn = sqlite3.connect('backend/marina.db')
c = conn.cursor()
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('Existing tables in SQLite:', tables)
