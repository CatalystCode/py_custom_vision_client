from typing import Dict
from typing import Text


class TrainingError(Exception):
    def __init__(self, status: Text, message: Text):
        self.status = status
        self.message = message

    def __str__(self):
        return ' '.join(_ for _ in (self.status, self.message) if _)

    @classmethod
    def has_error(cls, response: Dict):
        return 'statusCode' in response or 'Code' in response

    @classmethod
    def from_response(cls, response: Dict):
        status = response.get('statusCode') or response.get('Code')
        message = response.get('message') or response.get('Message')
        return TrainingError(status=status, message=message)
