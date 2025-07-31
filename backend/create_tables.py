from app.database import Base, engine
from app.products.models import Product
from app.settings.models import UserSettings  

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
