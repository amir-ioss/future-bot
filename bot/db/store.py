import sqlite3
import json
import os
from datetime import datetime, timedelta

class Store:
    def __init__(self, db_name='database.db'):
        # Specify the full path to the database file
        db_path = os.path.join(os.path.dirname(__file__), db_name)  # Creates the path in the db/ directory
        #otherwise it will created where the main file called dir :)
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def _User(self):

        # 3. Create a table
        self.cursor.execute('''
            CREATE TABLE users (
            username varchar(255) NOT NULL UNIQUE,
            api_key varchar(255) NOT NULL,
            api_secret varchar(255) NOT NULL
            );
        ''')

        users = [
        {
                'username': 'amir',
                'api_key': 'h5J8MK5WP5t2DKADpFvOhoE98chuKJxsSB7ny239DWaO49amJmkmzFgus7wEZPpH',        
                'api_secret': 'JEk6zkYmIrwOS1JswoIdPfwndqpfXRsfc00dS4F8rJS6c93qa8PRpLecOpCc8peb'
            },
            {
                'username': 'shuhaib',
                'api_key': '1Cno4uAqF0XMZ5nNTCy2wSXL7wG4cXypnNVGnXdtELkadzhr0N2TJANVVqCRG7yV',        
                'api_secret': 'Sc96uxWOVP2XboZZgsIOEASoaEnq1spMMTpUx1axvV2noZ3tAbPGkRBhpE4SAhVQ'
            }
        ]


        # Insert each user from the array into the table
        for user in users:
            self.cursor.execute('''
                INSERT INTO users (username, api_key, api_secret) VALUES (?, ?, ?)
            ''', (user["username"], user["api_key"], user["api_secret"]))

        # Commit the transaction to save the data
        self.conn.commit()



        # 4. Insert data
        # self.cursor.execute('INSERT INTO users (username, age) VALUES (?, ?)', ('Alice', 25))
        # conn.commit()  # Save (commit) the changes

        # 5. Query the data
        self.cursor.execute('SELECT * FROM users')
        rows = self.cursor.fetchall()

        # 6. Print out the results
        for row in rows:
            print(row)

        # 7. Update a user's age
        # self.cursor.execute('UPDATE users SET age = ? WHERE name = ?', (26, 'Alice'))
        # conn.commit()

        # 8. Delete a user
        # self.cursor.execute('DELETE FROM users WHERE name = ?', ('Bob',))
        # conn.commit()

    
    def _State(self):

        # 3. Create a table
        self.cursor.execute('''
            CREATE TABLE states (
            scalp TEXT,
            swing TEXT
            );
        ''')
        sample_object = {
            'status': False,
            # 'preferences': ['news', 'music', 'movies']
        }
        # Insert the JSON string into the database
        self.cursor.execute('INSERT INTO states (scalp) VALUES (?)', (json.dumps(sample_object),))
        # Commit the transaction
        self.conn.commit()


    def setState(self, state, obj):
        dict1 = self.getState(state)
        dict2 = obj
        combined_dict = {**dict1, **dict2}

        # Dynamically build the query string with the column name (row)
        query = f'UPDATE states SET {state} = ?'
        # Execute the query, safely inserting the JSON-serialized object
        self.cursor.execute(query, (json.dumps(combined_dict),))
        # Commit the transaction to save the changes
        self.conn.commit()

    def getState(self, state):
        if not state: return []
        # Query the table to retrieve the JSON string
        self.cursor.execute(f'SELECT {state} FROM states')
        row = self.cursor.fetchone()
        return json.loads(row[0])

        # # # Convert the JSON string back to a Python object
        # for row in rows:
        #     if row == None: return
        #     obj = json.loads(row)
        #     print(f'Data: {obj}')


# E X A M P L E

    # _User()


    # _State()
    # setState('scalp', {'name': 'Job', 'car' : None})
    # state = getState('scalp')
    # print(state)



    # Delete 
    # self.cursor.execute('DELETE FROM states WHERE name = ?', ('Bob',))
    # conn.commit()



    # 9. Close the connection
    # conn.close()

    def test(self):
        # self.cursor.execute(f'SELECT * FROM states')
        # row = self.cursor.fetchone()
        return 



store = Store()
state = store.getState('scalp')

# store.setState('scalp', {'SL':[{'ADA/USDT': 1729675760, 'type': 'LONG'}, {'SOL/USDT': 1729675760, 'type': 'SHORT'}]})
# key_exists = any('SOL/USDT' in item for item in state['SL'])


def checkInSL(sls, symbol, type, past = 30):
    inSL = False
    timePassed = False
    # Iterate through the list in 'SL'
    for item in sls:
        if symbol in item and item['type'] == type:
            inSL= True
            # Get the current time
            current_time = datetime.now()
            past_time = current_time - timedelta(minutes=30)  # Convert to seconds
            # past_time = item[symbol]

            # Calculate the difference
            difference = current_time - past_time
            # Check if 20 minutes have passed
            timePassed = difference <= timedelta(minutes=past)
            # print("Current time:", current_time)
            # print("Past time:", past_time)
            # print("Difference:", difference)
            break
    return inSL, timePassed
     

activeSymbol= 'ADA/USDT'

inSL, timePassed = checkInSL(state['SL'], activeSymbol, 'SHORT')

if inSL and not timePassed:
    print("wait")
elif inSL and timePassed:
    print("take new trade and remove from SL")
    state['SL'] = [elem for elem in state['SL'] if activeSymbol not in elem]
    store.setState('scalp', state)
else:
    print("take new trade")




# print(state)

