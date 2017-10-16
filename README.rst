.. image:: https://travis-ci.org/CatalystCode/py_custom_vision_client.svg?branch=master
  :target: https://travis-ci.org/CatalystCode/py_custom_vision_client

.. image:: https://img.shields.io/pypi/v/custom_vision_client.svg
  :target: https://pypi.python.org/pypi/custom_vision_client/

py_custom_vision_client
=======================

This repository contains a simple Python client for the `Custom Vision Service <https://azure.microsoft.com/en-us/services/cognitive-services/custom-vision-service/>`_.

Usage
`````

.. sourcecode :: py

  # first, train a model

  from custom_vision_client import TrainingClient, TrainingConfig

  azure_region = "southcentralus"
  training_key = "my-training-key"  # from settings pane on customvision.ai

  training_client = TrainingClient(TrainingConfig(azure_region, training_key))
  project_id = training_client.create_project("my-project-name").Id

  training_client.create_tag(project_id, "Cat")
  training_client.create_tag(project_id, "Dog")

  training_client.add_training_images(project_id, ["kitten.jpg"], "Cat")
  training_client.add_training_images(project_id, ["akita.png", "spitz.png"], "Dog")
  training_client.add_training_images(project_id, ["best-animal-pals.jpg"], "Cat", "Dog")

  model_id = training_client.trigger_training(project_id).Id

  # then, use the model to predict:

  from custom_vision_client import PredictionClient, PredictionConfig

  azure_region = "southcentralus"
  prediction_key = "my-prediction-key"  # from settings pane on customvision.ai

  prediction_client = PredictionClient(PredictionConfig(azure_region, project_id, prediction_key))

  predictions = prediction_client.classify_image("cat.jpg", model_id)  # could also be a url to a file
  best_prediction = max(predictions, key=lambda _: _.Probability)
  print(best_prediction.Tag)
