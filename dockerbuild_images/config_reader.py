import os
import yaml
from . import pyimporter


class ValidationError(Exception):
    pass


NIL = object()


def normalize_images_recursive_entry(images_recursive, curdir=None):
    curdir = curdir or os.getcwd()
    result = []
    for item in images_recursive:
        path = item.get('path')
        if path:
            result.append({
                'path': os.path.abspath(os.path.join(curdir, path))
            })
            continue

        exclude = item.get('exclude')
        if exclude:
            result.append({
                'exclude': os.path.abspath(os.path.join(curdir, exclude))
            })
            continue

        module = item.get('module')
        if module:
            module = pyimporter.import_(module)
            result.append({
                'path': os.path.dirname(module.__file__)
            })
            continue

        raise ValidationError((
            'Wrong definition in "images_recursive" section: %s | '
            '"path", "exclude" or "module" key required'
        ) % (item, ))

    return result


def normalize_images_entry(images, curdir=None):
    curdir = curdir or os.getcwd()
    result = {}
    for image_name, path in images.items():
        result[image_name] = os.path.abspath(os.path.join(curdir, path))
    return result


def normalize_build_args_envfile(envfile_entry, curdir=None):
    curdir = curdir or os.getcwd()
    return os.path.abspath(os.path.join(curdir, envfile_entry))


def normalize(config):
    if 'images' in config:
        config['images'] = normalize_images_entry(config['images'])
    if 'images_recursive' in config:
        config['images_recursive'] = normalize_images_recursive_entry(config['images_recursive'])
    return config


def construct_build_args(build_args_file):
    with open(build_args_file, 'r') as fd:
        lines = list(fd.readlines())

    build_args = []
    for line in lines:
        if line.startswith('#'):
            continue
        build_args.append(line.strip())
    return build_args


class ConfigurationAdapter(object):
    '''Filters out paths to Dockerfiles and adapts image_name is needed'''

    def __init__(self, images=None, images_recursive=None, build_args=None):
        self.images = images or {}
        self.images_recursive = images_recursive or []
        self._build_args = []
        self._build_args_from_configfile = build_args or []

    def get_build_args_file_path_from_environ(self, default=NIL):
        envfile = os.environ.get('DOCKERBUILD_BUILD_ARGS_FILE') or NIL
        return normalize_build_args_envfile(envfile) if envfile is not NIL else default

    @property
    def build_args(self):
        if self._build_args:
            return self._build_args

        build_args_file = self.get_build_args_file_path_from_environ()
        if build_args_file is NIL:
            self._build_args = self._build_args_from_configfile
        else:
            self._build_args = construct_build_args(build_args_file)
        return self._build_args

    def adapt(self, dockerfile_directory, dockerfile_name, image_name):
        dockerfile_absolute = os.path.abspath(
            os.path.join(dockerfile_directory, dockerfile_name)
        )

        if self.images:
            for iname, absolute_path in self.images.items():
                # image name from configuration file should take precedense
                if absolute_path == dockerfile_absolute:
                    # we are exchanging "image_name" with "iname"
                    return dockerfile_directory, dockerfile_name, iname

        if not self.images_recursive:
            return dockerfile_directory, dockerfile_name, image_name

        for item in self.images_recursive:
            exclude = item.get('exclude')
            if not exclude:
                continue
            exclude = '%s/' % exclude if not exclude.endswith('/') else exclude
            dockerfile_directory_cmp = (
                '%s/' % dockerfile_directory if not dockerfile_directory.endswith('/')
                else dockerfile_directory)
            if dockerfile_directory_cmp.startswith(exclude):
                return None
            # There's probably no point in checking "path"
        return dockerfile_directory, dockerfile_name, image_name


def validate(config):
    one_of = ['images', 'images_recursive']

    if not config:
        raise ValidationError('It looks like config file is empty.')

    if not any([(key in config) for key in one_of]):
        raise ValidationError('At least one of sections needs to be defined: %s' % (one_of))

    return config


def read(config_filepath):
    with open(config_filepath, 'r') as fd:
        config = yaml.load(fd.read(), Loader=yaml.Loader)
    config = validate(config)
    config = normalize(config)
    return ConfigurationAdapter(**config)
