import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:GRO41iFNZsp9lS7OidOEafx5Y6GPD1S2Guu6Q279mJGBy7JYeoT14EffDarZL5f6@167.71.42.178:5432/default?charset=utf8mb4"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()