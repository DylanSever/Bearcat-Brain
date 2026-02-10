#Dylan Sever 2/5/2026
#This program allows for the writinng to a MySQL 9 database
import mysql.connector
from mysql.connector import Error
from datetime import datetime

#prevent any critical information about the database from being publicly viewable in GitHub
try:
    from private import DB_CONFIG
except ImportError:
    #warn user Database isnt connected
    print("ERROR: Some critical components can't be imported. Ask a team member for assistance.")
    DB_CONFIG = {}

def create_connection():
    #Establish Connection to MySQL Database
    try:
        connection= mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error:
    #if the server is down or not responding return nothing
            return None

def log_interaction(user_input, ai_response, source_file="None"):
    #begin connection to database
    conn = create_connection()
    #check if database is connected
    if not conn:
        print("      (Note: Chat Not saved - Database disconnected)")
        return

    try:
        cursor = conn.cursor()
    # SQL command to insert chat log data into database
        query = """
        INSERT INTO chat_logs (sender, message_content, relevant_doc_source, timestamp)
        VALUES (%s, %s, %s, %s)
        """
    #this will log the users message. none is the source as this is useful for the ai reply.
        cursor.execute(query, ('user', user_input, None, datetime.now()))
    #this will log the AIs response. the source file tells what type of document the information came from.
        cursor.execute(query, ('bearcat_brain', ai_response, source_file, datetime.now()))
    #commit change and save it into the database
        conn.commit()
        print("   (chat logged to MySQL!)")


    except Error as e:
        print(f"    (error logging to DB: {e})")
    finally:
    #end connections when finished
        if conn.is_connected():
            cursor.close()
            conn.close()
