import logging
import io
import os
import inspect
import importlib
import glob

_logger = logging.getLogger(__name__)

import hashlib

class Tools():
    config = {}

    def __init__(self, args):
        self._load_config(args)

    def import_plugins(self, search_dir, package, base_class):
        _logger.info('Enabling processors. Search_dir {} package {} base_class {}'.format(search_dir, package, base_class))
        plugin_file_paths = glob.glob(os.path.join(search_dir, "*.py"))
        for plugin_file_path in plugin_file_paths:
            plugin_file_name = os.path.basename(plugin_file_path)

            module_name = os.path.splitext(plugin_file_name)[0]

            if module_name.startswith("__"):
                continue

            module = importlib.import_module(package + "." + module_name)

            for item in dir(module):
                value = getattr(module, item)
                if not value:
                    continue

                if not inspect.isclass(value):
                    continue

                if inspect.isabstract(value):
                    continue

                if base_class is not None:
                    if value._FAMILY_NAME == base_class._FAMILY_NAME:
                        continue

                yield value()

    def _load_config(self, args):
        _logger.debug('Args received {}'.format(args))
        for arg in args:
            parsed = arg.split("=")
            key = parsed[0].replace('--', '').strip()
            prevalue = parsed[1]
            values_arr = prevalue.strip().split(',')
            value = values_arr
            if len(values_arr) == 1:
                value = prevalue
            self.config[key] = value
        _logger.info('Config {}'.format(self.config))
        if 'addons_path' not in self.config.keys():
            raise Exception('addons_path not established')

        if 'validator_url' not in self.config.keys():
            raise Exception('validator_url not established')