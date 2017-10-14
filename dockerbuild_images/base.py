# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
import subprocess

import click


DOCKERFILE_NAME = 'Dockerfile'


def find_docker_files(path, dockerfile_name=DOCKERFILE_NAME):
    for root, dirs, files in os.walk(path):
        if '.git' in root:
            continue

        for fname in files:
            fname = fname.decode('utf-8')
            if dockerfile_name not in fname:
                continue

            parts = filter(bool, [
                p.strip('_') for p in fname.split(dockerfile_name, 1)
            ])
            parts = parts or [os.path.basename(root)]
            image_name = parts[0]
            root_absolute = os.path.join(os.getcwd(), root)
            root_absolute = os.path.abspath(root_absolute)
            yield (root_absolute, fname, image_name)


def build(root, docker_filename, image_name, dry=False, verbose=True, sleep=2):
    curdir = os.getcwd()
    log = click.echo
    try:
        command = [
            'docker', 'build', '-f', docker_filename, '-t', image_name, '.'
        ]
        if verbose:
            log(u'*' * 80)
            log(u'   Directory        :: %s' % root)
            log(u'   Docker file name :: %s' % docker_filename)
            log(u'   Image name       :: %s' % image_name)
            log(u'   Command          :: %s' % ' '.join(command))
            log(u'*' * 80)
            log(u'')
        if sleep:
            time.sleep(sleep)
        os.chdir(root)
        if not dry:
            subprocess.call(command)
    finally:
        os.chdir(curdir)
