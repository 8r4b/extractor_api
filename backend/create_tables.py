from database import engine, Base
import models  # Ensure all models are imported so they are registered

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully")
