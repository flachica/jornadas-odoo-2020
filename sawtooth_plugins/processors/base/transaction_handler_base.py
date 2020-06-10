#!/usr/bin/env python3

'''
TransactionHandlerBase abstract class interfaces for Transaction Families.
'''
import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

_logger = logging.getLogger(__name__)

def _hash(data):
        '''Compute the SHA-512 hash and return the result as hex characters.'''
        return hashlib.sha512(data).hexdigest()
        
def _get_tp_address(family_name, from_key):
    '''
    Return the address of a object key.

    The address is the first 6 hex characters from the hash SHA-512(TF name),
    plus the result of the hash SHA-512.
    '''
    return _hash(family_name.encode('utf-8'))[0:6] + _hash(from_key.encode('utf-8'))[0:64]

class TransactionHandlerBase(TransactionHandler):
    '''
    Transaction Processor class for the Transaction Families.

    This TP communicates with the Validator.    
    '''
    _FAMILY_NAME = ''
    _VERSION = ''

    def __init__(self, ):
        if not self.family_name:
            raise Exception('You cannot create a family without indicating the name')
        self._VERSION = self._VERSION if self._VERSION else '1.0'
        self._namespace_prefix = _hash(self._FAMILY_NAME.encode('utf-8'))[0:6]

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return self._FAMILY_NAME

    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return [self._VERSION]

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.

           The apply function does most of the work for this class by
           processing a transaction for the transaction family indicated in __init__.

           By default only save the payload in blockchain. Overwrite this.
        '''
        payload = transaction.payload.decode()        
        from_key = transaction.header.signer_public_key

        _logger.info("Payload = %s, from_key = %s", payload, from_key)
        # event_type = "{}/{}".format(self._FAMILY_NAME, 'apply')
        # context.add_event(event_type=event_type, attributes=[("payload", payload)])
        '''Save result.'''
        tp_address = _get_tp_address(self._FAMILY_NAME, from_key)
        state_data = payload.encode('utf-8')
        addresses = context.set_state({tp_address: state_data})

        if len(addresses) < 1:
            raise InternalError("State Error")