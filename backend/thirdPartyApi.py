from dotenv import load_dotenv
import os
import sqlite3
import httpx

load_dotenv()

CAT_DB_PATH = os.getenv("CAT_DB")

CAT_FACTS_API_URL = "https://meowfacts.herokuapp.com/"

try:
    conn = sqlite3.connect(CAT_DB_PATH)
    print("\nCat Database connection successful")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS catFacts (
        id TEXT PRIMARY KEY,
        fact TEXT
    )''')
    conn.commit()
except sqlite3.Error as e:
    print(f"Cat Database connection failed: {e}")

def fetch_cat_facts_from_api(numFacts: int):
    response = httpx.get(f"{CAT_FACTS_API_URL}?count={numFacts}")
    if response.status_code == 200:
        valid = validate_cat_fact_response(response.json(), numFacts)
        if valid:
            for fact in response.json()["data"]:
                print(fact)
                db_stat = store_cat_fact(fact)
                if not db_stat:
                    return False
        else:
            print("Invalid response from cat facts API")
    else:
        print("Failed to fetch cat facts from API")
        return False
    return True

def store_cat_fact(fact: str):
    try:
        cat_id = get_cat_fact_count() + 1
        cursor.execute('INSERT INTO catFacts (id, fact) VALUES (?, ?)', (cat_id, fact))
        conn.commit()
        print("Cat fact added successfully")
        return True
    except sqlite3.Error as e:
        print(f"Failed to add cat fact: {e}")
        return False

def get_cat_fact_count():
    try:
        cursor.execute('SELECT COUNT(*) FROM catFacts')
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"Failed to retrieve cat fact count: {e}")
        return 0
    
def validate_cat_fact_response(response, numFacts: int):
    if "data" in response and len(response["data"]) == numFacts:
        print("Valid cat fact response structure")
        return True
    else:
        print("Invalid cat fact response structure")
        return False

#this is for testing purposes to see contents of catFacts table
def print_all_cat_facts():
    try:
        cursor.execute('SELECT * FROM catFacts')
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Fact: {row[1]}")
    except sqlite3.Error as e:
        print(f"Failed to retrieve cat facts: {e}")

def clear_cat_facts_table():
    try:
        cursor.execute('DELETE FROM catFacts')
        conn.commit()
        print("Cat facts table cleared")
    except sqlite3.Error as e:
        print(f"Failed to clear cat facts table: {e}")

#clear_cat_facts_table()
#print_all_cat_facts()