from fastapi import Depends, APIRouter, Form, HTTPException, File, Query, UploadFile, logger
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
import crud, schemas, models
from database import SessionLocal, engine
import shutil
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/userss/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/user/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/get_news_id/{user_id}", response_model=List[schemas.UserCreate_News])
def read_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_news_for_id_user(db, item_id=user_id, skip=skip, limit=limit)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_item
@router.post("/create_news_/{user_id}", response_model=schemas.UserCreate_News_Create)
def create_user_news(user_id: int, item: schemas.UserCreate_News, db: Session = Depends(get_db)):
    created_news = crud.create_user_create_news(db=db, item=item, user_id=user_id)
    return created_news


@router.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):  
    created_item = crud.create_user_item(db=db, item=item, user_id=user_id)
    return created_item

@router.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@router.get("/items/{item_id}", response_model=schemas.Item)
def read_user(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item_id(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_item


@router.get("/get_items/{item_id}", response_model=List[schemas.Item])
def read_user(item_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_items_id(db, item_id=item_id, skip=skip, limit=limit)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_item
##
@router.post("/item_for_document_description/{user_id}", response_model=schemas.Documents_Terms_of_financing)
def create_item_for_about(user_id: int, item: schemas.Documents_Terms_of_financing, db: Session = Depends(get_db)):
    created_item = crud.create_user_item_document_description(db=db, item=item, user_document_id=user_id)
    return created_item

@router.get("/get_items_for_document_description/{user_document_id}", response_model=List[schemas.Documents_Terms_of_financing])
def read_user(user_document_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_document_description(db, user_document_id=user_document_id, skip=skip, limit=limit)
    if not db_item:
        raise HTTPException(status_code=404, detail="Items not found")
    return db_item

@router.get("/get_items_for_about/{item_id}", response_model=List[schemas.ItemCreate_about])
def read_user(item_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_user_about_items(db, item_id=item_id, skip=skip, limit=limit)
    if not db_item:
        raise HTTPException(status_code=404, detail="Items not found")
    return db_item

@router.post("/upload_file_about/{user_id}", response_model=schemas.File_new_build_apartment_ItemCreate_abouts)
async def upload_multiple_files_compan(
    user_id: int,
    files: List[UploadFile],
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = await crud.upload_file_about(db, files, user_id)
    return uploaded_files

@router.get("/get_image_about/{item_create_about_id}")
async def get_image_owner( item_create_about_id: int, db: Session = Depends(get_db)):
    file_path = crud.get_image_item_path_by_position_and_id(db, item_create_about_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='image/jpeg') 






@router.post("/item_for_document/{user_id}", response_model=schemas.Documents_title)
def create_item_for_about(user_id: int, item: schemas.Documents_title, db: Session = Depends(get_db)):  
    created_item = crud.create_user_item_document(db=db, item=item, user_document_id=user_id)
    return created_item
@router.get("/get_items_for_document/{user_document_id}", response_model=List[schemas.Documents_title])
def read_user(user_document_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_document(db, user_document_id=user_document_id, skip=skip, limit=limit)
    if not db_item:
        raise HTTPException(status_code=404, detail="Items not found")
    return db_item



@router.post("/item_for_document_description/{user_id}", response_model=schemas.Documents_Terms_of_financing_create)
def create_item_for_about(user_id: int, item: schemas.Documents_Terms_of_financing_create, db: Session = Depends(get_db)):  
    created_item = crud.create_user_item_document_description(db=db, item=item, user_document_id=user_id)
    return created_item

@router.get("/get_items_for_document_description/{user_document_id}", response_model=list[schemas.Documents_Terms_of_financing])
def read_user(user_document_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_document_description(db, user_document_id=user_document_id, skip=skip, limit=limit)
    if not db_item:
        raise HTTPException(status_code=404, detail="Items not found")
    return db_item
##

@router.post("/upload_file_compan/{item_id}", response_model=schemas.UserCreate_Files)
async def upload_multiple_files_compan(
    item_id: int,
    position: int,
    files: List[UploadFile],
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = await crud.usercreate_file(db, files, item_id, position)
    return uploaded_files

@router.get("/get_image_owner/{position}/{owner_id}")
async def get_image_owner(position: int, owner_id: int, db: Session = Depends(get_db)):
    file_path = crud.get_image_path_by_position_and_id_owner(db, position, owner_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='video/mp4') 


@router.post("/upload/{new_build_apartment_id}", response_model=schemas.Files)
async def upload_multiple_files(
    new_build_apartment_id: int,
    files: List[UploadFile],
    position: int,
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = await crud.upload_files(db, files, position, new_build_apartment_id)
    return uploaded_files

@router.get("/get_image/{position}/{new_build_apartment_id}")
async def get_image(position: int, new_build_apartment_id: int, db: Session = Depends(get_db)):
    file_path = crud.get_image_path_by_position_and_id(db, position, new_build_apartment_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='video/mp4') 






@router.post("/create_user_item_description/{description_id}", response_model=schemas.ItemDescription)
def create_user_item_description(description_id: int, item: schemas.ItemsCreateDescription, db: Session = Depends(get_db)):
    created_item = crud.create_user_item_description(db=db, item=item, user_discription_id=description_id)
    return created_item


@router.get("/get_descriptions_id/{item_id}", response_model=List[schemas.ItemDescription])
def read_user(item_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_descriptions_id(db, item_id=item_id, skip=skip, limit=limit)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_item





@router.post("/upload_description/{new_build_apartment_description_id}", response_model=schemas.File_descriptions)
async def upload_multiple_files_deckription(
    new_build_apartment_description_id: int,
    files: List[UploadFile],
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = await crud.upload_files_plan(db, files, new_build_apartment_description_id)
    return uploaded_files


@router.get("/get_image_description/{new_build_apartment_description_id}")
async def get_image_description(new_build_apartment_description_id: int, db: Session = Depends(get_db)):
    file_path = crud.get_image_path_by_id_description(db, new_build_apartment_description_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='image/jpeg')







@router.post("/upload_monitoring/{new_build_apartment_id}", response_model=schemas.File_construction_monitorings)
async def upload_multiple_files_monitoring(
    new_build_apartment_id: int,
    files: List[UploadFile] = File(...),
    position: int = Form(...),
    date: str = Form(...),
    namber_build_andsection: str = Form(...),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = await crud.upload_file_construction_monitoring(db, files, new_build_apartment_id, position, date, namber_build_andsection)
    return uploaded_files


@router.get("/get_images_metadata/{new_build_apartment_id}", response_model=schemas.File_construction_monitorings)
async def get_images_metadata(new_build_apartment_id: int, db: Session = Depends(get_db)):
    files = crud.get_images_by_new_build_apartment_id(db, new_build_apartment_id)
    
    if not files:
        raise HTTPException(status_code=404, detail="Files not found")


    metadata_list = [
        schemas.File_construction_monitoring(
            id=file.id,
            file_url=f"/get_image_monitoring/{file.id}",
            content_type=file.content_type,
            position=file.position,
            date=file.date,
            namber_build_andsection=file.namber_build_andsection,
            new_build_apartment_id=file.new_build_apartment_id
        ) for file in files
    ]
    
    return schemas.File_construction_monitorings(files=metadata_list)

@router.get("/get_image_monitoring/{file_id}")
async def get_image_monitoring(file_id: int, db: Session = Depends(get_db)):
    file = db.query(models.File_new_build_apartment_construction_monitoring).filter(
        models.File_new_build_apartment_construction_monitoring.id == file_id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(open(file.file_path, "rb"), media_type=file.content_type)



@router.get("/get_news_id/{user_id}", response_model=List[schemas.UserCreate_News])
def read_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_item = crud.get_news_for_id_user(db, item_id=user_id, skip=skip, limit=limit)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_item




@router.post("/upload_monitoring_360/{new_build_apartment_id}", response_model=schemas.File_new_build_apartment_aerial_survey_360s)
async def upload_multiple_files_monitoring_360(
    new_build_apartment_id: int,
    files: List[UploadFile] = File(...),
    date: str = Form(...),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = await crud.upload_file_monitoring_360(db, files, date, new_build_apartment_id)
    return uploaded_files



@router.get("/get_image_description_360_metadata/{new_build_apartment_description_id}", response_model=schemas.File_new_build_apartment_aerial_survey_360s)
async def get_images_metadata(new_build_apartment_description_id: int, db: Session = Depends(get_db)):
    files = crud.get_image_path_by_position_and_id_monitoring_monitoring_360(db, new_build_apartment_description_id)
    
    if not files:
        raise HTTPException(status_code=404, detail="Files not found")

    metadata_list = [
        schemas.File_new_build_apartment_aerial_survey_360(
            id=file.id,
            file_url=f"/get_image_description_360/{file.id}",
            content_type=file.content_type,
            date=file.date,
            file_path=file.file_path  # Add file_path to the initialization
        ) for file in files
    ]
    
    return schemas.File_new_build_apartment_aerial_survey_360s(files=metadata_list)

@router.get("/get_image_description_360/{file_id}")
async def get_image_monitoring_360(file_id : int, db: Session = Depends(get_db)):
    file = db.query(models.File_new_build_apartment_aerial_survey_360).filter(
        models.File_new_build_apartment_aerial_survey_360.id == file_id
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(open(file.file_path, "rb"), media_type=file.content_type)






@router.post("/3d_object/{new_build_apartment_id}", response_model=schemas.User_3D_File_models)
async def upload_3d_model(
    new_build_apartment_id: int,
    files: List[UploadFile],
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = await crud.upload_3d_model(db, files, new_build_apartment_id)
    return uploaded_files


@router.get("/get_3d_object/{new_build_apartment_id}", response_model=schemas.User_3D_File_models)
async def get_3d_models(new_build_apartment_id: int, db: Session = Depends(get_db)):
    files = crud.get_3d_models(db, new_build_apartment_id)
    if not files:
        raise HTTPException(status_code=404, detail="Files not found")
    
    file_responses = []
    for file in files:
        file_response = schemas.User_3D_File_model(
            id=file.id,
            file_url=file.file_path,
            content_type=file.content_type
        )
        file_responses.append(file_response)
    
    return schemas.User_3D_File_models(files=file_responses)


@router.get("/get_alll_plans/", response_model=List[schemas.ItemDescription])
def read_items(db: Session = Depends(get_db)):
    items = db.query(models.ItemsCreateDescription).all()
    return items

@router.get("/filter_items/", response_model=List[schemas.Item])
def filter_items(
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
    limit: int = 100,
    db: Session = Depends(get_db)
):
    items = crud.filter_items_by_description(
        db=db,
        min_price_one_meter=min_price_one_meter,
        max_price_one_meter=max_price_one_meter,
        min_all_meter_in_item=min_all_meter_in_item,
        max_all_meter_in_item=max_all_meter_in_item,
        min_all_price_items=min_all_price_items,
        max_all_price_items=max_all_price_items,
        type_items=type_items,
        input_term=input_term,
        state=state,
        floors=floors,
        apartment_condition=apartment_condition,
        construction_status=construction_status,
        declared_commissioning=declared_commissioning,
        housing_condition=housing_condition,
        skip=skip,
        limit=limit
    )
    return items