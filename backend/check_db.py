from backend.database import check_database_connection

if check_database_connection():
    print("NEXUS database connection successful!")
