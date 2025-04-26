#
# Item.py
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

import os
import urllib.parse

from django.utils.text import get_valid_filename

from com.yoclabo.filesystem.query.Query import *
from com.yoclabo.setting import Server

import environ
env = environ.Env()
env.read_env('.env')

class Item:

    def __init__(self, path: str, sequence: int) -> None:
        self.f_id: Path = Path(path)
        self.f_type: str = get_type(self.f_id)
        self.f_name: str = get_name(self.f_id)
        self.f_sequence: int = sequence
        self.f_ancestors: list = []
        return

    @property
    def id(self) -> str:
        return urllib.parse.quote(str(self.f_id).replace(Server.get_root_directory_path(), ''))

    @property
    def type(self) -> str:
        return self.f_type

    @property
    def name(self) -> str:
        return self.f_name

    @property
    def sequence(self) -> int:
        return self.f_sequence

    @property
    def ancestors(self) -> list:
        return self.f_ancestors

    @property
    def row_display_attributes(self) -> str:
        if self.f_sequence % 2 == 0:
            return 'bg-secondary bg-opacity-10'
        return 'border-top border-bottom'

    def fill_ancestors(self) -> None:
        for a in query_ancestors(self.f_id):
            self.f_ancestors.append(Item(str(a), 0))
        return


class Directory(Item):

    def __init__(self, path: str, sequence: int) -> None:
        super().__init__(path, sequence)
        self.f_children_info: list = []
        self.f_children: list = []
        self.f_page: int = 0
        self.f_pages: list = []
        self.f_is_tile: bool = False
        self.SLIDE_SHOW_INTERVAL_MS: int = env.int('SLIDE_SHOW_INTERVAL_MS', default=3000)
        self.ITEMS_PER_PAGE: int = env.int('ITEMS_PER_PAGE', default=10)
        self.TILE_ITEMS_PER_PAGE: int = env.int('TILE_ITEMS_PER_PAGE', default=30)
        return

    @property
    def children(self) -> list:
        return self.f_children

    @property
    def page(self) -> int:
        return self.f_page

    @property
    def pages(self) -> list:
        return self.f_pages

    @property
    def max_page(self) -> int:
        if 0 == len(self.f_children_info):
            return 1
        if self.f_is_tile:
            return -(-len(self.f_children_info) // self.TILE_ITEMS_PER_PAGE)
        return -(-len(self.f_children_info) // self.ITEMS_PER_PAGE)

    @property
    def prev_page(self) -> int:
        return self.f_page - 1 if 1 < self.f_page else 1

    @property
    def next_page(self) -> int:
        return self.f_page + 1 if self.max_page > self.f_page else self.max_page

    @property
    def is_tile(self) -> bool:
        return self.f_is_tile

    @property
    def slide_show_interval_ms(self) -> int:
        return self.SLIDE_SHOW_INTERVAL_MS

    def cache_children_info(self) -> None:
        l_children: list = query_children(self.f_id)
        i: int = 1
        for child in l_children:
            if get_type(child) == 'directory':
                self.f_children_info.append(Directory(str(child), i))
            elif get_type(child) == 'image':
                self.f_children_info.append(Image(str(child), i))
            elif get_type(child) == 'pdf':
                self.f_children_info.append(Pdf(str(child), i))
            elif get_type(child) == 'media':
                self.f_children_info.append(Media(str(child), i))
            else:
                self.f_children_info.append(Item(str(child), i))
            i += 1
        return

    def slice(self) -> None:
        l_start = self.TILE_ITEMS_PER_PAGE * (self.f_page - 1) if self.is_tile \
            else self.ITEMS_PER_PAGE * (self.f_page - 1)
        l_end = l_start + self.TILE_ITEMS_PER_PAGE if self.is_tile else l_start + self.ITEMS_PER_PAGE
        l_end = len(self.f_children_info) if len(self.f_children_info) < l_end else l_end
        for i in range(l_start, l_end):
            self.f_children.append(self.f_children_info[i])
        return

    def prepare_browse(self, page: int, is_tile: bool) -> None:
        self.fill_ancestors()
        self.f_page = page
        self.f_is_tile = is_tile
        self.cache_children_info()
        self.f_pages = Paginator().create_list(page, self.prev_page, self.next_page, self.max_page)
        self.slice()
        return

    def create_directory(self, name: str) -> None:
        if not name:
            return
        l_directory_path = Path(os.path.join(get_path_from_root_directory(self.id), get_valid_filename(name)))
        create_directory(l_directory_path)
        return

    def create_text_file(self, name: str, content: str) -> None:
        if not name:
            return
        l_text_file_path = Path(os.path.join(get_path_from_root_directory(self.id), get_valid_filename(name if name.endswith('.txt') else name + '.txt')))
        update_text_content(l_text_file_path, content)
        return

    def save_file(self, files: dict) -> None:
        l_dir = get_path_from_root_directory(self.id)
        with open(os.path.join(l_dir, get_valid_filename(files['uploadFile'].name)), 'wb+') as dest:
            for c in files['uploadFile'].chunks():
                dest.write(c)
        return


class Text(Item):

    def __init__(self, path: str, sequence: int) -> None:
        super().__init__(path, sequence)
        self.f_content: str = ''
        return

    @property
    def content(self) -> str:
        return self.f_content

    def get_text_content(self) -> None:
        self.f_content = get_text_content(self.f_id)
        return

    def update_text_content(self, new_content: str) -> None:
        update_text_content(self.f_id, new_content)
        return

    def prepare_view(self) -> None:
        self.fill_ancestors()
        self.get_text_content()
        return


class Image(Item):

    def __init__(self, path: str, sequence: int) -> None:
        super().__init__(path, sequence)
        self.f_image: str = ''
        return

    @property
    def image(self) -> str:
        return self.f_image

    def get_web_encoded_image(self) -> str:
        return get_web_encoded_image(self.f_id)

    def get_image_bytearray(self) -> bytes:
        return get_image_bytearray(self.f_id)

    def prepare_view(self) -> None:
        self.fill_ancestors()
        self.f_image = self.get_web_encoded_image()
        return


class Pdf(Item):

    def __init__(self, path: str, sequence: int) -> None:
        super().__init__(path, sequence)
        return

    def prepare_view(self) -> None:
        self.fill_ancestors()
        copy_file_to_static(str(self.f_id), self.f_name)
        return


class Media(Item):

    def __init__(self, path: str, sequence: int) -> None:
        super().__init__(path, sequence)
        return

    def prepare_view(self) -> None:
        self.fill_ancestors()
        copy_file_to_static(str(self.f_id), self.f_name)
        return


class Paginator:

    def __init__(self) -> None:
        self.f_page: int = 0
        self.f_text: str = ''
        self.f_is_current: bool = False
        self.CAPTION_PREV: str = 'Previous'
        self.CAPTION_NEXT: str = 'Next'
        self.CAPTION_DOT: str = '...'
        return

    @property
    def page(self) -> int:
        return self.f_page

    @property
    def text(self) -> str:
        return self.f_text

    @property
    def is_current(self) -> bool:
        return self.f_is_current

    @page.setter
    def page(self, arg: int) -> None:
        self.f_page = arg
        return

    @text.setter
    def text(self, arg: str) -> None:
        self.f_text = arg
        return

    @is_current.setter
    def is_current(self, arg: bool) -> None:
        self.f_is_current = arg
        return

    def create_list(self, current_page: int, prev_page: int, next_page: int, max_page: int) -> list:
        l_pages: list = []
        if 9 > max_page:
            l_pages = self.create_first_2(l_pages, prev_page)
            l_pages = self.create_center(l_pages, 2, max_page)
            l_pages = self.create_last_2(l_pages, next_page, max_page)
            l_pages = self.mark_current(l_pages, current_page)
            return l_pages
        if 1 + 4 > current_page:
            l_pages = self.create_first_2(l_pages, prev_page)
            l_pages = self.create_center(l_pages, 2, current_page + 3)
            l_pages = self.create_next_dot(l_pages, current_page)
            l_pages = self.create_last_2(l_pages, next_page, max_page)
            l_pages = self.mark_current(l_pages, current_page)
            return l_pages
        if max_page - 4 < current_page:
            l_pages = self.create_first_2(l_pages, prev_page)
            l_pages = self.create_prev_dot(l_pages, current_page)
            l_pages = self.create_center(l_pages, current_page - 2, max_page)
            l_pages = self.create_last_2(l_pages, next_page, max_page)
            l_pages = self.mark_current(l_pages, current_page)
            return l_pages
        l_pages = self.create_first_2(l_pages, prev_page)
        l_pages = self.create_prev_dot(l_pages, current_page)
        l_pages = self.create_center(l_pages, current_page - 2, current_page + 3)
        l_pages = self.create_next_dot(l_pages, next_page)
        l_pages = self.create_last_2(l_pages, next_page, max_page)
        l_pages = self.mark_current(l_pages, current_page)
        return l_pages

    def create_first_2(self, pages: list, prev_page: int) -> list:
        l_add = Paginator()
        l_add.page = 1
        l_add.text = '1'
        pages.append(l_add)
        l_add = Paginator()
        l_add.page = prev_page
        l_add.text = self.CAPTION_PREV
        pages.append(l_add)
        return pages

    def create_prev_dot(self, pages: list, current_page: int) -> list:
        l_add = Paginator()
        l_add.page = current_page - 3
        l_add.text = self.CAPTION_DOT
        pages.append(l_add)
        return pages

    @staticmethod
    def create_center(pages: list, start: int, end: int) -> list:
        for p in range(start, end):
            l_add = Paginator()
            l_add.page = p
            l_add.text = str(p)
            pages.append(l_add)
        return pages

    def create_next_dot(self, pages: list, current_page: int) -> list:
        l_add = Paginator()
        l_add.page = current_page + 3
        l_add.text = self.CAPTION_DOT
        pages.append(l_add)
        return pages

    def create_last_2(self, pages: list, next_page: int, max_page: int) -> list:
        l_add = Paginator()
        l_add.page = next_page
        l_add.text = self.CAPTION_NEXT
        pages.append(l_add)
        l_add = Paginator()
        l_add.page = max_page
        l_add.text = str(max_page)
        pages.append(l_add)
        return pages

    @staticmethod
    def mark_current(pages: list, current_page: int) -> list:
        for p in pages:
            if current_page == p.page:
                p.is_current = True
        return pages
