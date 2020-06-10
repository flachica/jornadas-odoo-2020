#!/usr/bin/env python3
'''
Script to vinculate all the transaction families processor to the handler
'''
from sawtooth_sdk.processor.core import TransactionProcessor
import sys
import os
from base.tools import Tools
from base.transaction_handler_base import TransactionHandlerBase
import traceback

import logging
_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG) # TODO: The logger must be configured with sawthooth tools. Validator container has the correct configuration

if __name__ == '__main__':
    _logger.info('Initializing transactions families')
    
    tools = Tools(sys.argv[1:]) # TODO: This class implements methods to load configuration variables. Must be reemplaced with sawthooth tools
    try:
        validator_url = tools.config['validator_url'] if 'validator_url' in tools.config.keys() else os.environ['HOSTNAME']
        families_directories = tools.config['addons_path']
        if isinstance(tools.config['addons_path'], str):
            families_directories = [tools.config['addons_path']]
        for path in families_directories:
            _logger.info('Searching families in {}. Linking with validator_url {}'.format(path, validator_url))
            SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
            plugins_directory_path = os.path.join(SCRIPT_DIR, path)
            families = tools.import_plugins(plugins_directory_path, path.replace(os.path.sep, '.'), TransactionHandlerBase)
            processor = TransactionProcessor(url=validator_url) # TODO: Sawthooth have configuration files, utilize it
            for family in families:
                _logger.info('Loading Transaction procesor for family {}'.format(family.family_name))
                processor.add_handler(family)
            processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)