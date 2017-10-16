from collections import namedtuple
from functools import lru_cache
from typing import Text
from typing import Iterable

from custom_vision_client.client import BaseClient
from custom_vision_client.exceptions import TrainingError
from custom_vision_client.models import AddImageResponse
from custom_vision_client.models import Project
from custom_vision_client.models import Tag
from custom_vision_client.models import TrainingResponse
from custom_vision_client.models import create

TrainingConfig = namedtuple('TrainingConfig', [
    'region',
    'project_name',
    'training_key',
])


class TrainingClient(BaseClient):
    _auth_keyname = 'Training-Key'

    def __init__(self, config: TrainingConfig):
        super().__init__(config.region, config.training_key)
        self._project_name = config.project_name

    @lru_cache(maxsize=1)
    def fetch_project_id(self) -> Text:
        return next(project.Id for project in self._fetch_projects()
                    if project.Name == self._project_name)

    def _format_projects_endpoint(self) -> Text:
        return '{base}/customvision/v1.0/Training/projects'.format(
            base=self._format_api_base())

    def _format_new_project_endpoint(self, project_name: Text) -> Text:
        query = (('name', project_name),
                 ('description', ''),
                 ('classifier', 'MultiLabel'),
                 ('useNegativeSet', 'true'))

        return '{base}?{query}'.format(
            base=self._format_projects_endpoint(),
            query='&'.join('{}={}'.format(*kv) for kv in query))

    def _format_project_endpoint(self) -> Text:
        return '{base}/{project_id}'.format(
            base=self._format_projects_endpoint(),
            project_id=self.fetch_project_id())

    def _format_tags_endpoint(self) -> Text:
        return '{base}/tags'.format(base=self._format_project_endpoint())

    def _format_tag_endpoint(self, tag_name: Text) -> Text:
        return '{base}?name={tag_name}'.format(
            base=self._format_tags_endpoint(),
            tag_name=tag_name)

    def _format_training_endpoint(self) -> Text:
        return '{base}/train'.format(base=self._format_project_endpoint())

    def _format_image_url(self, tags: Iterable[Tag]) -> Text:
        return '{base}/images/image?tagIds={tagIds}'.format(
            base=self._format_project_endpoint(),
            tagIds='&tagIds='.join(tag.Id for tag in tags))

    def _fetch_projects(self) -> Iterable[Project]:
        url = self._format_projects_endpoint()
        response = self._get_json(url)
        return [create(Project, _) for _ in response]

    def _fetch_project_tags(self) -> Iterable[Tag]:
        url = self._format_tags_endpoint()
        response = self._get_json(url)
        return [create(Tag, _) for _ in response['Tags']]

    def _fetch_tags_for_names(self, names: Iterable[Text]) -> Iterable[Tag]:
        all_tags = dict((tag.Name, tag) for tag in self._fetch_project_tags())
        return [all_tags[name] for name in names]

    def create_project(self, project_name: Text) -> Project:
        url = self._format_new_project_endpoint(project_name)
        response = self._post_json(url, headers=[('Content-Length', '0')])
        return create(Project, response)

    def create_tag(self, tag_name: Text) -> Tag:
        url = self._format_tag_endpoint(tag_name)
        response = self._post_json(url)
        return create(Tag, response)

    def trigger_training(self) -> TrainingResponse:
        url = self._format_training_endpoint()
        response = self._post_json(url, headers=[('Content-Length', '0')])
        if TrainingError.has_error(response):
            raise TrainingError.from_response(response)
        return create(TrainingResponse, response)

    def add_training_image(self, image_path: Text, *tag_names: Text):
        url = self._format_image_url(self._fetch_tags_for_names(tag_names))
        with open(image_path, 'rb') as fobj:
            response = self._post_json(url, files=self._format_file(fobj))
        return create(AddImageResponse, response)
