from dotenv import load_dotenv
import os
import pydantic
import sqlite3

load_dotenv()

DEALERSHIP_DB_PATH = os.getenv("DEALERSHIP_DB")

try:
    conn = sqlite3.connect(DEALERSHIP_DB_PATH)
    print("\nDealership Database connection successful")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        vin TEXT PRIMARY KEY,
        make TEXT,
        model TEXT,
        year INTEGER,
        color TEXT,
        price REAL,
        mileage INTEGER
    )''')
    conn.commit()
except sqlite3.Error as e:
    print(f"Dealership Database connection failed: {e}")
    

class Car(pydantic.BaseModel):
    vin: str
    make: str
    model: str
    year: int
    color: str
    price: float
    mileage: int

def add_car_to_db(car: Car):
    try:
        cursor.execute('''
        INSERT INTO cars (vin, make, model, year, color, price, mileage)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (car.vin, car.make, car.model, car.year, car.color, car.price, car.mileage))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    
def get_car_from_db(car_id: str):
    cursor.execute('SELECT * FROM cars WHERE vin = ?', (car_id,))
    row = cursor.fetchone()
    if row:
        return Car(
            vin=row[0],
            make=row[1],
            model=row[2],
            year=row[3],
            color=row[4],
            price=row[5],
            mileage=row[6]
        )
    return None

def update_price_in_db(car_id: str, car: Car):
    cursor.execute('''
    UPDATE cars
    SET price = ?
    WHERE vin = ?''',
    (car.price, car_id))
    conn.commit()
    return cursor.rowcount > 0

def delete_car_from_db(car_id: str):
    cursor.execute('DELETE FROM cars WHERE vin = ?', (car_id,))
    conn.commit()
    return cursor.rowcount > 0