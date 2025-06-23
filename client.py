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

    def create_folder(self, folder_path):
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

    def create_file(self, file_name, folder_path=None):
        try:
            params = {"folder_path": folder_path} if folder_path else {}
            url = f"{self.base_url}/create/file/{file_name}"
            logging.info(f"Post request made to {self.base_url}/create/file/{file_name}")
            response = requests.post(url, params=params)
        except Exception as e:
            logging.error(f"Excpetion occured while creating a file : {e}")
        return response


    def delete_file(self, file_path, base_folder):
        try :
            file_path = os.path.join(base_folder,file_path)
            file_path = os.path.join(base_folder,file_path)
            url = f"{self.base_url}/delete/file/{file_path}"
            logging.info(f"delete request made to {url}")
            response = requests.delete(url)
        except Exception as e:
            logging.error(f"Excpetion occured while deleting the file : {e}")
        return response

    def delete_folder(self, folder_path):
        url = f"{self.base_url}/delete/folder/{folder_path}"
        return requests.delete(url).json()

    def read_file(self, file_path,base_folder):
        try :
            file_path = os.path.join(base_folder,file_path)
            url = f"{self.base_url}/content/{file_path}"
            logging.info(f"read request made to {url}")
            response = requests.get(url)
            logging.info(f"Content succesfully recieved.")
        except Exception as e:
            logging.error("Error : ", e)
        return response.json()

    def edit_file(self, file_path, new_content,base_folder):
        try :
            file_path = os.path.join(base_folder,file_path)
            url = f"{self.base_url}/save_edit/{file_path}"
            logging.info(f"edit request made to {url}")
            data = {"content": new_content}
            response = requests.post(url,json = data).json()
            logging.info(f"Contents succesfully edited.")
        except Exception as e:
            logging.error("Error : ", e)
        return response
