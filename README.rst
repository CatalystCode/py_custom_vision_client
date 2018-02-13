This project is deprecated since there is now an `official Python SDK <https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/python-tutorial>`_ for the Custom Vision Service.

----

.. image:: https://travis-ci.org/CatalystCode/py_custom_vision_client.svg?branch=master
  :target: https://travis-ci.org/CatalystCode/py_custom_vision_client

.. image:: https://img.shields.io/pypi/v/custom_vision_client.svg
  :target: https://pypi.python.org/pypi/custom_vision_client/

py_custom_vision_client
=======================

This repository contains a simple Python client for the `Custom Vision Service <https://azure.microsoft.com/en-us/services/cognitive-services/custom-vision-service/>`_.

The Custom Vision Service is a tool for building custom image classification
models leveraging the power of transfer learning without the need to
administer a deep learning infrastructure. `Case study <https://www.microsoft.com/developerblog/2017/12/05/comparing-transfer-learning-systems-custom-vision-service-vs-inception-vs-mobilenet/>`_.

Setup
`````

You can install the library directly from PyPI:

.. sourcecode :: sh

  pip install custom_vision_client

Or alternatively you can get the latest version from source control:

.. sourcecode :: sh

  git clone https://github.com/CatalystCode/py_custom_vision_client.git
  cd py_custom_vision_client

Next up, you'll need to create a Custom Vision Service account and credentials.

First, log into the Custom Vision Service. If you don't already have an
account, a wizard will guide you through the signup experience. All you need
to register for the Custom Vision Service is an email address.

.. image:: https://raw.githubusercontent.com/CatalystCode/py_custom_vision_client/7f6f46b01262babee8923aaaa215dd2f44957d84/docs/signup-step-1.png
  :target: https://customvision.ai/

Next, navigate to the settings pane:

.. image:: https://raw.githubusercontent.com/CatalystCode/py_custom_vision_client/7f6f46b01262babee8923aaaa215dd2f44957d84/docs/signup-step-2.png
  :target: https://customvision.ai/projects

Now, copy the trainig key and prediction key:

.. image:: https://raw.githubusercontent.com/CatalystCode/py_custom_vision_client/7f6f46b01262babee8923aaaa215dd2f44957d84/docs/signup-step-3.png
  :target: https://customvision.ai/projects#/settings

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

Command-line interface
``````````````````````

You can also interact with the Custom Vision Service via a command-line interface:

.. sourcecode :: sh

  # first, train a model
  python3 -m custom_vision_client.training \
    --key="my-training-key" \
    --projectname="my-project-name" \
    --imagesroot="/path/to/images"

  # then, use the model to predict:
  python3 -m custom_vision_client.prediction \
    --key="my-prediction-key" \
    --projectid="my-project-id-from-training" \
    --modelid="my-model-id-from-training" \
    --image="path-or-url-to-image"

The command-line interface assumes that your training images are organized in folders
such that every folder contains all the training images for that label:

.. sourcecode :: sh

  /path/to/images
  ├── label_one
  │   ├── image_1.jpg
  │   ├── image_2.png
  │   └── image_3.png
  └── label_two
      ├── image_4.jpg
      └── image_5.jpg
