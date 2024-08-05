from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, ForeignKeyConstraint
from database import Base
from typing import List, Union
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class UserCreate(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    title_company = Column(String(50), unique=True, index=True)
    phone = Column(String(15), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    adres = Column(String(200), index=True)
    lng = Column(String(30), index=True)
    lat = Column(String(30), index=True)
    hashed_password = Column(String(255))
    year_of_foundation = Column(Integer, index=True)
    houses_were_delivered =Column(Integer, index=True)
    houses_in_the_process = Column(Integer, index=True)
    in_the_process_suburban_type = Column(Integer, index=True)
    suburban_type = Column(Integer, index=True)
    website = Column(String(60), index=True)
    weekdays = Column(String(20), index=True)
    weekend = Column(String(20), index=True)
    is_active = Column(Boolean, default=True)

    items = relationship("ItemCreate", back_populates="owner")
    files = relationship("UserCreate_File", back_populates="owner")
    news = relationship("UserCreate_News", back_populates="owner")


class UserCreate_News(Base):
    __tablename__ = "UserCreate_News"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    date = Column(String(30), index=True) 
    text = Column(String(255), nullable=False)
    link = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("UserCreate", back_populates="news")
   


class ItemCreate(Base):
    __tablename__ = "new_build_apartment"

    id = Column(Integer, primary_key=True)
    position = Column(Integer(), index=True)
    title = Column(String(30), index=True)
    description_text = Column(String(4000), index=True)
    price_hi = Column(Integer, index=True)
    price_low =Column(Integer, index=True)
    city = Column(String(30), index=True)
    line_adres = Column(String(40), index=True)
    class_bulding = Column(String(20), index=True)
    houses = Column(Integer, index=True)
    number_of_storeys = Column(Integer, index=True)
    construction_technology = Column(String(20), index=True)
    walls = Column(String(25), index=True)
    insulation = Column(String(30), index=True)
    heating = Column(String(40), index=True)
    ceiling_height = Column(String(30), index=True)
    number_of_flats= Column(Integer, index=True)
    apartment_condition = Column(String(30), index=True)
    territory = Column(String(30), index=True)
    car_park = Column(String(20), index=True)
    lng = Column(String(30), index=True)
    lat = Column(String(30), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("UserCreate", back_populates="items")
    files = relationship("File_new_build_apartment", back_populates="new_build_apartment")
    description = relationship("ItemsCreateDescription", back_populates="new_build_apartment")
    about = relationship("ItemCreate_about", uselist=False, back_populates="item_create")
    aerial_survey = relationship("File_new_build_apartment_aerial_survey_360", back_populates='apartment_aerial')
    documents_title = relationship('Documents_title', back_populates='documents')
    d3_object = relationship('User_3D_File_model', back_populates='User_3D_File')
    terms_of_financing = relationship('Documents_Terms_of_financing', back_populates='Terms_of_financing')

class ItemCreate_about(Base):
    __tablename__ = "new_build_apartment_about"

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String(100), nullable=False)
    dascription = Column(String(50), index=True)


    new_build_apartment_id = Column(Integer, ForeignKey("new_build_apartment.id"))
    files = relationship("File_new_build_apartment_ItemCreate_about", back_populates="item_create_about")
    item_create = relationship("ItemCreate", back_populates="about")

class ItemsCreateDescription(Base):
    __tablename__ = "new_build_apartment_description"

    id = Column(Integer, primary_key=True, index=True)
    type_items = Column(String(20), index=True)
    price_one_meter = Column(Integer(), index=True)
    all_meter_in_item = Column(Integer(),index=True)
    all_price_items = Column(Integer(), index=True)

    namber_build_andsection = Column(String(25), index=True)
    floors = Column(String(10), index=True)
    state = Column(String(30), index=True)
    input_term = Column(String(15), index=True)
    Features = Column(String(30), index=True)
    link = Column(String(255), index=True)
    new_build_apartment_id = Column(Integer, ForeignKey("new_build_apartment.id"))


    files = relationship("File_description", back_populates="new_build_apartment")
    new_build_apartment = relationship("ItemCreate", back_populates="description")



class Documents_title(Base):
    __tablename__ = "Documents_title"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    text = Column(String(300), index=True)
    link = Column(String(300), index=True)

    new_build_apartment_id = Column(Integer, ForeignKey("new_build_apartment.id"))

    documents = relationship("ItemCreate", back_populates="documents_title")


class Documents_Terms_of_financing(Base):
    __tablename__ = "Documents_Terms_of_financing"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    text = Column(String(255), index=True)
    link = Column(String(255), index=True)

    new_build_apartment_id = Column(Integer, ForeignKey("new_build_apartment.id"))

    Terms_of_financing = relationship("ItemCreate", back_populates="terms_of_financing")
