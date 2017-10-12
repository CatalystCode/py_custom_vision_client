from collections import namedtuple
from typing import Dict
from typing import Type

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
    'ProjectId',
    'TrainedWithDomainId',
    'Exportable',
])

AddImageResponse = namedtuple('AddImageResponse', [
    'IsBatchSuccessful',
    'Images',
])

Prediction = namedtuple('Prediction', [
    'TagId',
    'Tag',
    'Probability',
])


def create(namedtuple_class: Type[namedtuple], args: Dict) -> namedtuple:
    # noinspection PyProtectedMember
    fields = set(namedtuple_class._fields)

    args = {k: v for (k, v) in args.items() if k in fields}

    for field in fields:
        if field not in args:
            args[field] = None

    return namedtuple_class(**args)
