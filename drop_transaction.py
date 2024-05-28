from sqlalchemy import create_engine, MetaData, Table
from app import Transaction  # Import your Transaction model

# Create a SQLAlchemy engine to connect to the database
engine = create_engine('sqlite:///instance/transactions.db', echo=True)

# Create a MetaData object
metadata = MetaData()

# Reflect the existing database into the MetaData object
metadata.reflect(bind=engine)

# Access the Transaction table
transaction_table = Table('transaction', metadata, autoload_with=engine)

# Drop the Transaction table
transaction_table.drop(engine)

print("Transaction table deleted.")
