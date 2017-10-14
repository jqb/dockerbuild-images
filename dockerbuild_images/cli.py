# -*- coding: utf-8 -*-
import os
import datetime

import click

from .base import find_docker_files, build


def log(*args, **kwargs):
    return click.secho(*args, **kwargs)


def log_green(*args, **kwargs):
    kwargs.update(fg='green', bold=True)
    return click.secho(*args, **kwargs)


def err(*args, **kwargs):
    kwargs.update(fg='red', bold=True)
    return click.secho(*args, **kwargs)


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

    results = []
    for root, docker_filename, image_name, command in find_docker_files(directory_absolute):
        if not no_verbose:
            log(u'*' * 80)
            log(u'   Directory        :: %s' % root)
            log(u'   Docker file name :: %s' % docker_filename)
            log(u'   Image name       :: %s' % image_name)
            log(u'   Command          :: %s' % ' '.join(command))
            log(u'*' * 80)
            log(u'')

        start = datetime.datetime.now()
        was_ok = build(root, docker_filename, image_name, command, dry=dry, sleep=sleep)
        took = datetime.datetime.now() - start

        log('')  # let's do one extra new-line after

        results.append(
            (root, docker_filename, image_name, command, was_ok, took)
        )
        if not was_ok:
            err('')
            err('    %s' % ('*' * 80))
            err('    SOMETHING WENT WRONG WITH BUILD !!! ')
            err('    %s' % ('*' * 80))
            err('')

    log('\n')
    log('=' * 80)
    for root, docker_filename, image_name, command, was_ok, took in results:
        log(' - %s' % (os.path.abspath(os.path.join(root, docker_filename))))
        if was_ok:
            log_green('    OK | took: %s' % (took))
        else:
            err('    ERROR | You might want to go to the directory and check things out')
            err('          | $> cd %s' % root)
            err('          | $> %s' % ' '.join(command))
