from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as fobj:
    install_requires = [line.strip() for line in fobj]

with open('README.rst') as fobj:
    long_description = fobj.read()

packages = find_packages(exclude=['tests*'])

setup(
    name='custom_vision_client',
    version='0.0.2',
    author='Clemens Wolff',
    author_email='clewolff@microsoft.com',
    packages=packages,
    url='https://github.com/CatalystCode/py_custom_vision_client',
    license='License :: OSI Approved :: MIT License',
    description='A client for the Microsoft Azure Custom Vision Service',
    long_description=long_description,
    include_package_data=True,
    install_requires=install_requires)
