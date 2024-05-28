from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Transaction  # Import your Transaction model

# Create a SQLAlchemy engine to connect to the database
engine = create_engine('sqlite:///instance/transactions.db', echo=True)

# Create a session factory
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# Clear all data from the Transaction table
session.query(Transaction).delete()

# Commit the changes
session.commit()

# Close the session
session.close()

print("All data cleared from the Transaction table.")
