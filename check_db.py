import lancedb
import os

# Get the database path
db_path = os.environ.get("SOLAR_SAGE_VECTOR_DB_PATH", "./data/lancedb")
table_name = os.environ.get("SOLAR_SAGE_VECTOR_DB_TABLE", "solar_knowledge")

print(f"Checking database at {db_path} with table {table_name}")

try:
    # Connect to the database
    db = lancedb.connect(db_path)

    # Check if the table exists
    if table_name in db.table_names():
        print(f"Table {table_name} exists")

        # Open the table
        table = db.open_table(table_name)

        # Get the count of records
        count = len(table.to_pandas())
        print(f"Table {table_name} has {count} records")

        # Get a sample of records
        sample = table.to_pandas().head(2)
        print("\nSample records:")
        print("Columns:", sample.columns.tolist())
        print(sample.to_string())
    else:
        print(f"Table {table_name} does not exist")
except Exception as e:
    print(f"Error: {e}")
