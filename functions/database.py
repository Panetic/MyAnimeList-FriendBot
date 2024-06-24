import sqlite3

class Database:
    def __init__(self):
        self.db = sqlite3.connect("Users.db")
        self.cursor = self.db.cursor()
        self._create_users_table_if_not_exists()

    def _create_users_table_if_not_exists(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT NOT NULL UNIQUE
            )
        ''')
        self.db.commit()

    def user_check(self, users: list) -> list:
        # Convert list to tuple for SQL query
        users_tuple = tuple(users)

        # Retrieve users that are in the database
        query = "SELECT username FROM users WHERE username IN ({seq})".format(
            seq=','.join(['?']*len(users_tuple))
        )
        self.cursor.execute(query, users_tuple)
        found_users = self.cursor.fetchall()
        
        # Flatten the list of tuples to a list of strings
        found_users = [user[0] for user in found_users]

        # Create a new list excluding the found users
        new_users = [user for user in users if user not in found_users]
        
        return new_users

    def add_user(self, username: str):
        try:
            self.cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            self.db.commit()
        except sqlite3.IntegrityError:
            print(f"User '{username}' already exists in the database.")

    def add_all_users(self, users: list):
        try:
            # Prepare data for bulk insertion
            data = [(user,) for user in users]

            # Execute bulk insert with INSERT OR IGNORE
            self.cursor.executemany("INSERT OR IGNORE INTO users (username) VALUES (?)", data)

            # Commit the transaction
            self.db.commit()

            # Count successful insertions (excluding duplicates)
            rows_affected = self.cursor.rowcount
            print(f"{rows_affected} users added successfully.")

        except Exception as e:
            # Handle other exceptions
            print(f"Error occurred: {e}")

    def __del__(self):
        self.db.close()

# Example usage:
if __name__ == "__main__":
    db = Database()
    
    # Add some users to the database
    db.add_user("Alice")
    db.add_user("Bob")
    db.add_user("Charlie")
    
    # Check users against the database
    users_to_check = ["Alice", "David", "Charlie", "Eve"]
    new_users = db.user_check(users_to_check)
    print("New users:", new_users)  # Output should be: ['David', 'Eve']
