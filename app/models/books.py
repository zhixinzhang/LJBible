from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# Define your data class
Base = declarative_base()

class books(Base):
    __tablename__ = 'books'

    id = Column(Integer, Sequence('person_id_seq'), primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    
    addresses = relationship("Address", back_populates="person")

