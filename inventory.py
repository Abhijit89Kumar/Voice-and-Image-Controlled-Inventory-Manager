import logging
import mysql.connector
import random
import datetime
from loggings import log_function_call

class InventoryManager:
    def __init__(self, host, username, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor(buffered=True)

    def generate_unique_id(self, object_name):
        # Calculate ASCII sum of characters in object name
        ascii_sum = ''.join(str(ord(char)) for char in object_name)

        # Increase the length of the ID by appending additional unique digits
        if len(ascii_sum) < 10:
            # Add unique digits at the end to make it 10 characters long
            ascii_sum += ''.join(str(random.randint(0, 9)) for _ in range(10 - len(ascii_sum)))

        # Take the first 10 characters
        unique_id = ascii_sum[:5]+ascii_sum[-5:]
        return unique_id
    
    def generate_transaction_id(self, object_name, current_datetime):
        # Concatenate object name and current date and time
        combined_string = f"{object_name}_{current_datetime}"

        # Calculate ASCII sum of characters in combined string
        ascii_sum = ''.join(str(ord(char)) for char in combined_string)

        # Increase the length of the ID by appending additional unique digits
        if len(ascii_sum) < 10:
            # Add unique digits at the end to make it 10 characters long
            ascii_sum += ''.join(str(random.randint(0, 9)) for _ in range(10 - len(ascii_sum)))

        # Take the first 10 characters
        transaction_id = ascii_sum[:5] + ascii_sum[-5:]

        return transaction_id
    

    @log_function_call
    def add_in_object_mapping(self, object_name):
        result = {'success': False, 'message': '', 'object_id': None}

        try:
            # Convert object name to lowercase
            object_name_lower = object_name.lower()

            # Check if the object name already exists in the table
            query = "SELECT COUNT(*) FROM object_mapping WHERE LOWER(object_name) = %s"
            self.cursor.execute(query, (object_name_lower,))
            count = self.cursor.fetchone()[0]

            if count > 0:
                result['message'] = "already exists"
                logging.info(f"Object '{object_name_lower}' already exists in object_mapping table.")
                return result

            # Generate unique ID
            unique_id = self.generate_unique_id(object_name_lower)

            # Insert into object_mapping table
            query = "INSERT INTO object_mapping (object_id, object_name) VALUES (%s, %s)"
            self.cursor.execute(query, (unique_id, object_name_lower))
            self.conn.commit()
            
            result['success'] = True
            result['message'] = "inserted"
            result['object_id'] = unique_id
            logging.info(f"Object '{object_name_lower}' added to object_mapping table with ID: {unique_id}")
        except mysql.connector.Error as err:
            logging.error(f"Object '{object_name_lower}', Error : {err}")
            result['message'] = "error"
        return result
    
    @log_function_call        
    def find_object_id(self, object_name):
        result = {'success': False, 'message': '', 'object_id': None}

        try:
            query = "SELECT object_id FROM object_mapping WHERE object_name = %s"
            self.cursor.execute(query, (object_name,))
            object_id = self.cursor.fetchone()
            if object_id:
                result['success'] = True
                result['message'] = f"Found"
                result['object_id'] = object_id[0]
                logging.info(f"Object ID found for '{object_name}'")
            else:
                result['message'] = f"Not Found"
                logging.info(f"Object '{object_name}' not found in object_mapping table.")
        except mysql.connector.Error as err:
            logging.error(err)
            result['message'] = "Error"
        return result
    
            
    def view_objects(self):
        result = {'success': False, 'message': '', 'objects': []}

        try:
            query = "SELECT object_id, object_name FROM object_mapping"
            self.cursor.execute(query)
            objects = self.cursor.fetchall()

            if objects:
                objects_list = []
                for obj_id, obj_name in objects:
                    objects_list.append({'object_id': obj_id, 'object_name': obj_name})
                result['objects'] = objects_list
                result['success'] = True
                result['message'] = "List of objects retrieved from object_mapping table"
                logging.info(result['message'])
            else:
                result['message'] = "No objects found in object_mapping table."
                logging.info(result['message'])
        except mysql.connector.Error as err:
            logging.error(err)
            result['message'] = "Error retrieving objects from object_mapping table."

        return result
            
    def add_transaction(self, object_name, transaction_type, items_qty):
        result = {'success': False, 'message': ''}

        try:
            

            # Add items to inventory for 'in' transaction
            if transaction_type == 'in':
                result = self.inventory_change(object_name, items_qty,change_type='update')
                if not result['success']:
                    logging.error(f"Error: {result['message']}")
                    return result

            elif transaction_type == 'out':
                # Check if there are sufficient items in inventory
                inventory_result = self.view_inventory(object_name)
                if not inventory_result['success']:
                    logging.error(f"Error: {inventory_result['message']}")
                    return inventory_result

                current_qty = inventory_result['inventory']['items_quantity']
                if current_qty < items_qty:
                    result['message'] = f"Insufficient inventory for '{object_name}'. Transaction not added."
                    logging.warning(result['message'])
                    return result
            
                result = self.inventory_change(object_name, -items_qty, change_type='update')
                if not result['success']:
                    logging.error(f"Error: {result['message']}")
                    return result

            # Find object ID
            object_id_result = self.find_object_id(object_name)
            object_id_data = object_id_result
            
            if not object_id_data['success']:
                logging.error(f"Object '{object_name}' not found. Transaction not added.")
                result['message'] = f"Object '{object_name}' not found. Transaction not added."
                return result
            # Get current date and time as string
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Generate transaction ID
            transaction_id = self.generate_transaction_id(object_name, current_datetime)
        
            # Insert into transactions table
            query = "INSERT INTO transactions (transaction_id, object_id, object_name, transaction_type, items_qty) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(query, (transaction_id, object_id_data['object_id'], object_name, transaction_type, items_qty))
            self.conn.commit()
            
            result['success'] = True
            result['message'] = "Transaction added successfully."
            logging.info("Transaction added successfully.")
        except mysql.connector.Error as err:
            logging.error(err)
            result['message'] = "Error occurred while adding transaction."

        return result
            
    def view_inventory(self, object_name=None):
        result = {'success': False, 'message': '', 'inventory': None}

        try:
            if object_name:
                # View inventory for a specific object
                query = "SELECT * FROM inventory WHERE object_name = %s"
                self.cursor.execute(query, (object_name,))
                inventory = self.cursor.fetchall()

                if inventory:
                    result['inventory'] = {
                        'object_id': inventory[0][0],
                        'object_name': inventory[0][1],
                        'items_quantity': inventory[0][2]
                    }
                    result['success'] = True
                    result['message'] = f"Inventory found for '{object_name}'"
                    logging.info(f"Inventory found for '{object_name}': {result['inventory']}")
                else:
                    result['message'] = f"No inventory found for '{object_name}'"
                    logging.info(result['message'])
            else:
                # View entire inventory
                query = "SELECT * FROM inventory"
                self.cursor.execute(query)
                inventory = self.cursor.fetchall()

                if inventory:
                    inventory_list = []
                    for item in inventory:
                        inventory_list.append({
                            'object_id': item[0],
                            'object_name': item[1],
                            'items_quantity': item[2]
                        })
                    result['inventory'] = inventory_list
                    result['success'] = True
                    result['message'] = "Entire inventory retrieved"
                    logging.info("Entire inventory retrieved")
                else:
                    result['message'] = "Inventory is empty"
                    logging.info("Inventory is empty")
        except mysql.connector.Error as err:
            logging.error(err)
            result['message'] = "Error retrieving inventory"

        return result
            
    def inventory_change(self, object_name, items, change_type='update'):
        result = {'success': False, 'message': ''}

        try:
            # Check if the object exists in the object_mapping table
            object_id_result = self.find_object_id(object_name)
            object_id_data = object_id_result
            
            if object_id_data['success']:
                object_id = object_id_data['object_id']
            else:
                # Add the object to the object_mapping table
                add_object_result = self.add_in_object_mapping(object_name)
                add_object_data = add_object_result
                
                if not add_object_data['success']:
                    result['message'] = add_object_data['message']
                    return result
                
                object_id = add_object_data['object_id']

            # Check if the object already exists in the inventory
            query = "SELECT items FROM inventory WHERE id = %s"
            self.cursor.execute(query, (object_id,))
            current_items_row = self.cursor.fetchone()

            if current_items_row is None:
                current_items = 0
            else:
                current_items = current_items_row[0]

            # Perform the specified type of change
            if change_type == 'update':
                new_items = current_items + items
            elif change_type == 'set':
                new_items = items
            else:
                raise ValueError("Invalid change type. Supported values are 'update' or 'set'.")

            # Update or insert into the inventory
            if current_items_row is None:
                # If the object doesn't exist in inventory, insert a new row
                query = "INSERT INTO inventory (id, object_name, items) VALUES (%s, %s, %s)"
                self.cursor.execute(query, (object_id, object_name, new_items))
            else:
                # If the object exists in inventory, update the items count
                query = "UPDATE inventory SET items = %s WHERE id = %s"
                self.cursor.execute(query, (new_items, object_id))
                
            self.conn.commit()
            logging.info(f"Inventory updated for '{object_name}', Quantity: {new_items}, Change type: {change_type}")
            result['success'] = True
            result['message'] = "Inventory updated successfully"
        except mysql.connector.Error as err:
            logging.error(err)
            result['message'] = f"Error updating inventory for object: {object_name}"

        return result  
    
    def view_last_n_days_transactions(self, n_days):
        result = {'success': False, 'message': '', 'transactions': []}

        try:
            # Calculate the date N days ago
            n_days_ago = datetime.datetime.now() - datetime.timedelta(days=n_days)

            # Query to select transactions from the last N days
            query = "SELECT * FROM transactions WHERE transaction_date_time >= %s ORDER BY transaction_date_time DESC"
            self.cursor.execute(query, (n_days_ago,))
            transactions = self.cursor.fetchall()

            if transactions:
                transactions_list = []
                for transaction in transactions:
                    transaction_id, object_id, object_name, transaction_type, items_qty, transaction_date_time = transaction
                    transactions_list.append({
                        'transaction_id': transaction_id,
                        'object_id': object_id,
                        'object_name': object_name,
                        'transaction_type': transaction_type,
                        'items_qty': items_qty,
                        'transaction_date_time': transaction_date_time
                    })
                result['transactions'] = transactions_list
                result['success'] = True
                result['message'] = f"Last {n_days} days transactions retrieved."
                logging.info(result['message'])
            else:
                result['message'] = f"No transactions found in the last {n_days} days."
                logging.info(result['message'])
        except mysql.connector.Error as err:
            logging.error(err)
            result['message'] = "Error retrieving transactions."

        return result
     
inventory_manager = InventoryManager(host  = "localhost", username="debian-sys-maint", password="wsjj1GKuAFcAb9d0", database = "inventory")

# print(inventory_manager.add_in_object_mapping("Real Juice"))

# print(inventory_manager.find_object_id("Marie Gold Biscuits"))

# inventory_manager.add_object_mapping("Bru Instant Coffee")

# inventory_manager.find_object_id(object_name="Marie Gold Biscuits")
# inventory_manager.find_object_id(object_name="Bru Instant Coffee")

# print(inventory_manager.view_objects())

# print(inventory_manager.add_transaction(object_name="Tea", transaction_type = "out", items_qty=20))

# print(inventory_manager.view_last_n_days_transactions(n_days=7))
# print(inventory_manager.view_inventory(object_name="Marie Gold Biscuits"))

# print(inventory_manager.inventory_change("Milton Bottle", 100, change_type='set'))
print(inventory_manager.view_inventory())
# inventory_manager.view_inventory()