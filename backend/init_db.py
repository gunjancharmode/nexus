
from backend.database import engine
from backend.models import Base, Customer

Base.metadata.create_all(bind=engine)

print("NEXUS database tables created successfully!")
print("Tables:", list(Base.metadata.tables.keys()))
