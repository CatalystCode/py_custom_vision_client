class TrainingError(Exception):
    def __init__(self, status, message):
        self.message = message
        self.status = status

    def __str__(self):
        return ' '.join(_ for _ in (self.status, self.message) if _)
