#
# Query.py
#
# Copyright 2024 Yuichi Yoshii
#     吉井雄一 @ 吉井産業  you.65535.kir@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import base64
import os
import os.path
import shutil
import stat
from pathlib import Path

from django.utils.text import get_valid_filename

from browser.settings import BASE_DIR
from com.yoclabo.setting.Server import get_root_directory_path

ITEM_TYPE_DIRECTORY = 'directory'

ITEM_TYPE_TEXT = 'text'

ITEM_TYPE_IMAGE = 'image'

ITEM_TYPE_PDF = 'pdf'

ITEM_TYPE_MEDIA = 'media'

ITEM_TYPE_OTHER = 'other'


def get_path_from_root_directory(path: str) -> str:
    return os.path.join(get_root_directory_path(), path[1:]) if path.startswith('/') else os.path.join(
        get_root_directory_path(), path)


def query_ancestors(path: str, type: str, ancestors: list = None) -> list:
    if path == get_root_directory_path():
        return [{'id': path, 'type': ITEM_TYPE_DIRECTORY, 'name': os.path.basename(path)}]
    if len(Path(path).parts) == 1:
        return [{'id': path, 'type': ITEM_TYPE_DIRECTORY, 'name': os.path.basename(path)}]
    if ancestors is None:
        ancestors = []
    if os.path.isdir(path):
        ancestors = query_ancestors(os.path.dirname(path), ITEM_TYPE_DIRECTORY, ancestors) + [
            {'id': path, 'type': ITEM_TYPE_DIRECTORY, 'name': os.path.basename(path)}]
    else:
        ancestors = query_ancestors(os.path.dirname(path), ITEM_TYPE_DIRECTORY, ancestors)
    return ancestors


def query_children(path: str) -> list:
    l_children: list = []
    for c in Path(path).iterdir():
        if os.path.isdir(c):
            l_children.append({'id': str(c), 'type': ITEM_TYPE_DIRECTORY, 'name': os.path.basename(str(c))})
    for c in Path(path).iterdir():
        if os.path.isfile(c):
            l_file_name = os.path.basename(str(c))
            l_children.append({'id': str(c), 'type': get_type(l_file_name), 'name': l_file_name})
    return l_children


def get_type(path: str) -> str:
    l_p: Path = Path(path)
    if l_p.is_dir():
        return ITEM_TYPE_DIRECTORY
    if l_p.name.startswith('.'):
        return 'hidden_file'
    if l_p.suffix == '.txt' or l_p.suffix == '.text':
        return ITEM_TYPE_TEXT
    if l_p.suffix == '.jpg' or l_p.suffix == '.jpeg' or l_p.suffix == '.png' or l_p.suffix == '.gif':
        return ITEM_TYPE_IMAGE
    if l_p.suffix == '.pdf':
        return ITEM_TYPE_PDF
    if (l_p.suffix == '.mp4' or l_p.suffix == '.mp3' or l_p.suffix == '.m4a'
            or l_p.suffix == '.flv' or l_p.suffix == '.wmv'):
        return ITEM_TYPE_MEDIA
    return ITEM_TYPE_OTHER


def create_directory(path: str, name: str) -> None:
    l_path = os.path.join(path, get_valid_filename(name))
    if os.path.exists(l_path):
        return
    os.mkdir(l_path)
    return


def create_file(path: str, name: str, content: any) -> None:
    name = get_valid_filename(name)
    l_path = os.path.join(path, name)
    if os.path.exists(l_path):
        return
    if isinstance(content, str):
        with open(l_path, 'w') as dest:
            dest.write(content)
    if isinstance(content, dict):
        with open(l_path, 'wb+') as dest:
            for c in content['uploadFile'].chunks():
                dest.write(c)
    return


def get_text_content(path: str) -> str:
    return open(path).read()


def update_text_content(path: str, name: str, content: str) -> None:
    if os.path.isdir(path):
        return
    with open(path, 'w') as cont:
        cont.write(content)
    return


def rename(path: str, old_name: str, new_name: str) -> None:
    if not new_name:
        return
    old_name = get_valid_filename(old_name)
    if not os.path.exists(os.path.join(path, old_name)):
        old_name = old_name.replace('_', ' ')
    new_name = get_valid_filename(new_name)
    os.rename(os.path.join(path, old_name), os.path.join(path, new_name))
    return


def get_web_encoded_image(path: str) -> str:
    return 'data:image/jpeg;base64,' + base64.b64encode(open(str(path), 'rb').read()).decode()


def get_image_bytearray(path: str) -> bytes:
    return open(str(path), 'rb').read()


def copy_file_to_static(copy_from: str, copy_to: str) -> None:
    l_copy_to = os.path.join(BASE_DIR, 'static', copy_to)
    if os.path.exists(l_copy_to):
        os.remove(l_copy_to)
    shutil.copy(copy_from, l_copy_to)
    os.chmod(l_copy_to, stat.S_IREAD | stat.S_IWRITE | stat.S_IROTH)
    return
