import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Category  # Import your Category model here

# Database configuration
SQLALCHEMY_DATABASE_URL = 'sqlite:///./database.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Read data from the CSV file
csv_file_path = 'categories.csv'  # Replace with the path to your CSV file

with open(csv_file_path, 'r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    # Create a session
    db = SessionLocal()
    
    for row in csv_reader:
        # Create Category objects for each row
        category = Category(
            category_name=row['category_name'],
            category_description=row['category_description'],
            parent_category_id=row['parent_category_id']
        )
        
        # Add the Category object to the session
        db.add(category)
    
    # Commit the changes to the database
    db.commit()

    # Close the session
    db.close()
