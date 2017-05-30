from collections import namedtuple
from functools import lru_cache
from os import environ
from os.path import basename
from os.path import splitext

import requests

from exceptions import TrainingError


Tag = namedtuple('Tag', [
    'Description',
    'Id',
    'ImageCount',
    'Name',
])
Project = namedtuple('Project', [
    'Created',
    'CurrentIterationId',
    'Description',
    'Id',
    'LastModified',
    'Name',
    'Settings',
    'ThumbnailUri',
])
TrainingResponse = namedtuple('TrainingResponse', [
    'Id',
    'Name',
    'Status',
    'Created',
    'LastModified',
    'IsDefault',
])
AddImageResponse = namedtuple('AddImageResponse', [
    'IsBatchSuccessful',
    'Images',
])


class VisionServiceConfig(object):
    def __init__(self, region=None, training_key=None, project_name=None):
        self.region = region or environ['VISION_SERVICE_REGION']
        self.training_key = training_key or environ['VISION_SERVICE_TRAINING_KEY']
        self._project_name = project_name or environ['VISION_SERVICE_PROJECT_NAME']

    @lru_cache(maxsize=1)
    def _fetch_project(self):
        return [project for project in _fetch_projects(self)
                if project.Name == self._project_name][0]

    @property
    def project_id(self):
        return self._fetch_project().Id


def _fetch_projects(config):
    headers = {'Training-Key': config.training_key}
    url = ('https://{region}.api.cognitive.microsoft.com/customvision/v1.0'
           '/Training/projects'
           .format(region=config.region))
    json_response = requests.get(url, headers=headers).json()
    return [Project(**_) for _ in json_response]


def _fetch_project_tags(config):
    headers = {'Training-Key': config.training_key}
    url = ('https://{region}.api.cognitive.microsoft.com/customvision/v1.0'
           '/Training/projects/{project_id}/tags'
           .format(region=config.region,
                   project_id=config.project_id))
    json_response = requests.get(url, headers=headers).json()['Tags']
    return [Tag(**_) for _ in json_response]


def trigger_training(config):
    headers = {'Training-Key': config.training_key, 'Content-Length': '0'}
    url = ('https://{region}.api.cognitive.microsoft.com/customvision/v1.0'
           '/Training/projects/{project_id}/train'
           .format(region=config.region,
                   project_id=config.project_id))
    json_response = requests.post(url, headers=headers).json()
    try:
        return TrainingResponse(**json_response)
    except TypeError:
        status = json_response.get('statusCode') or json_response.get('Code')
        message = json_response.get('message') or json_response.get('Message')
        raise TrainingError(status=status, message=message)


def add_training_image(config, image_path, *tag_names):
    all_tags = dict((tag.Name, tag) for tag in _fetch_project_tags(config))
    tags = [all_tags[tag_name] for tag_name in tag_names]
    headers = {'Training-Key': config.training_key}
    url = ('https://{region}.api.cognitive.microsoft.com/customvision/v1.0'
           '/Training/projects/{project_id}/images/image?tagIds={tagIds}'
           .format(region=config.region,
                   project_id=config.project_id,
                   tagIds='&tagIds='.join(tag.Id for tag in tags)))
    with open(image_path, 'rb') as fobj:
        filename = basename(image_path)
        extension = splitext(filename)[1]
        files = {'file': (filename, fobj, 'application/{}'.format(extension))}
        json_response = requests.post(url, headers=headers, files=files).json()
    return AddImageResponse(**json_response)
