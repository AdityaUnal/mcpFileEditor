from fastapi import FastAPI,UploadFile, File
from typing import Union
import os
import logging
from fastapi.responses import JSONResponse
from starlette import status
import shutil
import zipfile
import tempfile

app = FastAPI()

logging.basicConfig(
    filename='server.log',        # Logs to a file
    filemode='a',              # 'a' for append, 'w' to overwrite
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO         # Only logs INFO and above
)

from pydantic import BaseModel

class FileContent(BaseModel):
    content: str

@app.get("/")
async def healthcheck():
    return "hello"

base_folder = os.getcwd()

@app.post("/create/folder/")
async def create_folder(file: UploadFile = File(...)):
    try:
        # Save uploaded zip temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Extract contents
        extract_dir_name = os.path.splitext(file.filename)[0]
        extract_path = os.path.join(os.getcwd(), extract_dir_name)
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        os.remove(tmp_path)
        return JSONResponse(
            content={
                "message": f"Folder '{extract_dir_name}' created successfully.",
                "path": extract_path   
            },
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_400_BAD_REQUEST
        )

def find_directory(target_dir_name, start_path='.'):
    for root, dirs, files in os.walk(start_path):
        if target_dir_name in dirs:
            return os.path.join(root, target_dir_name)
    return None


@ app.post("/create/file/{file_name}")
async def create_file(file_name: str,folder_path: Union[str,None] = None):
    try:
        start_from = os.getcwd()  # or any base path
        found_path = find_directory("temp_folder", start_from)
        base_folder_path = found_path
        if(folder_path == None):
            file_path = os.path.join(found_path,file_name)
        else :
            base_folder_path = os.path.join(found_path,folder_path)
            file_path = os.path.join(base_folder_path,file_name)
        if not os.path.exists(base_folder_path):
            os.makedirs(base_folder_path)
        logging.info(f"Request recieved to create {file_name} at {file_path}")
        with open(file_path, "x") as file:
            logging.info(f"{file_name} created successfully")
        response = JSONResponse(content={"message": f"{file_name} created in {base_folder_path}"}, status_code=status.HTTP_201_CREATED)
    except FileExistsError:
        logging.error(f"{file_name} already exists in {found_path}")
        response = JSONResponse(content={"message": f"{file_name} already exists in {base_folder_path}"}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logging.error(f"While creating file : {e}")
        response = JSONResponse(content={"message": f"While creating file : {e}"}, status_code=status.HTTP_400_BAD_REQUEST)
        
    return response    
        
@app.delete("/delete/folder/{folder_path}")
async def delete_folder(folder_path: str):
    try:
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            logging.info(f"{folder_path} directory successfully deleted.")
            response = JSONResponse(content={"message": f"{folder_path} directory successfully deleted"}, status_code=status.HTTP_204_NO_CONTENT)
        else:
            logging.error(f"{folder_path} is not a directory or does not exist.")
            response = JSONResponse(content={"message": f"{folder_path} is not a directory or does not exist."}, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logging.error(f"Error deleting directory {folder_path}: {e}")
        response = JSONResponse(content={"message": f"Error deleting directory {folder_path}: {e}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response

    
@ app.delete("/delete/file/{file_path}")
async def delete_file(file_path:str):
    try:
        os.remove(file_path)
        logging.info(f"{file_path} successfully deleted.")
        response = JSONResponse(content={"message": f"{file_path} successfully deleted"}, status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logging.error(f"Cannot delte due to error : {e}")
        response = JSONResponse(content={"message":f"Error : {e}"}, status_code=status.HTTP_400_BAD_REQUEST)
    
    return response


@ app.get("/content/{file_path}")
async def show_file(file_path:str):
    try:
        with open(file_path, "r") as file:
            content = file.read()
        
        logging.info(f"Contents of {file_path} are successfully sent.")
        return JSONResponse(
            content={
                "message": f"{file_path} successfully retrieved",
                "content": content
            },
            status_code=status.HTTP_200_OK
        )
    
    except FileNotFoundError:
        logging.error(f"{file_path} not present.")
        return JSONResponse(
            content={"message": f"File {file_path} not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    

@ app.post("/save_edit/{file_path}")
async def save_file(file_path:str,file_data: FileContent):
    try:
        with open(file_path, "w") as file:
           file.write(file_data.content)

        
        logging.info(f"Contents of {file_path} are successfully updated.")
        return JSONResponse(
            content={"message": f"{file_path} successfully updated"},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logging.erorr(f"Contents of {file_path} are not updated : {e}")
        return JSONResponse(
            content={"message": f"File {file_path} not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )

        