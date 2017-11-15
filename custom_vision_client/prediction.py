from collections import namedtuple
from os.path import isfile
from typing import Dict
from typing import List
from typing import Optional
from typing import Text

from custom_vision_client.client import BaseClient
from custom_vision_client.models import Prediction
from custom_vision_client.models import create

PredictionConfig = namedtuple('PredictionConfig', [
    'region',
    'project_id',
    'prediction_key',
])


class PredictionClient(BaseClient):
    _auth_keyname = 'Prediction-Key'

    def __init__(self, config: PredictionConfig):
        super().__init__(config.region, config.prediction_key)
        self._project_id = config.project_id

    def _format_prediction_endpoint(self, api: Text, model_id: Text) -> Text:
        url = ('{base}/customvision/v1.0/Prediction'
               '/{project_id}/{api}'
               .format(base=self._format_api_base(),
                       api=api,
                       project_id=self._project_id))
        if model_id:
            url += '?iterationId=' + model_id
        return url

    def _classify_remote_image(self, image_path: Text, model_id: Text) -> Dict:
        url = self._format_prediction_endpoint('url', model_id)
        return self._post_json(url, json={'Url': image_path})

    def _classify_local_image(self, image_path: Text, model_id: Text) -> Dict:
        url = self._format_prediction_endpoint('image', model_id)
        with open(image_path, 'rb') as fobj:
            response = self._post_json(url, files=self._format_files(fobj))
        return response

    def classify_image(self, image: Text,
                       model_id: Optional[Text]=None) -> List[Prediction]:

        if isfile(image):
            response = self._classify_local_image(image, model_id)
        else:
            response = self._classify_remote_image(image, model_id)
        return [create(Prediction, _) for _ in response['Predictions']]


def _cli():
    from argparse import ArgumentParser
    from json import dumps

    parser = ArgumentParser()
    parser.add_argument('--region', default='southcentralus')
    parser.add_argument('--key', required=True)
    parser.add_argument('--modelid')
    parser.add_argument('--projectid', required=True)
    parser.add_argument('--image', required=True)
    args = parser.parse_args()

    client = PredictionClient(PredictionConfig(
        region=args.region,
        project_id=args.projectid,
        prediction_key=args.key))

    predictions = client.classify_image(args.image, args.modelid)
    best = max(predictions, key=lambda _: _.Probability)
    print(dumps({'confidence': best.Probability, 'label': best.Tag}))


if __name__ == '__main__':
    _cli()
