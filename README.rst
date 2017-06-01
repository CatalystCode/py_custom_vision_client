.. image:: https://travis-ci.org/CatalystCode/py_custom_vision_client.svg?branch=master
  :target: https://travis-ci.org/CatalystCode/py_custom_vision_client

py_custom_vision_client
=======================

This repository contains a simple Python client for the `Custom Vision Service <https://azure.microsoft.com/en-us/services/cognitive-services/custom-vision-service/>`_.

Usage
`````

.. sourcecode :: py

  from custom_vision_client import TrainingClient, Config

  config = Config("my-azure-region", "my-project-name", "my-training-key")
  client = TrainingClient(config)

  client.create_tag("Cat")
  client.create_tag("Dog")

  client.add_training_image("kitten.jpg", "Cat")
  client.add_training_image("akita.png", "Dog")
  client.add_training_image("best-animal-pals.jpg", "Cat", "Dog")

  client.trigger_training()
