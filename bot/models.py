from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class BloodSugar(Base):
    __tablename__ = 'blood_sugar_readings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    blood_glucose_value = Column(Float, nullable=False)
    blood_description = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)


engine = create_engine('sqlite:///blood_sugar.db')

Base.metadata.create_all(engine)