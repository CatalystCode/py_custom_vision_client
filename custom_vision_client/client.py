from abc import abstractmethod
from io import FileIO
from os.path import basename
from os.path import splitext
from typing import Dict
from typing import Iterable
from typing import List
from typing import Text
from typing import Tuple

import requests

HttpFileInfo = Tuple[Text, FileIO, Text]
HttpFile = Tuple[Text, HttpFileInfo]
Header = Tuple[Text, Text]


class BaseClient(object):
    def __init__(self, region: Text, key: Text):
        self._region = region
        self._key = key

    def _format_api_base(self) -> Text:
        return 'https://{region}.api.cognitive.microsoft.com'.format(
            region=self._region)

    def _format_headers(self, kv: Iterable[Header]) -> Dict[Text, Text]:
        headers = {self._auth_keyname: self._key}
        for key, value in kv:
            headers[key] = value
        return headers

    @classmethod
    def _format_files(cls, *fobjs: FileIO) -> List[HttpFile]:
        files = []
        for fobj in fobjs:
            filename = basename(fobj.name)
            extension = splitext(filename)[1]
            content_type = 'application/{}'.format(extension)
            files.append(('file', (filename, fobj, content_type)))
        return files

    def _get_json(self, url: Text, **kwargs) -> Dict:
        return self._make_json_request('get', url, **kwargs)

    def _post_json(self, url: Text, **kwargs) -> Dict:
        return self._make_json_request('post', url, **kwargs)

    def _make_json_request(self, method: Text, url: Text, **kwargs) -> Dict:
        kwargs['headers'] = self._format_headers(kwargs.get('headers', []))
        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return response.json()

    @property
    @abstractmethod
    def _auth_keyname(self) -> Text:
        raise NotImplementedError
