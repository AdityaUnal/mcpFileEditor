import requests
import shutil
import os
import logging

logging.basicConfig(
    filename='client.log',        # Logs to a file
    filemode='a',              # 'a' for append, 'w' to overwrite
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO         # Only logs INFO and above
)

class MCPClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def upload_folder(self, folder_path):
        try:
            zip_path = shutil.make_archive("temp_folder", 'zip', folder_path)
            with open(zip_path, "rb") as f:
                files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
                logging.info(f"Post request made to {self.base_url}/create/folder/")
                response = requests.post(f"{self.base_url}/create/folder/", files=files)
                data = response.json()
                logging.info(f"New folder created at {data["path"]}")
        except Exception as e:
            logging.error(f"Exception occured while creating folder : {e} ")

        return response.json()

    def create_file(self, file_name, folder_path, base_folder):
        try:
            base_folder_path = base_folder
            if folder_path is not None:
                base_folder_path = os.path.join(base_folder,folder_path)
            if not os.path.exists(base_folder_path):
                os.makedirs(base_folder_path)
            file_name = os.path.join(base_folder_path,file_name)
            url = f"{self.base_url}/create/file/{file_name}"
            logging.info(f"Post request made to {url}")
            return requests.post(url)
        except Exception as e:
            logging.error(f"Excpetion occured while creating a file : {e}")


    def delete_file(self, file_path, base_folder):
        try :
            file_path = os.path.join(base_folder,file_path)
            url = f"{self.base_url}/delete/file/{file_path}"
            logging.info(f"delete request made to {url}")
            return requests.delete(url)
        except Exception as e:
            logging.error(f"Excpetion occured while deleting the file : {e}")


    def read_file(self, file_path,base_folder):
        try :
            file_path = os.path.join(base_folder,file_path)
            url = f"{self.base_url}/content/{file_path}"
            logging.info(f"read request made to {url}")
            response = requests.get(url)
            logging.info(f"Content succesfully recieved.")
            return response.json()
        except Exception as e:
            logging.error("Error : ", e)

    def edit_file(self, file_path, new_content,base_folder):
        try :
            file_path = os.path.join(base_folder,file_path)
            url = f"{self.base_url}/save_edit/{file_path}"
            logging.info(f"edit request made to {url}")
            data = {"content": new_content}
            response = requests.post(url,json = data).json()
            return response
            logging.info(f"Contents succesfully edited.")
        except Exception as e:
            logging.error("Error : ", e)
