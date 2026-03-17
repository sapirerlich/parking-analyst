from fastmcp import FastMCP
import sqlite3
import re
import datetime
from collections import Counter
from analysis_engine import * 


mcp = FastMCP("Parking Analyst")
db_path = '/Users/sapirerlich/Desktop/sapir/projects/whatsapp-mcp/whatsapp-bridge/store/messages.db'

@mcp.tool() # 2. This is the MCP Tool definition
def get_driver_history() -> str:
    """Retrieves a raw list of recent parking events. Use this when the user asks 'where did Sapir park yesterday?'"""

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        parking_history_query = f"""
        select case when is_from_me = 1 then 'Sapir' else 'Nir' end as driver, content, timestamp
        from messages
        """
        parking_history = cur.execute(parking_history_query).fetchall()

    formatted_history = []
    for driver, spot, time in parking_history:
        formatted_history.append(f"{driver} parked at {spot} at {time}")

    return "\n".join(formatted_history)

@mcp.tool()
def get_street_stats() -> str:
    """Calculates frequency totals for every street. Use this for general questions like 'which street do we use most?'"""
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        rows = cur.execute("SELECT content FROM messages").fetchall()
    
    streets = {}
    for row in rows:
        street_name = normalize_street(row[0]) 
        streets[street_name] = streets.get(street_name,0) +1

    formatted_history = []
    for street, times in streets.items():
        formatted_history.append(f"parked at {street} {times} times")

    return "\n".join(formatted_history)


@mcp.tool()
def get_parking_recommendation(target_hour: int = None, target_day: int = None) -> str:
    """
    Heuristic engine that predicts the best spot based on current or target time. Use this for 'where should I park now?'
    Optional target_hour (0-23) and target_day (0-6, 0=Sun) for future planning.
    """

    now = datetime.datetime.now()
    current_hour = target_hour if target_hour is not None else now.hour
    current_day = target_day if target_day is not None else now.strftime('%w') 

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        query = """
        SELECT content, 
               strftime('%w', timestamp) as day_of_week,
               strftime('%H', timestamp) as hour
        FROM messages
        """
        rows = cur.execute(query).fetchall()    

    perfect_matches = [] # Same day, +/- 1 hour
    time_matches = []    # Any day, +/- 1 hour

    for content, day, hour in rows:
        street = normalize_street(content)
        if not street:
            continue
        db_hour = int(hour)
        is_in_window = abs(db_hour - current_hour) <= 1
        if is_in_window:
            time_matches.append(street)
            if day == current_day:
                perfect_matches.append(street)            
    
    if perfect_matches:
        return calculate_best_spot(perfect_matches)

    if time_matches:
        return calculate_best_spot(time_matches)
    
    # If no time_matches were found
    all_streets = [normalize_street(r[0]) for r in rows if r[0]]
    if all_streets:
        top_overall = Counter(all_streets).most_common(1)[0][0]
        return f"No specific pattern for this time. Historically, your most used spot is {top_overall}."

if __name__ == "__main__":
    mcp.run()