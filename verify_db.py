import sqlalchemy
from sqlalchemy import create_engine, text
import os

db_path = r"d:\ems1\instance\database.db"
engine = create_engine(f"sqlite:///{db_path}")

with engine.connect() as connection:
    result = connection.execute(text("SELECT username FROM users"))
    for row in result:
        print(f"User: {row[0]}")
