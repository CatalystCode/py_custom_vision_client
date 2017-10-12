from collections import namedtuple

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
