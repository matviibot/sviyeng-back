import uvicorn
from fastapi import FastAPI, HTTPException
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Add the URLs of your client applications
    "https://www.sviyeng.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Connect to MySQL
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password',
    database='svyieng'  # Add the name of your database
)

cursor = cnx.cursor()

# Check if the database exists
cursor.execute("SHOW DATABASES LIKE 'svyieng'")
database_exists = cursor.fetchone() is not None

if not database_exists:
    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE svyieng")
    cnx.commit()

# Use the database
cursor.execute("USE svyieng")

# Check if the table exists
cursor.execute("SHOW TABLES LIKE 'users'")
table_exists = cursor.fetchone() is not None

if not table_exists:
    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            password VARCHAR(100) NOT NULL
        )
    ''')
    cnx.commit()


@app.post("/login")
def login(data: dict):
    email = data.get('email')
    password = data.get('password')

    try:
        # Retrieve the user from the database based on the provided email
        query = "SELECT password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        stored_password = result[0]

        if password == stored_password:
            return {"message": "Login successful", "success": True}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail="Failed to retrieve user: " + str(error))


@app.post("/register")
def create_user(data: dict):
    try:
        print(data["name"], data["last_name"], data["email"], data["password"])
        query = "INSERT INTO users (name, last_name, email, password) VALUES (%s, %s, %s, %s)"
        values = (data["name"], data["last_name"], data["email"], data["password"])
        cursor.execute(query, values)
        cnx.commit()
        return {"message": "User created successfully", "success": True}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail="Failed to create user: " + str(error))


if __name__ == "__main__":
    cursor.execute("use svyieng")
    uvicorn.run(app, host="localhost", port=8000)
