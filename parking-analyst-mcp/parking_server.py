from fastmcp import FastMCP
import aiomysql
import datetime
from collections import Counter
from analysis_engine import * 
import os
from dotenv import load_dotenv

load_dotenv() 

mcp = FastMCP("Parking Analyst")

# Aiven Connection Details
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE", "defaultdb")

async def get_db_conn():
    """Helper to create a MySQL connection"""
    return await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        autocommit=True
    )

@mcp.tool()
async def get_driver_history() -> str:
    """Retrieves recent parking events from the cloud. Use for 'where did Sapir park yesterday?'"""
    conn = await get_db_conn()
    async with conn.cursor() as cur:
        query = """
        SELECT CASE WHEN is_from_me = 1 THEN 'Sapir' ELSE 'Nir' END as driver, 
               content, timestamp 
        FROM messages 
        ORDER BY timestamp DESC LIMIT 50
        """
        await cur.execute(query)
        rows = await cur.fetchall()
    conn.close()

    formatted = [f"{r[0]} parked at {r[1]} at {r[2]}" for r in rows]
    return "\n".join(formatted) if formatted else "No parking history found."

@mcp.tool()
async def get_street_stats() -> str:
    """Calculates street totals. Use for 'which street do we use most?'"""
    conn = await get_db_conn()
    async with conn.cursor() as cur:
        await cur.execute("SELECT content FROM messages")
        rows = await cur.fetchall()
    conn.close()
    
    streets = {}
    for (content,) in rows:
        street_name = normalize_street(content) 
        streets[street_name] = streets.get(street_name, 0) + 1

    formatted = [f"parked at {s} {t} times" for s, t in streets.items()]
    return "\n".join(formatted) if formatted else "No stats available."

@mcp.tool()
async def get_parking_recommendation(target_hour: int = None, target_day: int = None) -> str:
    """Predicts best spot based on cloud history. Use for 'where should I park now?'
    Optional target_hour (0-23) and target_day (0-6, 0=Sun) for future planning."""

    now = datetime.datetime.now()
    h = target_hour if target_hour is not None else now.hour
    d_python = target_day if target_day is not None else int(now.strftime('%w'))

    conn = await get_db_conn()
    async with conn.cursor() as cur:
        query = """
        SELECT content, 
               (DAYOFWEEK(timestamp) - 1) as day_of_week, 
               HOUR(timestamp) as hour 
        FROM messages
        """
        await cur.execute(query)
        rows = await cur.fetchall()
    conn.close()

    perfect_matches = []
    time_matches = []
    all_streets = []

    for content, db_day, db_hour in rows:
        street = normalize_street(content)
        if not street: continue
        all_streets.append(street)

        if abs(db_hour - h) <= 1:
            time_matches.append(street)
            if int(db_day) == d_python:
                perfect_matches.append(street)            
    
    if perfect_matches:
        return calculate_best_spot(perfect_matches)
    if time_matches:
        return calculate_best_spot(time_matches)
    
    if all_streets:
        top_overall = Counter(all_streets).most_common(1)[0][0]
        return f"No specific time pattern. Historically, your top spot is {top_overall}."
    
    return "Not enough data yet."

if __name__ == "__main__":
    mcp.run()