import json
import time
import streamlit as st
import pandas as pd
import numpy as np
import http.client
import requests
from streamlit_echarts import st_echarts
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Documents_Terms_of_financing, File_new_build_apartment, File_new_build_apartment_ItemCreate_about, File_new_build_apartment_construction_monitoring, ItemCreate_about, UserCreate, ItemCreate, File_description, UserCreate_File, ItemsCreateDescription, File_new_build_apartment_aerial_survey_360, Documents_title, UserCreate_News, User_3D_File_model
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def create_video(image_url, image_end_url, prompt):
    conn = http.client.HTTPSConnection("api.piapi.ai")
    payload = json.dumps({
        "image_url": image_url,
        "image_end_url": image_end_url,
        "expand_prompt": True,
        "prompt": prompt,
    })
    headers = {
        "X-API-Key": "0f5eea9dd96c1eeb1657c3bf55c301490d465093ef03f3d69fc17989bb5e092b",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    conn.request("POST", "/api/luma/v1/video", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print("Video Creation Response:", data.decode("utf-8"))  # Debug print
    return json.loads(data.decode("utf-8"))

def get_video(task_id):
    conn = http.client.HTTPSConnection("api.piapi.ai")
    headers = {
        'X-API-Key': "0f5eea9dd96c1eeb1657c3bf55c301490d465093ef03f3d69fc17989bb5e092b",
        'Content-Type': "application/json",
        'Accept': "application/json"
    }
    conn.request("GET", f"/api/luma/v1/video/{task_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

# Database connection
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost/test?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the database session
session = SessionLocal()

# Streamlit app
st.title("Admin Interface")

def authenticate(username, password):
    user = session.query(UserCreate).filter(UserCreate.email == username, UserCreate.hashed_password == password).first()
    return user

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user'] = None

if st.session_state['logged_in']:
    user = st.session_state['user']
    st.sidebar.write(f"Logged in as {user.title_company}")

    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.experimental_rerun()

else:
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user
            st.experimental_rerun()
        else:
            st.sidebar.error("Invalid username or password")

# Continue with the rest of the app only if logged in
if st.session_state['logged_in']:
    # Sidebar menu
    menu = ['close', "Users", "Items", 'Items Create Description', 'Aerial Survey 360', "construction monitoring", 'Documents Title',"Documents term of finansing"]
    choice = st.sidebar.selectbox("add change dalit information", menu)

    menuu = ['close',"create video"]
    choicec = st.sidebar.selectbox("static", menuu)



    # Functions to handle CRUD operations
    def get_users():
        user = st.session_state['user']
        return session.query(UserCreate).filter(UserCreate.id == user.id).all()

    # Function to add a user to the database
    def add_user(user_data):
        new_user = UserCreate(**user_data)
        session.add(new_user)
        session.commit()
        st.success("User added successfully!")

    # Function to delete a user from the database
    def delete_user(user_id):
        user = session.query(UserCreate).filter(UserCreate.id == user_id).first()
        session.delete(user)
        session.commit()
        st.success("User deleted successfully!")

    # Function to update a user in the database
    def update_user(user_id, updated_data):
        session.query(UserCreate).filter(UserCreate.id == user_id).update(updated_data)
        session.commit()
        st.success("User updated successfully!")


    def get_files():
        user = st.session_state['user']
        files = session.query(UserCreate_File).join(UserCreate, UserCreate_File.owner_id == UserCreate.id).filter(UserCreate_File.owner_id == user.id).all()
        return [
            {
                'id': file.id,
                'filename': file.filename,
                'position': file.position,
                'content_type': file.content_type,
                'file_path': file.file_path,
                'title_company': file.owner.title_company
            }
            for file in files
        ]

    def upload_file_user(item_id, position, files):
        url = f"http://localhost:8000/upload_file_compan/{item_id}?position={position}"
        response = requests.post(url, files=files)
        return response.json()

    def delete_file(item_id):
        user = st.session_state['user']
        file = session.query(UserCreate_File).filter(UserCreate_File.id == item_id, UserCreate_File.owner_id == user.id).first()
        if file:
            session.delete(file)
            session.commit()
            st.success("File deleted successfully!")
        else:
            st.error("You can only delete your own files!")


    def update_file(item_id, file_data):
        if 'title_company' in file_data:
            title_company = file_data.pop('title_company')
            user = session.query(UserCreate).filter(UserCreate.title_company == title_company).first()
            if user:
                file_data['owner_id'] = user.id

        file = session.query(UserCreate_File).filter(UserCreate_File.id == item_id).first()
        if file:
            for key, value in file_data.items():
                setattr(file, key, value)
            session.commit()
            st.success("File updated successfully!")
        else:
            st.warning("File not found!")

    # Function to get news from the database
    def get_news():
        user = st.session_state['user']
        files = session.query(UserCreate_News).join(UserCreate, UserCreate_News.owner_id == UserCreate.id).filter(UserCreate_News.owner_id == user.id).all()
        return [
            {
                'id': file.id,
                'title': file.title,
                'date': file.date,
                'text': file.text,
                'link': file.link,
                'title_company': file.owner.title_company
            }
            for file in files
        ]
    def add_news(news_data):
        new_news = UserCreate_News(**news_data)
        session.add(new_news)
        session.commit()
        st.success("News added successfully!")

    def delete_news(news_id):
        user = st.session_state['user']
        news = session.query(UserCreate_News).filter(UserCreate_News.id == news_id, UserCreate_News.owner_id == user.id).first()
        if news:
            session.delete(news)
            session.commit()
            st.success("News deleted successfully!")
        else:
            st.error("You can only delete your own news!")

    def update_news(news_id, updated_data):
        if 'title_company' in updated_data:
            title_company = updated_data.pop('title_company')
            user = session.query(UserCreate).filter(UserCreate.title_company == title_company).first()
            if user:
                updated_data['owner_id'] = user.id

        session.query(UserCreate_News).filter(UserCreate_News.id == news_id).update(updated_data)
        session.commit()
        st.success("News updated successfully!")







    def get_items():
        user = st.session_state['user']
        return session.query(ItemCreate).filter(ItemCreate.owner_id == user.id).all()

    def get_items_ids():
        user = st.session_state['user']
        return session.query(UserCreate.id, UserCreate.title_company).filter(UserCreate.id == user.id).all()

    def get_items_ids_items():
        user = st.session_state['user']
        return session.query(ItemCreate.title).filter(ItemCreate.owner_id == user.id).all()
    def get_user_title_company_map():
        users = get_users()
        return {user.id: user.title_company for user in users}

    def add_item(item_data):
        new_item = ItemCreate(**item_data)
        session.add(new_item)
        session.commit()
        st.success("Item added successfully!")

    def upload_item_photo(date, file, item_id):
        files = {"files": (file.name, file.getvalue(), file.type)}
        data = {"date": date}
        url = f"http://localhost:8000/upload/{item_id}"
        response = requests.post(url, files=files, data=data)
        return response.json()

    def update_item(item_data):
        item = session.query(ItemCreate).filter(ItemCreate.id == item_data['id']).first()
        if item:
            for key, value in item_data.items():
                setattr(item, key, value)
            session.commit()
            st.success("Item updated successfully!")

    def delete_item(item_id):
        item = session.query(ItemCreate).filter(ItemCreate.id == item_id).first()
        if item:
            session.delete(item)
            session.commit()
            st.success("Item deleted successfully!")
        else:
            st.warning("Item not found!")

    def get_item_create_about():
        user = st.session_state['user']
        return session.query(ItemCreate_about).join(ItemCreate).filter(ItemCreate.owner_id == user.id).all()

    def get_360_ids():
        user = st.session_state['user']
        return session.query(ItemCreate_about.new_build_apartment_id).filter(ItemCreate_about.owner_id == user.id).all()

    def add_item_create_about(item_create_about):
        new_item = ItemCreate_about(**item_create_about)
        session.add(new_item)
        session.commit()
        st.success("Item added successfully!")

    def update_item_create_about(item_create_about):
        item = session.query(ItemCreate_about).filter(ItemCreate_about.id == item_create_about['id']).first()
        if item:
            item.link = item_create_about['link']
            item.dascription = item_create_about['dascription']
            item.new_build_apartment_id = item_create_about['new_build_apartment_id']
            session.commit()
            st.success("Item updated successfully!")

    def delete_item_create_about(delete_item_create_about_id):
        item = session.query(ItemCreate_about).filter(ItemCreate_about.id == delete_item_create_about_id).first()
        if item:
            session.delete(item)
            session.commit()
            st.success("Item deleted successfully!")




    def get_file_description_file_ids():
        user = st.session_state['user']
        return session.query(ItemCreate_about.id, ItemCreate_about.dascription, ItemCreate.title).join(ItemCreate).filter(ItemCreate.owner_id == user.id).all()
    # Function to upload the description photo
    def upload_description_photo_file(item_create_about_id, file):
        files = {"files": (file.name, file.getvalue(), file.type)}
        url = f"http://localhost:8000//upload_file_about/{item_create_about_id}"
        response = requests.post(url, files=files)
        return response.json()

    # Function to delete file description
    def delete_file_description_file(item_create_about_id):
        file = session.query(File_new_build_apartment_ItemCreate_about).filter(File_new_build_apartment_ItemCreate_about.id == item_create_about_id).first()
        session.delete(file)
        session.commit()
        st.success("File deleted successfully!")

    # Function to update file description
    def update_file_description_file(item_create_about_id, file_data):
        file = session.query(File_new_build_apartment_ItemCreate_about).filter(File_new_build_apartment_ItemCreate_about.id == item_create_about_id).first()
        if file:
            for key, value in file_data.items():
                setattr(file, key, value)
            session.commit()
            st.success("File updated successfully!")
        else:
            st.warning("File not found!")


    def get_file_items():
        user = st.session_state['user']
        return session.query(File_new_build_apartment).join(ItemCreate).filter(ItemCreate.owner_id == user.id).all()

    def upload_file_items(new_build_apartment_id, position, files):
        url = f"http://localhost:8000/upload/{new_build_apartment_id}?position={position}"
        response = requests.post(url, files=files)
        return response.json()
    def delete_file_items(file_id):
        file = session.query(File_new_build_apartment).filter(File_new_build_apartment.id == file_id).first()
        if file:
            session.delete(file)
            session.commit()
            st.success("File deleted successfully!")
        else:
            st.warning("File not found!")

    def update_file_items(file_id, file_data):
        file = session.query(File_new_build_apartment).filter(File_new_build_apartment.id == file_id).first()
        if file:
            for key, value in file_data.items():
                setattr(file, key, value)
            session.commit()
            st.success("File updated successfully!")
        else:
            st.warning("File not found!")




    def get_new_build_apartment_ids():
        user = st.session_state['user']
        return session.query(ItemCreate.id, ItemCreate.title).filter(ItemCreate.owner_id == user.id).all()

    def add_items_create_description(items_create_description):
        new_item = ItemsCreateDescription(**items_create_description)
        session.add(new_item)
        session.commit()
        st.success("Item added successfully!")

    def update_items_create_description(item_data):
        item = session.query(ItemsCreateDescription).filter(ItemsCreateDescription.id == item_data['id']).first()
        if item:
            for key, value in item_data.items():
                setattr(item, key, value)
            session.commit()
            st.success("Item updated successfully!")
        else:
            st.warning("Item not found!")

    def delete_items_create_description(item_id):
        item = session.query(ItemsCreateDescription).filter(ItemsCreateDescription.id == item_id).first()
        if item:
            session.delete(item)
            session.commit()
            st.success("Item deleted successfully!")
        else:
            st.warning("Item not found!")

    def get_file_description():
        user = st.session_state['user']
        return session.query(File_description).filter(
            ItemsCreateDescription.new_build_apartment_id == user.id
        ).all()
    
    def get_items_create_description():
        user = st.session_state['user']
        return session.query(
            ItemsCreateDescription.id,
            ItemsCreateDescription.type_items,
            ItemsCreateDescription.price_one_meter,
            ItemsCreateDescription.all_meter_in_item,
            ItemsCreateDescription.all_price_items,
            ItemsCreateDescription.namber_build_andsection,
            ItemsCreateDescription.floors,
            ItemsCreateDescription.state,
            ItemsCreateDescription.input_term,
            ItemsCreateDescription.Features,
            ItemsCreateDescription.link,
            ItemsCreateDescription.new_build_apartment_id,
            ItemCreate.title  # Make sure to join on ItemCreate to get the title
        ).join(ItemCreate, ItemsCreateDescription.new_build_apartment_id == ItemCreate.id).filter(ItemCreate.owner_id == user.id).all()
    def upload_description_photo(new_build_apartment_description_id, file):
        files = {"files": (file.name, file.getvalue(), file.type)}
        url = f"http://localhost:8000/upload_description/{new_build_apartment_description_id}"
        response = requests.post(url, files=files)
        return response.json()

    def delete_file_description(new_build_apartment_description_id):
        file = session.query(File_description).filter(File_description.id == new_build_apartment_description_id).first()
        if file:
            session.delete(file)
            session.commit()
            st.success("File deleted successfully!")
        else:
            st.warning("File not found!")

    def update_file_description(new_build_apartment_description_id, file_data):
        file = session.query(File_description).filter(File_description.id == new_build_apartment_description_id).first()
        if file:
            for key, value in file_data.items():
                setattr(file, key, value)
            session.commit()
            st.success("File updated successfully!")
        else:
            st.warning("File not found!")



# Functions to interact with the database
    def get_aerial_survey_360():
        user = st.session_state['user']
        return session.query(File_new_build_apartment_aerial_survey_360).join(ItemCreate).filter(ItemCreate.owner_id == user.id).all()


    def upload_file(date, file, new_build_apartment_id):
        files = {"files": (file.name, file.getvalue(), file.type)}
        data = {"date": date}
        url = f"http://localhost:8000/upload_monitoring_360/{new_build_apartment_id}"
        response = requests.post(url, files=files, data=data)
        return response.json()

    def update_aerial_survey_360(item_aerial_survey_360):
        item = session.query(File_new_build_apartment_aerial_survey_360).filter(File_new_build_apartment_aerial_survey_360.id == item_aerial_survey_360['id']).first()
        if item:
            item.date = item_aerial_survey_360['date']
            item.filename = item_aerial_survey_360['filename']
            session.commit()
            st.success("Item updated successfully!")

    def delete_aerial_survey_360(item_aerial_survey_360_id):
        item = session.query(File_new_build_apartment_aerial_survey_360).filter(File_new_build_apartment_aerial_survey_360.id == item_aerial_survey_360_id).first()
        if item:
            session.delete(item)
            session.commit()
            st.success("Item deleted successfully!")









    def get_documents_title():
        user = st.session_state['user']
        return session.query(Documents_title).join(ItemCreate).filter(ItemCreate.owner_id == user.id).all()



    def add_document_title(item_document_title):
        new_item = Documents_title(**item_document_title)
        session.add(new_item)
        session.commit()
        st.success("Item added successfully!")

    def update_document_title(item_document_title):
        item = session.query(Documents_title).filter(Documents_title.id == item_document_title['id']).first()
        if item:
            item.title = item_document_title['title']
            item.text = item_document_title['text']
            item.link = item_document_title['link']
            item.new_build_apartment_id = item_document_title['new_build_apartment_id']
            session.commit()
            st.success("Item updated successfully!")

    def delete_document_title(item_document_title_id):
        item = session.query(Documents_title).filter(Documents_title.id == item_document_title_id).first()
        if item:
            session.delete(item)
            session.commit()
            st.success("Item deleted successfully!")








    def get_documents_title_description():
        user = st.session_state['user']
        return session.query(Documents_Terms_of_financing).join(ItemCreate).filter(ItemCreate.owner_id == user.id).all()

    def add_document_title_description(item_documents_title_description):
        new_item = Documents_Terms_of_financing(**item_documents_title_description)
        session.add(new_item)
        session.commit()
        st.success("Item added successfully!")

    def update_document_title_description(item_documents_title_description):
        item = session.query(Documents_Terms_of_financing).filter(Documents_Terms_of_financing.id == item_documents_title_description['id']).first()
        if item:
            item.title = item_documents_title_description['title']
            item.text = item_documents_title_description['text']
            item.link = item_documents_title_description['link']
            item.new_build_apartment_id = item_documents_title_description['new_build_apartment_id']
            session.commit()
            st.success("Item updated successfully!")

    def delete_document_title_description(item_documents_title_description_id):
        item = session.query(Documents_Terms_of_financing).filter(Documents_Terms_of_financing.id == item_documents_title_description_id).first()
        if item:
            session.delete(item)
            session.commit()
            st.success("Item deleted successfully!")






    def get_file_apartment_construction_monitoring():
        user = st.session_state['user']
        return session.query(File_new_build_apartment_construction_monitoring).join(ItemCreate).filter(ItemCreate.owner_id == user.id).all()


    def get_file_apartment_construction_monitoring_ids():
        user = st.session_state['user']
        return session.query(ItemsCreateDescription.id, ItemsCreateDescription.namber_build_andsection, ItemCreate.title).filter(ItemsCreateDescription.new_build_apartment_id == user.id).distinct().all()

    def upload_apartment_construction_monitoring(new_build_apartment_id, file, namber_build_andsection, date, position):
        files = {"files": (file.name, file.getvalue(), file.type)}
        data = {
            "date": date,
            "namber_build_andsection": namber_build_andsection,
            "position": position
        }
        url = f"http://localhost:8000/upload_monitoring/{new_build_apartment_id}"
        response = requests.post(url, files=files, data=data)
        return response.json()

    def delete_apartment_construction_monitoring(new_build_apartment_id):
        file = session.query(File_new_build_apartment_construction_monitoring).filter(File_new_build_apartment_construction_monitoring.id == new_build_apartment_id).first()
        if file:
            session.delete(file)
            session.commit()
            st.success("File deleted successfully!")
        else:
            st.warning("File not found!")

    def update_apartment_construction_monitoring(new_build_apartment_id, file_data):
        file = session.query(File_new_build_apartment_construction_monitoring).filter(File_new_build_apartment_construction_monitoring.id == new_build_apartment_id).first()
        if file:
            for key, value in file_data.items():
                setattr(file, key, value)
            session.commit()
            st.success("File updated successfully!")
        else:
            st.warning("File not found!")
    # Main content


    def get_3d_model():
        return session.query(User_3D_File_model).all()

    # Function to upload the description photo
    def upload_3d_model(new_build_apartment_id, file):
        files = {"files": (file.name, file.getvalue(), file.type)}
        url = f"http://localhost:8000/3d_object/{new_build_apartment_id}"
        response = requests.post(url, files=files)
        return response.json()

    # Function to delete file description
    def delete_3d_model(new_build_apartment_id):
        file = session.query(User_3D_File_model).filter(User_3D_File_model.id == new_build_apartment_id).first()
        session.delete(file)
        session.commit()
        st.success("File deleted successfully!")

    # Function to update file description
    def update_3d_model(new_build_apartment_id, file_data):
        file = session.query(User_3D_File_model).filter(User_3D_File_model.id == new_build_apartment_id).first()
        if file:
            for key, value in file_data.items():
                setattr(file, key, value)
            session.commit()
            st.success("File updated successfully!")
        else:
            st.warning("File not found!")
























    if choice == "Users":
            st.subheader("Manage Users")
            user_data = []

            users = get_users()
            for user in users:
                user_data.append({
                    'id': user.id,
                    'title_company': user.title_company,
                    'email': user.email,
                    'phone': user.phone,
                    'adres': user.adres,
                    'lng': user.lng,
                    'lat': user.lat,
                    'hashed_password': user.hashed_password,
                    'year_of_foundation': user.year_of_foundation,
                    'houses_were_delivered': user.houses_were_delivered,
                    'houses_in_the_process': user.houses_in_the_process,
                    'in_the_process_suburban_type': user.in_the_process_suburban_type,
                    'suburban_type': user.suburban_type,
                    'website': user.website,
                    'is_active': user.is_active
                })
            df = pd.DataFrame(user_data)
            edited_df = st.data_editor(df)

            if not df.equals(edited_df):
                for index, row in edited_df.iterrows():
                    original_row = df.iloc[index]
                    if row['id'] != original_row['id']:
                        continue  # skip the unchanged rows

                    updated_data = {column: row[column] for column in df.columns if column != 'id'}
                    update_user(row['id'], updated_data)

            st.subheader("Manage Files")
            file_data = get_files()
            df = pd.DataFrame(file_data)

            # Replace 'owner_id' column with 'title_company' for display
            df_display = df.copy()
            df_display['title_company'] = df_display.pop('title_company')
            
            edited_df = st.data_editor(df_display)

            if not df.equals(edited_df):
                for index, row in edited_df.iterrows():
                    original_row = df.iloc[index]
                    if row['id'] != original_row['id']:
                        continue  # skip the unchanged rows

                    updated_data = {column: row[column] for column in df.columns if column != 'id'}
                    update_file(row['id'], updated_data)

            # Add file
            st.subheader("Add File")
            item_ids = get_items_ids()
            item_id_map = {item.id: item.title_company for item in item_ids}

            with st.form("add_file_form"):
                position = st.number_input("Position", step=1)
                item_id = st.selectbox("Owner", options=list(item_id_map.keys()), format_func=lambda x: item_id_map[x])
                file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf", "mp4", "avi", "mov"])  # Allow video uploads
                submitted = st.form_submit_button("Upload File")

                if submitted:
                    files = [("files", (file.name, file.getvalue(), file.type))]
                    upload_file_user(item_id, position, files)

            # Delete file
            st.subheader("Delete File")
            delete_file_id = st.number_input("File ID to Delete", step=1)
            if st.button("Delete File"):
                delete_file(delete_file_id)

            # Add news
    if choice == "Users":    
            st.subheader("Manage News")
            news_data = get_news()
            df = pd.DataFrame(news_data)

            # Replace 'owner_id' column with 'title_company' for display
            df_display = df.copy()
            df_display['title_company'] = df_display.pop('title_company')

            edited_df = st.data_editor(df_display)

            if not df.equals(edited_df):
                for index, row in edited_df.iterrows():
                    original_row = df.iloc[index]
                    if row['id'] != original_row['id']:
                        continue  # skip the unchanged rows

                    updated_data = {column: row[column] for column in df.columns if column != 'id'}
                    update_news(row['id'], updated_data)

            # Add news
            st.subheader("Add News")
            item_ids = get_items_ids()
            item_id_map = {item.id: item.title_company for item in item_ids}

            with st.form("add_news_form"):
                title = st.text_input("Title")
                date = st.date_input("Date")
                text = st.text_input("Text")
                link = st.text_input("Link")
                owner_id = st.selectbox("Owner", options=list(item_id_map.keys()), format_func=lambda x: item_id_map[x])
                submitted = st.form_submit_button("Add News")

                if submitted:
                    news_data = {
                        "title": title,
                        "date": date,
                        "text": text,
                        "link": link,
                        "owner_id": owner_id
                    }
                    add_news(news_data)

            # Delete news
            st.subheader("Delete News")
            delete_news_id = st.number_input("News ID to Delete", step=1)
            if st.button("Delete News"):
                delete_news(delete_news_id)































    elif choice == "Items":
        st.subheader("Manage Items")

        user_data = []
        items = get_items()
        user_title_company_map = get_user_title_company_map()

        for item in items:
            user_data.append({
                'id': item.id,
                'title': item.title,
                'price_hi': item.price_hi,
                'price_low': item.price_low,
                'city': item.city,
                'line_adres': item.line_adres,
                'class_bulding': item.class_bulding,
                'houses': item.houses,
                'number_of_storeys': item.number_of_storeys,
                'construction_technology': item.construction_technology,
                'walls': item.walls,
                'insulation': item.insulation,
                'heating': item.heating,
                'ceiling_height': item.ceiling_height,
                'number_of_flats': item.number_of_flats,
                'apartment_condition': item.apartment_condition,
                'territory': item.territory,
                'car_park': item.car_park,
                'lng': item.lng,
                'lat': item.lat,
                'owner_id': item.owner_id,
                'owner_title_company': user_title_company_map.get(item.owner_id)
            })

        df = pd.DataFrame(user_data)
        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip unchanged rows
                
                item_data = {column: row[column] for column in df.columns if column != 'owner_title_company'}
                update_item(item_data)

        st.subheader("Add Item")
        with st.form("add_item_form"):
            title = st.text_input("Title")
            position = st.number_input("Position", step=1)
            description_text = st.text_area("Description Text")
            price_hi = st.number_input("High Price", step=1)
            price_low = st.number_input("Low Price", step=1)
            city = st.text_input("City")
            line_adres = st.text_input("Address Line")
            class_bulding = st.text_input("Building Class")
            houses = st.number_input("Houses", step=1)
            number_of_storeys = st.number_input("Number of Storeys", step=1)
            construction_technology = st.text_input("Construction Technology")
            walls = st.text_input("Walls")
            insulation = st.text_input("Insulation")
            heating = st.text_input("Heating")
            ceiling_height = st.text_input("Ceiling Height")
            number_of_flats = st.number_input("Number of Flats", step=1)
            apartment_condition = st.text_input("Apartment Condition")
            territory = st.text_input("Territory")
            car_park = st.text_input("Car Park")
            lng = st.text_input("Lng")
            lat = st.text_input("Lat")
            
            user_title_company_map = get_user_title_company_map()
            owner_id_options = list(user_title_company_map.keys())
            owner_title_company_options = list(user_title_company_map.values())
            
            owner_id = st.selectbox("Owner", options=owner_id_options, format_func=lambda x: user_title_company_map[x])
            
            submitted = st.form_submit_button("Add Item")
            if submitted:
                item_data = {
                    "title": title,
                    "position": position,
                    "description_text": description_text,
                    "price_hi": price_hi,
                    "price_low": price_low,
                    "city": city,
                    "line_adres": line_adres,
                    "class_bulding": class_bulding,
                    "houses": houses,
                    "number_of_storeys": number_of_storeys,
                    "construction_technology": construction_technology,
                    "walls": walls,
                    "insulation": insulation,
                    "heating": heating,
                    "ceiling_height": ceiling_height,
                    "number_of_flats": number_of_flats,
                    "apartment_condition": apartment_condition,
                    "territory": territory,
                    "car_park": car_park,
                    "lng": lng,
                    "lat": lat,
                    "owner_id": owner_id
                }
                add_item(item_data)

        st.subheader("Delete Item")
        with st.form("delete_item_form"):
            delete_id = st.number_input("ID to delete", step=1)
            delete_submitted = st.form_submit_button("Delete Item")
            if delete_submitted:
                delete_item(delete_id)



        st.subheader("Manage Items")

        user_data = []
        items = get_file_items()
        new_build_apartment_map = {item.id: item.title for item in get_items()}

        for item in items:
            user_data.append({
                'id': item.id,
                'filename': item.filename,
                'position': item.position,
                'new_build_apartment_title': new_build_apartment_map.get(item.new_build_apartment_id)
            })

        df = pd.DataFrame(user_data)
        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip unchanged rows

                updated_data = {column: row[column] for column in df.columns if column not in ['id', 'new_build_apartment_title']}
                update_file_items(row['id'], updated_data)

        st.subheader("Add File")
        with st.form("add_file_form"):
            position = st.number_input("Position", step=1)
            new_build_apartment_ids = get_new_build_apartment_ids()
            new_build_apartment_id = st.selectbox("New Build Apartment", options=new_build_apartment_ids, format_func=lambda x: x[1])
            file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf", "mp4", "avi", "mov"])
            submitted = st.form_submit_button("Upload File")

            if submitted:
                files = [("files", (file.name, file.getvalue(), file.type))]
                upload_file_items(new_build_apartment_id[0], position, files)

        st.subheader("Delete File")
        delete_file_id = st.number_input("File ID to Delete", step=1)
        if st.button("Delete File"):
            delete_file_items(delete_file_id)



        st.subheader("Manage Items create about")
        user_dataa = []
        new_build_apartment_map = {item.id: item.title for item in get_items()}

        userss = get_item_create_about()

        for user in userss:
            user_dataa.append({
                'id': user.id,
                'link': user.link,
                'dascription': user.dascription,
                'new_build_apartment_id': new_build_apartment_map.get(user.new_build_apartment_id)
            })

        df = pd.DataFrame(user_dataa)
        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip the unchanged rows

                if (row['title'] != original_row['title'] or row['text'] != original_row['text'] or 
                    row['link'] != original_row['link'] or row['new_build_apartment_title'] != original_row['new_build_apartment_title']):
                    
                    new_build_apartment_id = [key for key, value in new_build_apartment_map.items() if value == row['new_build_apartment_title']][0]
                    
                    item_create_about = {
                        "id": row['id'],
                        "dascription": row['dascription'],
                        "link": row['link']
                    }
                    update_item_create_about(item_create_about)

        st.subheader("Add Documents Title Description")
        with st.form("add_item_form_2"):
            dascription = st.text_input("Title")
            link = st.text_input("Link")
            documents_title_ids = get_new_build_apartment_ids()
            new_build_apartment_id = st.selectbox("Documents Title ID", options=documents_title_ids, format_func=lambda x: x[1])
            submittedd = st.form_submit_button("Add Item")
            if submittedd:
                item_create_about = {
                    "dascription": dascription,
                    "link": link,
                    "new_build_apartment_id": new_build_apartment_id[0]
                }
                add_item_create_about(item_create_about)

        st.subheader("Delete Documents Title Description")
        with st.form("delete_item_form_2"):
            delete_item_create_about_id = st.number_input("ID to delete", min_value=0, step=1)
            delete_submitted = st.form_submit_button("Delete Item")

            if delete_submitted:
                delete_item_create_about(delete_item_create_about_id)





        st.subheader("Manage file description")
        user_dataa = []

        users = get_file_description_file_ids()
        for user in users:
            user_dataa.append({
                'id': user.id,
                'description': user.dascription,  # Ensure this matches the queried field name
                'title': user.title
            })
        # Create a DataFrame
        df = pd.DataFrame(user_dataa)

        # Remove duplicates based on specific column

        # Display the data using Streamlit's data editor
        edited_dff = st.data_editor(df)


        if not df.equals(edited_dff):
            for index, row in edited_dff.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip the unchanged rows

                updated_data = {column: row[column] for column in df.columns if column != 'id'}
                item_create_about_id = row['id']
                update_file_description_file(item_create_about_id, updated_data)

            # Add file
        st.subheader("Add File for items create")
        with st.form("Add File for items create"):
            new_build_apartment_ids = get_file_description_file_ids()
            formatted_options = [(item.id, f"{item.dascription} - {item.title}") for item in new_build_apartment_ids]

            item_create_about_id = st.selectbox("New Build Apartment ID", options=formatted_options, format_func=lambda x: x[1])
            file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf", "mp4", "avi", "mov"])  # Allow video uploads
            submitted = st.form_submit_button("Upload File")

            if submitted and file is not None:
                upload_description_photo_file(item_create_about_id[0], file)

            # Delete file
        st.subheader("Delete File for Items")
        item_create_about_id = st.number_input("File ID to Delete", step=0)
        if st.button("Delete File for Items"):
            delete_file_description_file(item_create_about_id)
















    elif choice == "Items Create Description":
        st.subheader("Manage Items Create Description")
        user_data = []

        users = get_items_create_description()
        new_build_apartment_map = {item.id: item.title for item in get_items()}

        for user in users:
            user_data.append({
                'id': user.id,
                'type_items': user.type_items,
                'price_one_meter': user.price_one_meter,
                'all_meter_in_item': user.all_meter_in_item,
                'all_price_items': user.all_price_items,
                'namber_build_andsection': user.namber_build_andsection,
                'floors': user.floors,
                'state': user.state,
                'input_term': user.input_term,
                'Features': user.Features,
                'link': user.link,
                'new_build_apartment_title': new_build_apartment_map.get(user.new_build_apartment_id)
            })

        df = pd.DataFrame(user_data)
        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip the unchanged rows
                
                if row.to_dict() != original_row.to_dict():
                    item_data = row.to_dict()
                    update_items_create_description(item_data)

        st.subheader("Add Item")
        with st.form("add_item_form"):
            type_items = st.text_input("Type Items")
            price_one_meter = st.number_input("Price per Meter", min_value=0)
            all_meter_in_item = st.number_input("All Meter in Item", min_value=0)
            all_price_items = st.number_input("All Price", min_value=0)
            namber_build_andsection = st.text_input("Number Build and Section")
            floors = st.text_input("Floors")
            state = st.text_input("State")
            input_term = st.text_input("Input Term")
            features = st.text_input("Features")
            link = st.text_input("Link for 3D walk")
            new_build_apartment_ids = get_new_build_apartment_ids()
            new_build_apartment_id = st.selectbox("New Build Apartment ID", options=new_build_apartment_ids, format_func=lambda x: x[1])

            submitted = st.form_submit_button("Add Item")

            if submitted:
                item_data = {
                    "type_items": type_items,
                    "price_one_meter": price_one_meter,
                    "all_meter_in_item": all_meter_in_item,
                    "all_price_items": all_price_items,
                    "namber_build_andsection": namber_build_andsection,
                    "floors": floors,
                    "state": state,
                    "input_term": input_term,
                    "Features": features,
                    "link": link,
                    "new_build_apartment_id": new_build_apartment_id[0]
                }
                add_items_create_description(item_data)
                
        st.subheader("Delete Item")
        with st.form("delete_item_form"):
            delete_id = st.number_input("ID to delete", min_value=0, step=1)
            delete_submitted = st.form_submit_button("Delete Item")

            if delete_submitted:
                delete_items_create_description(delete_id)

        st.subheader("Manage File Description")
        user_dataa = []

        users = get_file_description()

        # Extend the map to include additional fields from ItemsCreateDescription and ItemCreate
        new_build_apartment_description_map = {}
        for item in get_items():
            for description in item.description:
                new_build_apartment_description_map[description.id] = {
                    'title': item.title,
                    'type_items': description.type_items,
                    'namber_build_andsection': description.namber_build_andsection
                }


        for user in users:
            description_details = new_build_apartment_description_map.get(user.new_build_apartment_description_id, {})
            user_dataa.append({
                'id': user.id,
                'filename': user.filename,
                'new_build_apartment_description_id': f"{description_details.get('title', '')} | {description_details.get('type_items', '')} | {description_details.get('namber_build_andsection', '')}"
            })

                
        df = pd.DataFrame(user_dataa)
        edited_dff = st.data_editor(df)

        if not df.equals(edited_dff):
            for index, row in edited_dff.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip the unchanged rows

                updated_data = {column: row[column] for column in df.columns if column != 'id'}
                new_build_apartment_description_id = row['id']
                update_file_description(new_build_apartment_description_id, updated_data)

        # Add file
        st.subheader("Add File")
        with st.form("add_file_form"):
            new_build_apartment_ids = get_items_create_description()
            formatted_options = [
            (item.id, f"{item.type_items} - price_one_meter {item.price_one_meter} - all_meter_in_item {item.all_meter_in_item} - {item.namber_build_andsection} - {item.title}")
            for item in new_build_apartment_ids
            ]

            new_build_apartment_description_id = st.selectbox("New Build Apartment ID", options=formatted_options, format_func=lambda x: x[1])
            file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf", "mp4", "avi", "mov"])  # Allow video uploads
            submitted = st.form_submit_button("Upload File")

            if submitted and file is not None:
                upload_description_photo(new_build_apartment_description_id[0], file)

        # Delete file
        st.subheader("Delete File")
        new_build_apartment_description_id = st.number_input("File ID to Delete", step=1)
        if st.button("Delete File"):
            delete_file_description(new_build_apartment_description_id)















    elif choice == "Aerial Survey 360":
        st.subheader("Manage Aerial Survey 360")
        user_data = []

        users = get_aerial_survey_360()
        new_build_apartment_map = {item.id: item.title for item in get_new_build_apartment_ids()}

        for user in users:
            user_data.append({
                "ID": user.id,
                "Filename": user.filename,
                "Date": user.date,
                "New Build Apartment Title": new_build_apartment_map.get(user.new_build_apartment_id)
            })
        df = pd.DataFrame(user_data)
        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['ID'] != original_row['ID']:
                    continue  # skip the unchanged rows

                if row['Date'] != original_row['Date'] or row['Filename'] != original_row['Filename']:
                    item_aerial_survey_360 = {
                        "id": row['ID'],
                        "date": row['Date'],
                        "filename": row['Filename']
                    }
                    update_aerial_survey_360(item_aerial_survey_360)

        st.subheader("Add File")
        with st.form("upload_file_form"):
            date = st.date_input("Date")
            new_build_apartment_ids = get_new_build_apartment_ids()
            new_build_apartment_id = st.selectbox("New Build Apartment ID", options=new_build_apartment_ids, format_func=lambda x: x[1])
            file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf"])
            submitted = st.form_submit_button("Upload File")
            
            if submitted and file is not None:
                response = upload_file(date.strftime('%Y-%m-%d'), file, new_build_apartment_id[0])
                st.write(response)
            elif submitted and file is None:
                st.error("Please upload a file.")

        st.subheader("Delete Aerial Survey 360")
        with st.form("delete_item_form"):
            delete_id = st.number_input("ID to delete", min_value=0, step=1)
            delete_submitted = st.form_submit_button("Delete Item")

            if delete_submitted:
                delete_aerial_survey_360(delete_id)









    elif choice == "construction monitoring":
        st.subheader("Manage construction monitoring")
        user_data = []

        users = get_file_apartment_construction_monitoring()
        new_build_apartment_map = {item.id: item.title for item in get_new_build_apartment_ids()}

        seen_ids = set()
        for user in users:
            if user.id not in seen_ids:
                seen_ids.add(user.id)
                user_data.append({
                    'id': user.id,
                    'content_type': user.content_type,
                    'position': user.position,
                    'date': user.date,
                    'namber_build_andsection': user.namber_build_andsection,
                    'new_build_apartment_title': new_build_apartment_map.get(user.new_build_apartment_id)
                })

        df = pd.DataFrame(user_data)
        df.drop_duplicates(inplace=True)  # Remove duplicates if any

        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip the unchanged rows

                if (row['position'] != original_row['position'] or 
                    row['new_build_apartment_title'] != original_row['new_build_apartment_title'] or 
                    row['date'] != original_row['date'] or 
                    row['namber_build_andsection'] != original_row['namber_build_andsection']):

                    new_build_apartment_id = [key for key, value in new_build_apartment_map.items() if value == row['new_build_apartment_title']][0]

                    item_document_title = {
                        "id": row['id'],
                        "position": row['position'],
                        "date": row['date'],
                        "namber_build_andsection": row['namber_build_andsection'],
                        "new_build_apartment_id": new_build_apartment_id
                    }
                    update_apartment_construction_monitoring(row['id'], item_document_title)

        st.subheader("Add Item")
        with st.form("add_item_form"):
            position = st.number_input('Position', step=1)
            date = st.text_input('Date')
            namber_build_andsectionas = get_file_apartment_construction_monitoring_ids()
            
            # Track seen titles to remove duplicates
            seen_titles = set()
            options = []
            for item in namber_build_andsectionas:
                if item.title not in seen_titles:
                    seen_titles.add(item.title)
                    # Store a tuple (actual_value, display_value)
                    actual_value = item.namber_build_andsection
                    display_value = f"{item.namber_build_andsection} - {item.title}"
                    options.append((actual_value, display_value))
            
            # Create the selectbox with the options tuple
            selected_option = st.selectbox("Number Build and Section", options=options, format_func=lambda x: x[1])
            # selected_option[0] will give the `namber_build_andsection` value
            namber_build_andsection = selected_option[0]
            file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf", "mp4", "avi", "mov"])  # Allow video uploads
            new_build_apartment_ids = get_new_build_apartment_ids()
            new_build_apartment_id = st.selectbox("New Build Apartment Title", options=new_build_apartment_ids, format_func=lambda x: x[1])
            submitted = st.form_submit_button("Add Item")

            if submitted and file is not None:
                upload_apartment_construction_monitoring(new_build_apartment_id[0], file, namber_build_andsection, date, position)

        st.subheader("Delete Item")
        with st.form("delete_item_form"):
            new_build_apartment_id = st.number_input("ID to delete", min_value=0, step=1)
            delete_submitted = st.form_submit_button("Delete Item")

            if delete_submitted:
                delete_apartment_construction_monitoring(new_build_apartment_id)










    elif choice == "Documents Title":
        st.subheader("Manage Documents Title")
        user_data = []

        users = get_documents_title()
        new_build_apartment_map = {item.id: item.title for item in get_new_build_apartment_ids()}

        for user in users:
            user_data.append({
                'id': user.id,
                'title': user.title,
                'text':user.text,
                'link':user.link,
                'new_build_apartment_title': new_build_apartment_map.get(user.new_build_apartment_id)
            })
        df = pd.DataFrame(user_data)
        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip the unchanged rows

                if row['title'] != original_row['title'] or row['text'] != original_row['text'] or row['link'] != original_row['link'] or row['new_build_apartment_title'] != original_row['new_build_apartment_title']:
                    new_build_apartment_id = [key for key, value in new_build_apartment_map.items() if value == row['new_build_apartment_title']][0]
                    
                    item_document_title = {
                        "id": row['id'],
                        "title": row['title'],
                        "text": row['text'],
                        "link": row['link'],
                        "new_build_apartment_id": new_build_apartment_id
                    }
                    update_document_title(item_document_title)

        st.subheader("Add Item")
        with st.form("add_item_form"):
            title = st.text_input("Title")
            text = st.text_area("Text")
            link = st.text_input("Link")
            new_build_apartment_ids = get_new_build_apartment_ids()
            new_build_apartment_id = st.selectbox("New Build Apartment Title", options=new_build_apartment_ids, format_func=lambda x: x[1])
            submitted = st.form_submit_button("Add Item")

            if submitted:
                item_document_title = {
                    "title": title,
                    "text":text,
                    "link":link,
                    "new_build_apartment_id": new_build_apartment_id[0]
                }
                add_document_title(item_document_title)

        st.subheader("Delete Item")
        with st.form("delete_item_form"):
            delete_id = st.number_input("ID to delete", min_value=0, step=1)
            delete_submitted = st.form_submit_button("Delete Item")

            if delete_submitted:
                delete_document_title(delete_id)

    elif choice == "Documents term of finansing":
        st.subheader("Manage Documents Description")
        user_dataa = []

        userss = get_documents_title_description()
        new_build_apartment_map = {item.id: item.title for item in get_new_build_apartment_ids()}

        for user in userss:
            user_dataa.append({
                'id': user.id,
                'title': user.title,
                'text': user.text,
                'link': user.link,
                'new_build_apartment_title': new_build_apartment_map.get(user.new_build_apartment_id)
            })
        df = pd.DataFrame(user_dataa)
        edited_df = st.data_editor(df)

        if not df.equals(edited_df):
            for index, row in edited_df.iterrows():
                original_row = df.iloc[index]
                if row['id'] != original_row['id']:
                    continue  # skip the unchanged rows

                if (row['title'] != original_row['title'] or row['text'] != original_row['text'] or 
                    row['link'] != original_row['link'] or row['new_build_apartment_title'] != original_row['new_build_apartment_title']):
                    
                    new_build_apartment_id = [key for key, value in new_build_apartment_map.items() if value == row['new_build_apartment_title']][0]
                    
                    item_documents_title_description = {
                        "id": row['id'],
                        "title": row['title'],
                        "text": row['text'],
                        "link": row['link'],
                        "new_build_apartment_id": new_build_apartment_id
                    }
                    update_document_title_description(item_documents_title_description)

        st.subheader("Add Documents Title Description")
        with st.form("add_item_form_2"):
            title = st.text_input("Title")
            text = st.text_area("Text")
            link = st.text_input("Link")
            documents_title_ids = get_new_build_apartment_ids()
            new_build_apartment_id = st.selectbox("Documents Title ID", options=documents_title_ids, format_func=lambda x: x[1])
            submittedd = st.form_submit_button("Add Item")
            if submittedd:
                item_documents_title_description = {
                    "title": title,
                    "text": text,
                    "link": link,
                    "new_build_apartment_id": new_build_apartment_id[0]
                }
                add_document_title_description(item_documents_title_description)


        st.subheader("Delete Documents Title Description")
        with st.form("delete_item_form_2"):
            delete_id = st.number_input("ID to delete", min_value=0, step=1)
            delete_submitted = st.form_submit_button("Delete Item")

            if delete_submitted:
                delete_document_title_description(delete_id)




    elif choice == "3D model":
            st.subheader("Manage 3D Model")
            user_dataa = []

            users = get_3d_model()
            for user in users:
                user_dataa.append({
                    'id': user.id,
                    'filename': user.filename,
                    'new_build_apartment_id': user.new_build_apartment_id
                })
            df = pd.DataFrame(user_dataa)
            edited_dff = st.data_editor(df)

            if not df.equals(edited_dff):
                for index, row in edited_dff.iterrows():
                    original_row = df.iloc[index]
                    if row['id'] != original_row['id']:
                        continue  # skip the unchanged rows

                    updated_data = {column: row[column] for column in df.columns if column != 'id'}
                    new_build_apartment_id = row['id']
                    update_3d_model(new_build_apartment_id, updated_data)

            # Add file
            st.subheader("Add File")
            with st.form("add_file_form"):
                new_build_apartment_ids = get_new_build_apartment_ids()
                new_build_apartment_id = st.selectbox("New Build Apartment ID", options=new_build_apartment_ids, format_func=lambda x: x[1])
                file = st.file_uploader("Choose a file", type=["glb"])  # Allow video uploads
                submitted = st.form_submit_button("Upload File")

                if submitted and file is not None:
                    upload_3d_model(new_build_apartment_id[0], file)

            # Delete file
            st.subheader("Delete File")
            new_build_apartment_id = st.number_input("File ID to Delete", step=1)
            if st.button("Delete File"):
                delete_3d_model(new_build_apartment_id)









    if choicec == 'create video':
        st.subheader("CREATE VIDEO")
        with st.form("ADD IMAGE"):
            prompt = st.text_input("Prompt")
            image_url = st.text_input("Image Start URL (or only use one photo)")
            image_end_url = st.text_input("Image Finish URL")
            submitted = st.form_submit_button("Upload File")

            if submitted:
                response = create_video(image_url, image_end_url,prompt)
                task_id = response['data']['task_id']
                st.write("Video creation initiated. Task ID:", task_id)
                st.write("Checking status...")

                # Polling the video status
                while True:
                    status_response = get_video(task_id)
                    status = status_response['data']['status']
                    st.write(f"Current status: {status}")

                    if status == "completed":
                        video_url = status_response['data']['generation']['video']['url']
                        st.video(video_url)
                        st.write("Video created successfully!")
                        break
                    elif status == "failed":
                        st.write("Video creation failed. Please try again.")
                        break
                    else:
                        st.write("Processing... Please wait.")
                        time.sleep(5)  # Wait for 5 seconds before checking again




















    ######stastic##########
    if choicec == 'static all':
        st.subheader('Statistic')

        options = {
        "xAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        "yAxis": {"type": "value"},
        "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
        }
        events = {
            "click": "function(params) { console.log(params.name); return params.name }",
            "dblclick": "function(params) { return [params.type, params.name, params.value] }",
        }

        st.markdown("Click on a bar for label + value, double click to see type+name+value")
        s = st_echarts(
            options=options, events=events, height="500px", key="render_basic_bar_events"
        )
        if s is not None:
            st.write(s)


        options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": ["Direct", "Mail Ad", "Affiliate Ad", "Video Ad", "Search Engine"]
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "value"},
        "yAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },

        "series": [
            {
                "name": "Direct",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": [320, 302, 301, 334, 390, 330, 320],
            },
            {
                "name": "Mail Ad",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": [120, 132, 101, 134, 90, 230, 210],
            },
            {
                "name": "Affiliate Ad",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": [220, 182, 191, 234, 290, 330, 310],
            },
            {
                "name": "Video Ad",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": [150, 212, 201, 154, 190, 330, 410],
            },
            {
                "name": "Search Engine",
                "type": "bar",
                "stack": "total",
                "label": {"show": True},
                "emphasis": {"focus": "series"},
                "data": [820, 832, 901, 934, 1290, 1330, 1320],
            },
        ],
        }
        st_echarts(options=options, height="500px")
        option = {
        "legend": {"top": "bottom"},
        "toolbox": {
            "show": True,
            "feature": {
                "mark": {"show": True},
                "dataView": {"show": True, "readOnly": False},
                "restore": {"show": True},
                "saveAsImage": {"show": True},
            },
        },
        "series": [
            {
                "name": "面积模式",
                "type": "pie",
                "radius": [50, 250],
                "center": ["50%", "50%"],
                "roseType": "area",
                "itemStyle": {"borderRadius": 8},
                "data": [
                    {"value": 40, "name": "rose 1"},
                    {"value": 38, "name": "rose 2"},
                    {"value": 32, "name": "rose 3"},
                    {"value": 30, "name": "rose 4"},
                    {"value": 28, "name": "rose 5"},
                    {"value": 26, "name": "rose 6"},
                    {"value": 22, "name": "rose 7"},
                    {"value": 18, "name": "rose 8"},
                ],
            }
        ],
        }
        st_echarts(
            options=option, height="600px",
        )
        option = {
        "xAxis": {"data": ["2017-10-24", "2017-10-25", "2017-10-26", "2017-10-27"]},
        "yAxis": {},
        "series": [
            {
                "type": "k",
                "data": [
                    [20, 34, 10, 38],
                    [40, 35, 30, 50],
                    [31, 38, 33, 44],
                    [38, 15, 5, 42],
                ],
            }
        ],
        }
        st_echarts(option, height="500px")

        hours = [
        "12a",
        "1a",
        "2a",
        "3a",
        "4a",
        "5a",
        "6a",
        "7a",
        "8a",
        "9a",
        "10a",
        "11a",
        "12p",
        "1p",
        "2p",
        "3p",
        "4p",
        "5p",
        "6p",
        "7p",
        "8p",
        "9p",
        "10p",
        "11p",
        ]
        days = [
            "Saturday",
            "Friday",
            "Thursday",
            "Wednesday",
            "Tuesday",
            "Monday",
            "Sunday",
        ]

        data = [
            [0, 0, 5],
            [0, 1, 1],
            [0, 2, 0],
            [0, 3, 0],
            [0, 4, 0],
            [0, 5, 0],
            [0, 6, 0],
            [0, 7, 0],
            [0, 8, 0],
            [0, 9, 0],
            [0, 10, 0],
            [0, 11, 2],
            [0, 12, 4],
            [0, 13, 1],
            [0, 14, 1],
            [0, 15, 3],
            [0, 16, 4],
            [0, 17, 6],
            [0, 18, 4],
            [0, 19, 4],
            [0, 20, 3],
            [0, 21, 3],
            [0, 22, 2],
            [0, 23, 5],
            [1, 0, 7],
            [1, 1, 0],
            [1, 2, 0],
            [1, 3, 0],
            [1, 4, 0],
            [1, 5, 0],
            [1, 6, 0],
            [1, 7, 0],
            [1, 8, 0],
            [1, 9, 0],
            [1, 10, 5],
            [1, 11, 2],
            [1, 12, 2],
            [1, 13, 6],
            [1, 14, 9],
            [1, 15, 11],
            [1, 16, 6],
            [1, 17, 7],
            [1, 18, 8],
            [1, 19, 12],
            [1, 20, 5],
            [1, 21, 5],
            [1, 22, 7],
            [1, 23, 2],
            [2, 0, 1],
            [2, 1, 1],
            [2, 2, 0],
            [2, 3, 0],
            [2, 4, 0],
            [2, 5, 0],
            [2, 6, 0],
            [2, 7, 0],
            [2, 8, 0],
            [2, 9, 0],
            [2, 10, 3],
            [2, 11, 2],
            [2, 12, 1],
            [2, 13, 9],
            [2, 14, 8],
            [2, 15, 10],
            [2, 16, 6],
            [2, 17, 5],
            [2, 18, 5],
            [2, 19, 5],
            [2, 20, 7],
            [2, 21, 4],
            [2, 22, 2],
            [2, 23, 4],
            [3, 0, 7],
            [3, 1, 3],
            [3, 2, 0],
            [3, 3, 0],
            [3, 4, 0],
            [3, 5, 0],
            [3, 6, 0],
            [3, 7, 0],
            [3, 8, 1],
            [3, 9, 0],
            [3, 10, 5],
            [3, 11, 4],
            [3, 12, 7],
            [3, 13, 14],
            [3, 14, 13],
            [3, 15, 12],
            [3, 16, 9],
            [3, 17, 5],
            [3, 18, 5],
            [3, 19, 10],
            [3, 20, 6],
            [3, 21, 4],
            [3, 22, 4],
            [3, 23, 1],
            [4, 0, 1],
            [4, 1, 3],
            [4, 2, 0],
            [4, 3, 0],
            [4, 4, 0],
            [4, 5, 1],
            [4, 6, 0],
            [4, 7, 0],
            [4, 8, 0],
            [4, 9, 2],
            [4, 10, 4],
            [4, 11, 4],
            [4, 12, 2],
            [4, 13, 4],
            [4, 14, 4],
            [4, 15, 14],
            [4, 16, 12],
            [4, 17, 1],
            [4, 18, 8],
            [4, 19, 5],
            [4, 20, 3],
            [4, 21, 7],
            [4, 22, 3],
            [4, 23, 0],
            [5, 0, 2],
            [5, 1, 1],
            [5, 2, 0],
            [5, 3, 3],
            [5, 4, 0],
            [5, 5, 0],
            [5, 6, 0],
            [5, 7, 0],
            [5, 8, 2],
            [5, 9, 0],
            [5, 10, 4],
            [5, 11, 1],
            [5, 12, 5],
            [5, 13, 10],
            [5, 14, 5],
            [5, 15, 7],
            [5, 16, 11],
            [5, 17, 6],
            [5, 18, 0],
            [5, 19, 5],
            [5, 20, 3],
            [5, 21, 4],
            [5, 22, 2],
            [5, 23, 0],
            [6, 0, 1],
            [6, 1, 0],
            [6, 2, 0],
            [6, 3, 0],
            [6, 4, 0],
            [6, 5, 0],
            [6, 6, 0],
            [6, 7, 0],
            [6, 8, 0],
            [6, 9, 0],
            [6, 10, 1],
            [6, 11, 0],
            [6, 12, 2],
            [6, 13, 1],
            [6, 14, 3],
            [6, 15, 4],
            [6, 16, 0],
            [6, 17, 0],
            [6, 18, 0],
            [6, 19, 0],
            [6, 20, 1],
            [6, 21, 2],
            [6, 22, 2],
            [6, 23, 6],
        ]
        data = [[d[1], d[0], d[2] if d[2] != 0 else "-"] for d in data]

        option = {
        "tooltip": {"position": "top"},
        "grid": {"height": "50%", "top": "10%"},
        "xAxis": {"type": "category", "data": hours, "splitArea": {"show": True}},
        "yAxis": {"type": "category", "data": days, "splitArea": {"show": True}},
        "visualMap": {
            "min": 0,
            "max": 10,
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": "15%",
        },
        "series": [
            {
                "name": "Punch Card",
                "type": "heatmap",
                "data": data,
                "label": {"show": True},
                "emphasis": {
                    "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}
                },
            }
        ],
        }
        st_echarts(option, height="500px")