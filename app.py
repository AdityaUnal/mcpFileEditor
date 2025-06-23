import streamlit as st
import tkinter as tk
from tkinter import filedialog
import os
import importlib
import client
importlib.reload(client)
from client import MCPClient
import shutil
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT
)

st.set_page_config(page_title="MCP File Editor", layout="wide")

client = MCPClient()

st.title(" MCP File Editor")

# Upload folder (zip)
st.sidebar.header("Upload Folder")

def get_tree(path, prefix=""):
    tree = ""
    files = sorted(os.listdir(path))
    for idx, file in enumerate(files):
        full_path = os.path.join(path, file)
        connector = "└── " if idx == len(files) - 1 else "├── "
        tree += prefix + connector + file + "\n"
        if os.path.isdir(full_path):
            extension = "    " if idx == len(files) - 1 else "│   "
            tree += get_tree(full_path, prefix + extension)
    return tree

with st.sidebar:
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    st.write('Please select a folder:')
    clicked = st.button('Browse Folder')
    
if clicked:
    if 'dirname' in st.session_state:
        dest = filedialog.askdirectory(master=root, title="Select a destination to save the current directory")
        if dest:
            shutil.move(st.session_state['dirname'], dest)
        else:
            shutil.rmtree(st.session_state['dirname'])
    dirname = str(filedialog.askdirectory(master=root))
    if dirname:
        response = client.upload_folder(dirname)
        st.session_state['dirname'] = response["path"]

# Use the stored dirname if available
if 'dirname' in st.session_state:
    dirname = st.session_state['dirname']
    st.subheader("Folder Tree")
    tree_str = get_tree(dirname)
    st.code(tree_str, language="text")

    st.subheader("Create a New File")
    file_name = st.text_input("Enter new file name (e.g., myfile.txt):")
    folder_path = st.text_input("Enter directory (optional, relative to base, e.g., insidedemo\hello):")
    if st.button("Create File"):
        if file_name:
            response = client.create_file(file_name, folder_path if folder_path else None,dirname)
            if response and response.status_code==HTTP_201_CREATED:
                st.rerun()  # This will rerun the script from the top
            elif response:
                st.error(f"Error : {response.json()["message"]}")
        else:
            st.warning("Please enter a file name.")

    st.subheader("Delete a File")
    file_to_delete = st.text_input("Enter file path to delete (e.g., hello\hello.txt):", key="delete_file")
    if st.button("Delete File"):
        if file_to_delete:
            response = client.delete_file(file_to_delete,dirname)
            if response and response.status_code==HTTP_204_NO_CONTENT:
                st.rerun()  # This will rerun the script from the top
            else:
                st.error("Failed to delete file. Please check the file path.")
        else:
            st.warning("Please enter a file path.")

    st.subheader("Update a File")
    update_file_path = st.text_input("Enter file path to update (e.g., temp_folder\hello.txt):", key="update_file")
    file_content = ""
    if st.button("Load File Content"):
        if update_file_path:
            response = client.read_file(update_file_path,dirname)

            if response and "content" in response:
                st.session_state["edit_content"] = response["content"]
            else:
                st.session_state["edit_content"] = ""
                st.error("Failed to load file content. Please check the file path.")
        else:
            st.warning("Please enter a file path.")

    if "edit_content" in st.session_state:
        edited_content = st.text_area("Edit file content:", value=st.session_state["edit_content"], height=300)
        if st.button("Save Changes"):
            if update_file_path:
                response = client.edit_file(update_file_path, edited_content, dirname)
                if response and "message" in response:
                    st.success(response["message"])
                    st.session_state.pop("edit_content", None)
                    st.rerun()
                else:
                    st.error("Failed to update file. Please check the file path and content.")
            else:
                st.warning("Please enter a file path.")

    
