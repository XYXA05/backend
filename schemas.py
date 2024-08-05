from typing import Optional, List
from pydantic import BaseModel
class Description(BaseModel):
    type_items: str
    price_one_meter: int
    all_meter_in_item: int
    all_price_items : int
    namber_build_andsection: str
    floors: str
    state: str
    input_term: str
    Features : str
    link: str

class ItemsCreateDescription(Description):
    pass

class ItemDescription(Description):

    id: int
    new_build_apartment_id: int

    class Config:
        orm_mode = True
class ItemBase(BaseModel):
    title: str
    position: int
    description: List[ItemDescription]  # Change to list
    description_text: Optional[str] = None
    price_hi: int
    price_low: int
    city: str
    line_adres: str
    class_bulding: str
    houses: int
    number_of_storeys: int
    construction_technology: str
    walls: str
    insulation: str
    heating: str
    ceiling_height: str
    number_of_flats: int
    apartment_condition: str
    territory: str
    car_park: str
    lng: str
    lat: str
class ItemCreate(ItemBase):
    pass

class Item(ItemBase):

    id: int
    owner_id: int


    class Config:
        orm_mode = True




class ItemCreate_about(BaseModel):
    id: int
    link: str
    dascription: str

class ItemCreate_abouts(ItemCreate_about):
    pass

class item_ItemCreate_about(ItemCreate_about):
    id: int
    new_build_apartment_id: int

    class Config:
        orm_mode = True


class Documents_title(BaseModel):
    title: str
    text: str
    link: str

class Documents_titles(Documents_title):
    pass

class Documents_title_create(Documents_title):

    id: int
    new_build_apartment_id: int

    class Config:
        orm_mode = True

class Documents_Terms_of_financing(BaseModel):
    title: str
    text: str
    link: str

class Documents_Terms_of_financings(Documents_Terms_of_financing):
    pass

class Documents_Terms_of_financing_create(Documents_Terms_of_financing):
    id: int
    new_build_apartment_id: int
    class Config:
        orm_mode = True

    
class UserBase(BaseModel):
    email: str

class UserCreate(BaseModel):
    title_company: str
    phone: str
    email: str
    adres: str
    lng: str
    lat: str
    hashed_password: str
    year_of_foundation: int
    houses_were_delivered: int
    houses_in_the_process: int
    in_the_process_suburban_type: int
    suburban_type: int
    website: str
    weekdays: str
    weekend: str
    is_active: bool


class User(UserBase):
    id: int
    is_active: bool
    title_company: str
    phone: str
    email: str
    adres: Optional[str] = None
    lng: str
    lat: str
    year_of_foundation: Optional[int] = None
    houses_were_delivered: Optional[int] = None
    houses_in_the_process: Optional[int] = None
    in_the_process_suburban_type: Optional[int] = None
    suburban_type: Optional[int] = None
    website: Optional[str] = None
    weekdays: Optional[str] = None
    weekend: Optional[str] = None
    items: List[Item] = []

    class Config:
        orm_mode = True


class UserCreate_News(BaseModel):
    title: str
    date: str
    text: str
    link:str

class UserCreate_Newss(UserCreate_News):
    pass

class UserCreate_News_Create(UserCreate_News):

    id: int
    owner_id: int

    class Config:
        orm_mode = True








