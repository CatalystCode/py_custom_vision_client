from collections import namedtuple
from typing import List
from typing import Optional
from typing import Text

from custom_vision_client.client import BaseClient
from custom_vision_client.models import Prediction

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

    def _format_prediction_endpoint(self) -> Text:
        return '{base}/customvision/v1.0/Prediction/{project_id}'.format(
            base=self._format_api_base(),
            project_id=self._project_id)

    def _format_image_prediction_endpoint(self, model_id: Optional[Text]) -> Text:
        url = '{base}/image'.format(base=self._format_prediction_endpoint())
        if model_id:
            url += '?iterationId=' + model_id
        return url

    def classify_image(self, image_path: Text, model_id: Optional[Text]=None) -> List[Prediction]:
        url = self._format_image_prediction_endpoint(model_id)
        with open(image_path, 'rb') as fobj:
            response = self._post_json(url, files=self._format_file(fobj))
        return [Prediction(**_) for _ in response['Predictions']]
