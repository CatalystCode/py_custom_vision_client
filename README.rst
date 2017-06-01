.. image:: https://travis-ci.org/CatalystCode/py_custom_vision_client.svg?branch=master
  :target: https://travis-ci.org/CatalystCode/py_custom_vision_client

py_custom_vision_client
=======================

This repository contains a simple Python client for the `Custom Vision Service <https://azure.microsoft.com/en-us/services/cognitive-services/custom-vision-service/>`_.

Usage
`````

.. sourcecode :: py

  # first, train a model

  from custom_vision_client import TrainingClient, TrainingConfig

  training_client = TrainingClient(TrainingConfig("my-azure-region", "my-project-name", "my-training-key"))

  training_client.create_tag("Cat")
  training_client.create_tag("Dog")

  training_client.add_training_image("kitten.jpg", "Cat")
  training_client.add_training_image("akita.png", "Dog")
  training_client.add_training_image("best-animal-pals.jpg", "Cat", "Dog")

  model_id = training_client.trigger_training().Id

  project_id = training_client.fetch_project_id()

  # then, use the model to predict:

  from custom_vision_client import PredictionClient, PredictionConfig

  prediction_client = PredictionClient(PredictionConfig("my-azure-region", project_id, "my-prediction-key"))

  predictions = prediction_client.classify_image("cat.jpg", model_id)
  best_prediction = max(predictions, key=lambda _: _.Probability)
  print(best_prediction.Tag)
