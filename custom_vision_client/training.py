from functools import lru_cache
from io import FileIO
from os import environ
from os.path import basename
from os.path import splitext
from typing import Dict
from typing import Iterable
from typing import Text
from typing import Tuple

import requests

from custom_vision_client.exceptions import TrainingError
from custom_vision_client.models import AddImageResponse
from custom_vision_client.models import Project
from custom_vision_client.models import Tag
from custom_vision_client.models import TrainingResponse

HttpFile = Dict[Text, Tuple[Text, FileIO, Text]]


class TrainingConfig(object):
    def __init__(self, region=None, project_name=None, training_key=None):
        self.region = region or environ['VISION_REGION']
        self.project_name = project_name or environ['VISION_PROJECT_NAME']
        self.training_key = training_key or environ['VISION_TRAINING_KEY']


class TrainingClient(object):
    def __init__(self, config: TrainingConfig):
        self._config = config

    @lru_cache(maxsize=1)
    def _fetch_project_id(self) -> Text:
        return next(project.Id for project in self._fetch_projects()
                    if project.Name == self._config.project_name)

    def _format_api_base(self) -> Text:
        return 'https://{region}.api.cognitive.microsoft.com'.format(
            region=self._config.region)

    def _format_projects_endpoint(self) -> Text:
        return '{base}/customvision/v1.0/Training/projects'.format(
            base=self._format_api_base())

    def _format_project_endpoint(self) -> Text:
        return '{base}/{project_id}'.format(
            base=self._format_projects_endpoint(),
            project_id=self._fetch_project_id())

    def _format_tags_endpoint(self) -> Text:
        return '{base}/tags'.format(base=self._format_project_endpoint())

    def _format_tag_endpoint(self, tag_name: Text) -> Text:
        return '{base}?name={tag_name}'.format(
            base=self._format_tags_endpoint(),
            tag_name=tag_name)

    def _format_training_endpoint(self) -> Text:
        return '{base}/train'.format(base=self._format_project_endpoint())

    def _format_image_url(self, *tags: Tag) -> Text:
        return '{base}/images/image?tagIds={tagIds}'.format(
            base=self._format_project_endpoint(),
            tagIds='&tagIds='.join(tag.Id for tag in tags))

    def _format_headers(self, *kv: Tuple[Text, Text]) -> Dict[Text, Text]:
        headers = {'Training-Key': self._config.training_key}
        for key, value in kv:
            headers[key] = value
        return headers

    @classmethod
    def _format_file(cls, fobj: FileIO) -> HttpFile:
        filepath = fobj.name
        filename = basename(filepath)
        extension = splitext(filename)[1]
        return {'file': (filename, fobj, 'application/{}'.format(extension))}

    def _fetch_projects(self) -> Iterable[Project]:
        url = self._format_projects_endpoint()
        response = self._get_json(url)
        return [Project(**_) for _ in response]

    def _fetch_project_tags(self) -> Iterable[Tag]:
        url = self._format_tags_endpoint()
        response = self._get_json(url)
        return [Tag(**_) for _ in response['Tags']]

    def _fetch_tags_for_names(self, *tag_names: Text) -> Iterable[Tag]:
        all_tags = dict((tag.Name, tag) for tag in self._fetch_project_tags())
        return [all_tags[tag_name] for tag_name in tag_names]

    def _get_json(self, url: Text, **kwargs) -> Dict:
        return self._make_json_request('get', url, **kwargs)

    def _post_json(self, url: Text, **kwargs) -> Dict:
        return self._make_json_request('post', url, **kwargs)

    def _make_json_request(self, method: Text, url: Text, **kwargs) -> Dict:
        kwargs['headers'] = self._format_headers(*kwargs.pop('headers', []))
        response = getattr(requests, method)(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def create_tag(self, tag_name: Text) -> Tag:
        url = self._format_tag_endpoint(tag_name)
        response = self._post_json(url)
        return Tag(**response)

    def trigger_training(self) -> TrainingResponse:
        url = self._format_training_endpoint()
        response = self._post_json(url, headers=('Content-Length', '0'))
        try:
            return TrainingResponse(**response)
        except TypeError:
            raise TrainingError.from_response(response)

    def add_training_image(self, image_path: Text, *tag_names: Text):
        url = self._format_image_url(self._fetch_tags_for_names(*tag_names))
        with open(image_path, 'rb') as fobj:
            response = self._post_json(url, files=self._format_file(fobj))
        return AddImageResponse(**response)
