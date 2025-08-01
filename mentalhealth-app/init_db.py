# init_db.py
from database import engine
from models import Base  # Import models to register them with SQLAlchemy

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")