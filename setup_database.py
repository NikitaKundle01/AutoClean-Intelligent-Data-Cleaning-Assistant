from modules.db_handler import DBHandler
import mysql.connector

def setup_database():
    # Read the SQL file
    with open('database/db_setup.sql', 'r') as file:
        sql_script = file.read()
    
    # Split into individual statements
    statements = sql_script.split(';')
    
    # Connect to MySQL (without specifying a database)
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='yourpassword'
    )
    cursor = conn.cursor()
    
    # Execute each statement
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
            except mysql.connector.Error as err:
                print(f"Error executing statement: {err}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()