#
# Router.py
#
# Copyright 2021 Yuichi Yoshii
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

from com.yoclabo.routing import BrowserHandler, FilesystemHandler


def run_browser_handler(handler: BrowserHandler) -> HttpResponse:
    return handler.run()


def run_filesystem_handler(handler: FilesystemHandler) -> HttpResponse:
    return handler.run()


class Router:

    def __init__(self, request: WSGIRequest) -> None:
        self.f_request: WSGIRequest = request
        return

    @property
    def request(self) -> WSGIRequest:
        return self.f_request

    def has_get_param(self, name: str) -> bool:
        if self.request.GET.get(name) is None:
            return False
        if not self.request.GET.get(name):
            return False
        return True

    def has_post_param(self, name: str) -> bool:
        if self.request.POST.get(name) is None:
            return False
        if not self.request.POST.get(name):
            return False
        return True

    def get_param(self, name: str) -> str:
        if self.has_post_param(name):
            return self.request.POST.get(name)
        return self.request.GET.get(name)


class BrowserRouter(Router):

    def __init__(self, request: WSGIRequest):
        super().__init__(request)

    def run(self) -> HttpResponse:
        h = BrowserHandler.BrowserHandler(self.request)
        return run_browser_handler(h)


class FilesystemRouter(Router):

    def __init__(self, request: WSGIRequest):
        super().__init__(request)

    def is_image_bytearray_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('content'):
            return False
        if self.get_param('content') != 'bytes':
            return False
        return True

    def is_web_encoded_image_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('content'):
            return False
        if self.get_param('content') != 'encoded':
            return False
        return True

    def is_document_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('type'):
            return False
        if self.get_param('type') == 'media':
            return True
        if self.get_param('type') == 'pdf':
            return True
        if self.get_param('type') == 'image':
            if self.has_get_param('content'):
                return False
            return True
        return False

    def is_directory_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        return True

    def is_root_get(self) -> bool:
        if len(self.request.POST) > 0:
            return False
        if len(self.request.GET) > 0:
            if self.get_param('id') != '':
                return False
        return True

    def respond_image_bytearray(self) -> HttpResponse:
        h = FilesystemHandler.FilesystemImageBytearrayHandler(self.request)
        return run_filesystem_handler(h)

    def respond_web_encoded_image(self) -> HttpResponse:
        h = FilesystemHandler.FilesystemWebEncodedImageHandler(self.request)
        return run_filesystem_handler(h)

    def respond_document(self) -> HttpResponse:
        h = FilesystemHandler.FilesystemDocumentHandler(self.request)
        return run_filesystem_handler(h)

    def respond_directory(self) -> HttpResponse:
        h = FilesystemHandler.FilesystemDirectoryHandler(self.request)
        return run_filesystem_handler(h)

    def respond_root(self) -> HttpResponse:
        h = FilesystemHandler.FilesystemRootDirectoryHandler(self.request)
        return run_filesystem_handler(h)

    def run(self) -> HttpResponse:
        if self.is_image_bytearray_get():
            return self.respond_image_bytearray()
        if self.is_web_encoded_image_get():
            return self.respond_web_encoded_image()
        if self.is_document_get():
            return self.respond_document()
        if self.is_directory_get():
            return self.respond_directory()
        if self.is_root_get():
            return self.respond_root()
        h = BrowserHandler.BrowserHandler(self.request)
        return run_browser_handler(h)
