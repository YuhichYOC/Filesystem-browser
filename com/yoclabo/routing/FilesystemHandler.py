#
# FilesystemHandler.py
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

from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse
from django.shortcuts import render

from com.yoclabo.filesystem.item.Item import Directory, Image, Pdf, Media
from com.yoclabo.setting import Server


def go_to_root(page: int, tile: bool) -> dict:
    l_d = Directory(Server.get_root_directory_path(), 1)
    l_d.prepare_browse(page, tile)
    return {'directory': l_d}


def go_to_directory(path: str, page: int, tile: bool) -> dict:
    l_d = Directory(Server.get_root_directory_path() + path, 1)
    l_d.prepare_browse(page, tile)
    return {'directory': l_d}


def view_image(path: str) -> dict:
    l_i = Image(Server.get_root_directory_path() + path, 1)
    l_i.prepare_view()
    return {'document': l_i}


def view_pdf(path: str) -> dict:
    l_p = Pdf(Server.get_root_directory_path() + path, 1)
    l_p.prepare_view()
    return {'document': l_p}


def view_media(path: str) -> dict:
    l_m = Media(Server.get_root_directory_path() + path, 1)
    l_m.prepare_view()
    return {'document': l_m}


def get_web_encoded_image(path: str) -> str:
    l_i = Image(Server.get_root_directory_path() + path, 1)
    return l_i.get_web_encoded_image()


def get_image_bytearray(path: str) -> bytes:
    l_i = Image(Server.get_root_directory_path() + path, 1)
    return l_i.get_image_bytearray()


class FilesystemHandler:

    def __init__(self, request: WSGIRequest) -> None:
        self.f_request: WSGIRequest = request
        return

    @property
    def request(self) -> WSGIRequest:
        return self.f_request

    def has_get_param(self, name: str) -> bool:
        return self.request.GET.get(name) is not None

    def has_post_param(self, name: str) -> bool:
        return self.request.POST.get(name) is not None

    def get_param(self, name: str) -> str:
        if self.has_post_param(name):
            return self.request.POST.get(name)
        return self.request.GET.get(name)

    def run(self) -> None:
        pass


class FilesystemImageBytearrayHandler(FilesystemHandler):

    def run(self) -> HttpResponse:
        return HttpResponse(get_image_bytearray(self.get_param('id')), content_type='application/octet-stream')


class FilesystemWebEncodedImageHandler(FilesystemHandler):

    def run(self) -> HttpResponse:
        return HttpResponse(get_web_encoded_image(self.get_param('id')), content_type='text/plain')


class FilesystemDocumentHandler(FilesystemHandler):

    def run(self) -> HttpResponse:
        if self.get_param('type') == 'media':
            return render(self.request, 'filesystem/view.html', view_media(self.get_param('id')))
        if self.get_param('type') == 'pdf':
            return render(self.request, 'filesystem/view.html', view_pdf(self.get_param('id')))
        return render(self.request, 'filesystem/view.html', view_image(self.get_param('id')))


class FilesystemDirectoryHandler(FilesystemHandler):

    def run(self) -> HttpResponse:
        l_page: int = 1
        if self.has_get_param('page'):
            l_page = int(self.get_param('page'))
        l_tile: bool = False
        if self.has_get_param('tile'):
            l_tile = bool(self.get_param('tile'))
        return render(self.request, 'filesystem/browse.html',
                      go_to_directory(self.get_param('id'), l_page, l_tile))


class FilesystemRootDirectoryHandler(FilesystemHandler):

    def run(self) -> HttpResponse:
        l_page: int = 1
        if self.has_get_param('page'):
            l_page = int(self.get_param('page'))
        l_tile: bool = False
        if self.has_get_param('tile'):
            l_tile = bool(self.get_param('tile'))
        return render(self.request, 'filesystem/browse.html',
                      go_to_root(l_page, l_tile))
