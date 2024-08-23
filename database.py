import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:3ZXwD21Xk9uMao9Z7BJPu3WHKPzh2oElCoUvLxMXFp7X0hrOHWLRJYCO9yqpmQxv@167.71.42.178:5432/default?charset=utf8mb4"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=280,
    pool_pre_ping=True  # Checks the connection before using it
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()