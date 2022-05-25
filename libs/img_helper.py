import os
import re
from werkzeug.datastructures import FileStorage
from flask_uploads import UploadSet, IMAGES
from typing import Union

IMAGE_SET = UploadSet('images', IMAGES)

def save_image(image: FileStorage, folder: str=None, name: str=None) -> str:
    return IMAGE_SET.save(image, folder, name)

def get_path(filename: str=None, folder: str=None) -> str:
    return IMAGE_SET.path(filename, folder)

def find_image_any_format(filename: str=None, folder: str=None) -> Union[str, None]:
    for _format in IMAGES:
        image = f"{filename}.{_format}"
        image_path = get_path(filename=image, folder=folder)
        if os.path.isfile(image_path):
            return image_path
    return None

def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    if isinstance(file, FileStorage):
        return file.filename
    return file

def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    file_name = _retrieve_filename(file)
    allowed_format = "|".join(IMAGES)
    regex = f"[a-zA-Z0-9][a-zA-Z0-9_()-]*\.({allowed_format})$"
    return re.match(regex, file_name) is not None

def get_basename(file: Union[str, FileStorage]) -> str:
    file_name = _retrieve_filename(file)
    return os.path.split(file_name)[1]

def get_extension(file: Union[str, FileStorage]) -> str:
    file_name = _retrieve_filename(file)
    return os.path.splitext(file_name)[1]