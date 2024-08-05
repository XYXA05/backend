
import logging
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload
import models, schemas
from sqlalchemy import and_
from schemas import ItemCreate as ItemCreateSchema, ItemsCreateDescription as ItemsCreateDescriptionSchema



def get_user(db: Session, user_id: int):
    return db.query(models.UserCreate).filter(models.UserCreate.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.UserCreate).filter(models.UserCreate.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserCreate).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.hashed_password + "notreallyhashed"
    db_user = models.UserCreate(email=user.email, hashed_password=fake_hashed_password, title_company=user.title_company,
    adres=user.adres, lng=user.lng, lat=user.lat, year_of_foundation=user.year_of_foundation, houses_were_delivered=user.houses_were_delivered,
    houses_in_the_process=user.houses_in_the_process, in_the_process_suburban_type=user.in_the_process_suburban_type,
    suburban_type=user.suburban_type, website=user.website, phone=user.phone, weekdays=user.weekdays, weekend=user.weekend, is_active=user.is_active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


############

def get_news_for_id_user(db: Session, item_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.UserCreate_News).filter(models.UserCreate_News.owner_id == item_id).offset(skip).limit(limit).all()

def create_user_create_news(db: Session, item: schemas.UserCreate_Newss, user_id: int):
    db_item = models.UserCreate_News(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
############


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ItemCreate).offset(skip).limit(limit).all()

def get_item_id(db: Session, item_id: int):
    return db.query(models.ItemCreate).filter(models.ItemCreate.id == item_id).first()

def get_items_id(db: Session, item_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ItemCreate).filter(models.ItemCreate.owner_id == item_id).offset(skip).limit(limit).all()


def get_user_about_items(db: Session, item_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ItemCreate_about).filter(models.ItemCreate_about.new_build_apartment_id == item_id).offset(skip).limit(limit).all()


def create_user_about_items(db: Session, item: schemas.ItemCreate_about, user_id: int):
    db_item = models.ItemCreate_about(**item.dict(), new_build_apartment_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item



def create_user_item_description(db: Session, item: schemas.ItemsCreateDescription, user_discription_id: int):
    db_item = models.ItemsCreateDescription(**item.dict(), new_build_apartment_id=user_discription_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_descriptions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ItemsCreateDescription).offset(skip).limit(limit).all()

def get_descriptions_id(db: Session, item_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ItemsCreateDescription).filter(models.ItemsCreateDescription.new_build_apartment_id == item_id).offset(skip).limit(limit).all()


def create_user_item_document(db: Session, item: schemas.Documents_title, user_document_id: int):
    db_item = models.Documents_title(**item.dict(), new_build_apartment_id=user_document_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_document(db: Session, user_document_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Documents_title).filter(models.Documents_title.new_build_apartment_id== user_document_id).offset(skip).limit(limit).all()




def create_user_item_document_description(db: Session, item: schemas.Documents_Terms_of_financing, user_document_id: int):
    item_dict = item.dict()
    item_dict['new_build_apartment_id'] = user_document_id
    db_item = models.Documents_Terms_of_financing(**item_dict)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_document_description(db: Session, user_document_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Documents_Terms_of_financing).filter(models.Documents_Terms_of_financing.new_build_apartment_id == user_document_id).offset(skip).limit(limit).all()

def filter_items_by_description(
    db: Session,
    min_price_one_meter: Optional[int] = None,
    max_price_one_meter: Optional[int] = None,
    min_all_meter_in_item: Optional[int] = None,
    max_all_meter_in_item: Optional[int] = None,
    min_all_price_items: Optional[int] = None,
    max_all_price_items: Optional[int] = None,
    type_items: Optional[str] = None,
    input_term: Optional[str] = None,
    state: Optional[str] = None,
    floors: Optional[str] = None,
    apartment_condition: Optional[str] = None,
    construction_status: Optional[str] = None,
    declared_commissioning: Optional[str] = None,
    housing_condition: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.ItemCreate]:
    query = db.query(models.ItemCreate).outerjoin(models.ItemsCreateDescription)

    if min_price_one_meter is not None and max_price_one_meter is not None:
        query = query.filter(models.ItemsCreateDescription.price_one_meter.between(min_price_one_meter, max_price_one_meter))
    elif min_price_one_meter is not None:
        query = query.filter(models.ItemsCreateDescription.price_one_meter >= min_price_one_meter)
    elif max_price_one_meter is not None:
        query = query.filter(models.ItemsCreateDescription.price_one_meter <= max_price_one_meter)

    if min_all_meter_in_item is not None and max_all_meter_in_item is not None:
        query = query.filter(models.ItemsCreateDescription.all_meter_in_item.between(min_all_meter_in_item, max_all_meter_in_item))
    elif min_all_meter_in_item is not None:
        query = query.filter(models.ItemsCreateDescription.all_meter_in_item >= min_all_meter_in_item)
    elif max_all_meter_in_item is not None:
        query = query.filter(models.ItemsCreateDescription.all_meter_in_item <= max_all_meter_in_item)

    if min_all_price_items is not None and max_all_price_items is not None:
        query = query.filter(models.ItemsCreateDescription.all_price_items.between(min_all_price_items, max_all_price_items))
    elif min_all_price_items is not None:
        query = query.filter(models.ItemsCreateDescription.all_price_items >= min_all_price_items)
    elif max_all_price_items is not None:
        query = query.filter(models.ItemsCreateDescription.all_price_items <= max_all_price_items)

    if type_items:
        query = query.filter(models.ItemsCreateDescription.type_items == type_items)
    if input_term:
        query = query.filter(models.ItemsCreateDescription.input_term == input_term)
    if state:
        query = query.filter(models.ItemsCreateDescription.state == state)
    if floors:
        query = query.filter(models.ItemsCreateDescription.floors == floors)
    if apartment_condition:
        query = query.filter(models.ItemCreate.apartment_condition == apartment_condition)
    if construction_status:
        query = query.filter(models.ItemCreate.class_bulding == construction_status)
    if declared_commissioning:
        query = query.filter(models.ItemsCreateDescription.input_term == declared_commissioning)
    if housing_condition:
        query = query.filter(models.ItemsCreateDescription.state == housing_condition)

    return query.offset(skip).limit(limit).all()