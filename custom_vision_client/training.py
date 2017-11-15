from collections import namedtuple
from typing import Iterable
from typing import Optional
from typing import Text
from typing import TypeVar

from requests.exceptions import HTTPError

from custom_vision_client.client import BaseClient
from custom_vision_client.exceptions import TrainingError
from custom_vision_client.models import AddImageResponse
from custom_vision_client.models import Project
from custom_vision_client.models import Tag
from custom_vision_client.models import TrainingResponse
from custom_vision_client.models import create

T = TypeVar('T')

TrainingConfig = namedtuple('TrainingConfig', [
    'region',
    'training_key',
])


def _grouper(iterable: Iterable[T], group_size: int) -> Iterable[Iterable[T]]:
    iterator = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(group_size):
                chunk.append(next(iterator))
            yield chunk
        except StopIteration:
            if chunk:
                yield chunk
            break


class TrainingClient(BaseClient):
    _auth_keyname = 'Training-Key'
    _training_batch_size = 50

    def __init__(self, config: TrainingConfig):
        super().__init__(config.region, config.training_key)

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

    def _format_project_endpoint(self, project_id: Text) -> Text:
        return '{base}/{project_id}'.format(
            base=self._format_projects_endpoint(),
            project_id=project_id)

    def _format_tags_endpoint(self, project_id: Text) -> Text:
        return '{base}/tags'.format(
            base=self._format_project_endpoint(project_id))

    def _format_tag_endpoint(self, project_id: Text, tag_name: Text) -> Text:
        return '{base}?name={tag_name}'.format(
            base=self._format_tags_endpoint(project_id),
            tag_name=tag_name)

    def _format_training_endpoint(self, project_id: Text) -> Text:
        return '{base}/train'.format(
            base=self._format_project_endpoint(project_id))

    def _format_image_url(self, project_id: Text, tags: Iterable[Tag]) -> Text:
        return '{base}/images/image?tagIds={tagIds}'.format(
            base=self._format_project_endpoint(project_id),
            tagIds='&tagIds='.join(tag.Id for tag in tags))

    def _fetch_projects(self) -> Iterable[Project]:
        url = self._format_projects_endpoint()
        response = self._get_json(url)
        return [create(Project, _) for _ in response]

    def _fetch_project_tags(self, project_id: Text) -> Iterable[Tag]:
        url = self._format_tags_endpoint(project_id)
        response = self._get_json(url)
        return [create(Tag, _) for _ in response['Tags']]

    def _fetch_tags_for_names(self, project_id: Text,
                              names: Iterable[Text]) -> Iterable[Tag]:

        all_tags = {tag.Name: tag
                    for tag in self._fetch_project_tags(project_id)}

        return [all_tags[name] for name in names]

    def create_project(self, project_name: Text) -> Project:
        url = self._format_new_project_endpoint(project_name)
        response = self._post_json(url, headers=[('Content-Length', '0')])
        return create(Project, response)

    def create_tag(self, project_id: Text, tag_name: Text) -> Optional[Tag]:
        url = self._format_tag_endpoint(project_id, tag_name)
        try:
            response = self._post_json(url)
        except HTTPError:
            # tag already exists
            return None
        else:
            return create(Tag, response)

    def trigger_training(self, project_id: Text) -> TrainingResponse:
        url = self._format_training_endpoint(project_id)
        try:
            response = self._post_json(url, headers=[('Content-Length', '0')])
        except HTTPError:
            raise TrainingError(
                'Unable to train.',
                'Check that you have at least two tags in your project and '
                'have associated at least 10 images to every tag')
        if TrainingError.has_error(response):
            raise TrainingError.from_response(response)
        return create(TrainingResponse, response)

    def _add_training_images(self, project_id: Text, tags: Iterable[Tag],
                             image_paths: Iterable[Text]) -> dict:

        url = self._format_image_url(project_id, tags)
        fobjs = [open(image_path, 'rb') for image_path in image_paths]
        try:
            return self._post_json(url, files=self._format_files(*fobjs))
        finally:
            for fobj in fobjs:
                fobj.close()

    def add_training_images(self, project_id: Text,
                            image_paths: Iterable[Text], *tag_names: Text):

        is_batch_successful = True
        images = []

        tags = self._fetch_tags_for_names(project_id, tag_names)
        for batch in _grouper(image_paths, self._training_batch_size):
            response = self._add_training_images(project_id, tags, batch)

            is_batch_successful |= response.get('IsBatchSuccessful', False)
            images.extend(response.get('Images', []))

        return AddImageResponse(IsBatchSuccessful=is_batch_successful,
                                Images=images)


def _cli():
    from argparse import ArgumentParser
    from glob import glob
    from json import dumps
    from os import listdir

    parser = ArgumentParser()
    parser.add_argument('--region', default='southcentralus')
    parser.add_argument('--key', required=True)
    parser.add_argument('--projectname', required=True)
    parser.add_argument('--imagesroot', required=True)
    parser.add_argument('--imagetypes', default='jpg,png')
    args = parser.parse_args()

    client = TrainingClient(TrainingConfig(
        region=args.region,
        training_key=args.key))

    project_id = client.create_project(args.projectname).Id
    for label in listdir(args.imagesroot):
        images = []
        for extension in args.imagetypes.split(','):
            images.extend(glob(
                '{}/{}/**/*.{}'.format(args.imagesroot, label, extension),
                recursive=True))

        client.create_tag(project_id, label)
        client.add_training_images(project_id, images, label)

    model_id = client.trigger_training(project_id).Id
    print(dumps({'model_id': model_id, 'project_id': project_id}))


if __name__ == '__main__':
    _cli()
