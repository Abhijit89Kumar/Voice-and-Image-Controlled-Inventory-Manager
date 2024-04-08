import mysql.connector

# Establish connection to MySQL server
conn = mysql.connector.connect(
    host="localhost",
    user="debian-sys-maint",
    password="wsjj1GKuAFcAb9d0"
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

try:
    cursor.execute("CREATE DATABASE IF NOT EXISTS inventory")
    # Switch to the newly created database
    cursor.execute("USE inventory")
    
    # Create inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        object_name VARCHAR(100) NOT NULL,
        items INT NOT NULL
    )
    """)

    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        object_id BIGINT,
        object_name VARCHAR(100) NOT NULL,
        transaction_type ENUM('in', 'out') NOT NULL,
        items_qty INT NOT NULL,
        transaction_date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create object_mapping table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS object_mapping (
        object_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        object_name VARCHAR(100) NOT NULL
    )
    """)

    print("Database tables created successfully!")

    # Get list of all tables in the database
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # Iterate over each table
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")

        # Get column names for the current table
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()

        # Print column names
        for column in columns:
            column_name = column[0]
            print(f"- {column_name}")

        print()  # Add a newline between tables

    
except mysql.connector.Error as err:
    print("Error:", err)
      
    
finally:
    # Close cursor and connection
    cursor.close()
    conn.close()    
    
