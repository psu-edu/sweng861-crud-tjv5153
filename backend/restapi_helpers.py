from dotenv import load_dotenv
import os
import pydantic
import sqlite3

load_dotenv()

DEALERSHIP_DB_PATH = os.getenv("DEALERSHIP_DB")

try:
    conn = sqlite3.connect(DEALERSHIP_DB_PATH)
    print("Dealership Database connection successful")
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
    except sqlite3.IntegrityError:
        return False
    
    return True
    
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
    else:
        return None
    
def check_car_exists(car_id: str):
    cursor.execute('SELECT 1 FROM cars WHERE vin = ?', (car_id,))
    return cursor.fetchone() is not None

def update_price_in_db(car_id: str, price: float):
    if check_car_exists(car.vin):
        try:
            cursor.execute('''
            UPDATE cars
            SET price = ?
            WHERE vin = ?''',
            (price, car_id))
            conn.commit()
        except sqlite3.Error:
            return False
        
        return True
    else:
        return False

def update_car_in_db(car: Car):
    if check_car_exists(car.vin):
        try:
            cursor.execute('''
            UPDATE cars
            SET make = ?, model = ?, year = ?, color = ?, price = ?, mileage = ?
            WHERE vin = ?''',
            (car.make, car.model, car.year, car.color, car.price, car.mileage, car.vin))
            conn.commit()
        except sqlite3.Error:
            return False
        
        return True
    else:
        return False

def delete_car_from_db(car_id: str):
    if check_car_exists(car_id):
        try:
            cursor.execute('DELETE FROM cars WHERE vin = ?', (car_id,))
            conn.commit()
        except sqlite3.Error:
            return False
        
        return True
    else:
        return False

def print_all_cars():
    try:
        cursor.execute('SELECT * FROM cars')
        rows = cursor.fetchall()
        for row in rows:
            print(f"VIN: {row[0]}, Make: {row[1]}, Model: {row[2]}, Year: {row[3]}, Color: {row[4]}, Price: {row[5]}, Mileage: {row[6]}")
    except sqlite3.Error as e:
        print(f"Failed to retrieve cars: {e}")

def clear_cars_table():
    try:
        cursor.execute('DELETE FROM cars')
        conn.commit()
        print("Cars table cleared")
    except sqlite3.Error as e:
        print(f"Failed to clear cars table: {e}")

#clear_cars_table()
print_all_cars()

