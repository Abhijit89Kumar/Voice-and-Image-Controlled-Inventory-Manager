import logging
import mysql.connector

# Establish connection to MySQL server
conn = mysql.connector.connect(
    host="localhost",
    user="debian-sys-maint",
    password="wsjj1GKuAFcAb9d0",
    database="inventory"
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

def delete_object_from_object_mapping(self, object_name=None, object_id=None):
        try:
            if object_name:
                query = "DELETE FROM object_mapping WHERE object_name = %s"
                cursor.execute(query, (object_name,))
            elif object_id:
                query = "DELETE FROM object_mapping WHERE object_id = %s"
                cursor.execute(query, (object_id,))
            else:
                print("Error: Either object name or object ID must be provided.")
                return
            conn.commit()
            print("Object deleted successfully.")
        except mysql.connector.Error as err:
            print("Error:", err)

def delete_inventory_item(object_id):
    result = {'success': False, 'message': ''}

    try:
        # Delete the inventory item with the specified object ID
        query = "DELETE FROM inventory WHERE id = %s"
        cursor.execute(query, (object_id,))
        conn.commit()

        if cursor.rowcount == 0:
            result['message'] = f"Object with ID {object_id} not found in inventory."
            logging.error(result['message'])
            return result

        result['success'] = True
        result['message'] = f"Inventory item with ID {object_id} deleted successfully."
        logging.info(result['message'])
    except mysql.connector.Error as err:
        logging.error(err)
        result['message'] = "Error deleting inventory item."

    return result

delete_inventory_item(1)


try:
    # query = "DELETE FROM object_mapping WHERE object_name = %s"
    # cursor.execute(query, (object_name,))
    pass
except mysql.connector.Error as err:
    print("Error:", err)
    
finally:
    # Close cursor and connection
    cursor.close()
    conn.close()    
    
