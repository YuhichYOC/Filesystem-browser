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

from browser.settings import BASE_DIR
from com.yoclabo.setting.Server import get_root_directory_path


def get_path_from_root_directory(path: str) -> str:
    return os.path.join(get_root_directory_path(), path[1:]) if path.startswith('/') else os.path.join(get_root_directory_path(), path)


def query_ancestors(path: Path, ancestors: list = None) -> list:
    if str(path) == get_root_directory_path():
        return [path]
    if len(path.parts) == 1:
        return [path]
    if ancestors is None:
        ancestors = []
    ancestors = query_ancestors(path.parent, ancestors) + [path]
    return ancestors


def query_children(path: Path) -> list:
    l_children: list = []
    for c in path.iterdir():
        if os.path.isdir(c):
            l_children.append(c)
    for c in path.iterdir():
        if os.path.isfile(c):
            l_children.append(c)
    return l_children


def get_type(path: Path) -> str:
    if path.is_dir():
        return 'directory'
    if path.name.startswith('.'):
        return 'hidden_file'
    if path.suffix == '.txt' or path.suffix == '.text':
        return 'text'
    if path.suffix == '.jpg' or path.suffix == '.jpeg' or path.suffix == '.png' or path.suffix == '.gif':
        return 'image'
    if path.suffix == '.pdf':
        return 'pdf'
    if (path.suffix == '.mp4' or path.suffix == '.mp3' or path.suffix == '.m4a'
            or path.suffix == '.flv' or path.suffix == '.wmv'):
        return 'media'
    return 'other'


def create_directory(path: Path) -> None:
    if os.path.exists(path):
        return
    os.mkdir(path)
    return


def get_name(path: Path) -> str:
    return path.name


def get_text_content(path: Path) -> str:
    return open(path).read()


def update_text_content(path: Path, content: str) -> None:
    if os.path.isdir(path):
        return
    with open(path, 'w') as cont:
        cont.write(content)
    return


def get_web_encoded_image(path: Path) -> str:
    return 'data:image/jpeg;base64,' + base64.b64encode(open(str(path), 'rb').read()).decode()


def get_image_bytearray(path: Path) -> bytes:
    return open(str(path), 'rb').read()


def copy_file_to_static(copy_from: str, copy_to: str) -> None:
    l_copy_to = os.path.join(BASE_DIR, 'static', copy_to)
    if os.path.exists(l_copy_to):
        os.remove(l_copy_to)
    shutil.copy(copy_from, l_copy_to)
    os.chmod(l_copy_to, stat.S_IREAD | stat.S_IWRITE | stat.S_IROTH)
    return
