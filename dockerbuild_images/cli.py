# -*- coding: utf-8 -*-
import os
import click

from .base import find_docker_files, build


@click.command()
@click.option('--no-verbose', is_flag=True)
@click.option('--dry', is_flag=True, help='Show only what script will do')
@click.option('--sleep', default=2, help='Wait of some seconds before building found Dockerfile')
@click.argument('directory')
def main(directory, no_verbose, dry, sleep):
    directory_absolute = os.path.abspath(
        os.path.join(os.getcwd(), directory)
    )
    if not os.path.exists(directory_absolute):
        raise click.UsageError('Provided directory "%s" needs to exists' % directory_absolute)

    for root, docker_filename, image_name in find_docker_files(directory_absolute):
        build(root, docker_filename, image_name, dry=dry, verbose=(not no_verbose), sleep=sleep)
