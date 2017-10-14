# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="dockerbuild-images",
    version='0.0.1',
    description='Recursively builds Dockerfiles',
    author='Jakub Janoszek',
    author_email='kuba.janoszek@gmail.com',
    url='https://github.com/jqb/dockerbuild-images',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        dockerbuild-images=dockerbuild_images.cli:main
    ''',
    include_package_data=True,
    zip_safe=False,
)
