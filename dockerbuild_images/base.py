# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess


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
            command = [
                'docker', 'build', '-f', fname, '-t', image_name, '.'
            ]
            yield (root_absolute, fname, image_name, command)


def build(root, docker_filename, image_name, command, dry=False):
    curdir = os.getcwd()
    try:
        os.chdir(root)
        if not dry:
            subprocess.check_call(command)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        os.chdir(curdir)
