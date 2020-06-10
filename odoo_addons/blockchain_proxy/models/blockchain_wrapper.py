'''
BlockChainWrapper class interfaces with Sawtooth through the REST API.
'''
import hashlib
import base64
import random
import time
import requests
import yaml
from requests.exceptions import ReadTimeout

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from odoo import fields, models, _
from odoo.models import AbstractModel
from odoo.tools import config
from odoo.exceptions import UserError
import logging
import os
import json

_logger = logging.getLogger(__name__)


def _hash(data):
    return hashlib.sha512(data).hexdigest()


class BlockChainWrapper(AbstractModel):
    _family_name = ''
    _base_url = ''
    _signer = ''
    _address = ''
    _public_key = ''

    _name = 'blockchain.wrapper'
    _description = 'Wrapper for Odoo models to can transact request with Blockchain'

    def hash(self, data):
        return _hash(str(data).encode('utf-8'))

    def _send_to_rest_api(self, suffix, data=None, content_type=None, timeout=10):
        '''Send a REST command to the Validator via the REST API.'''
        url = "{}/{}".format(self._base_url, suffix)
        _logger.info("Sending to REST API URL {}".format(url))

        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data, timeout=timeout)
            else:
                result = requests.get(url, headers=headers, timeout=timeout)

            if not result.ok:
                raise UserError(_("Error {}: {}".format(result.status_code, result.reason)))
        except requests.ConnectionError as err:
            raise UserError(_('Check connectivity with the Blockchain network. Failed to connect to {}\n Error: \n {}'.format(url, str(err))))
        except ReadTimeout as err:
            raise UserError(_('Timeout error with the Blockchain network. Failed to recieve data from {}\n Error: \n {}'.format(url, str(err))))
        except BaseException as err:
            raise Exception(err)

        return result.text

    def _check_init(self):
        if not self._family_name:
            raise UserError(_('The wrapper is not initialized. Please, call init_bc method before'))

    def _wait_for_status(self, batch_id, wait, result):
        '''Wait until transaction status is not PENDING (COMMITTED or error).

           'wait' is time to wait for status, in seconds.

           Called after sending data through REST API. 
           If the answer is not satisfactory the problem must be in new TP or in the Sawttoth core
        '''
        if wait and wait > 0:
            waited = 0
            start_time = time.time()
            while waited < wait:
                result = self._send_to_rest_api("batch_statuses?id={}&wait={}"
                                                .format(batch_id, wait))
                status = yaml.safe_load(result)['data'][0]['status']
                waited = time.time() - start_time

                if status != 'PENDING':
                    return result
            raise UserError(_('Transaction timed out after waiting {} seconds. Review de transaction processor log'.format(wait)))
        else:
            _logger.info('Status returned {}'.format(result))
            return result

    def init_bc(self, family_name=None):
        if self._family_name:
            return
        self._family_name = family_name
        self._base_url = config.get('blockchain_client_url') or os.environ.get('BLOCKCHAIN_CLIENT_URL', 'http://localhost:8008')
        if not self._signer:
            key_file = config.get('sawtooth_key') or os.environ.get('SAWTOOTH_KEY', 'sawtooth-key.priv')
            if key_file is None:
                self._signer = None
                return
        try:
            with open(key_file) as key_fd:
                private_key_str = key_fd.read().strip()
        except OSError as err:
            raise UserError(_('Failed to read private key {}: {}'.format(key_file, str(err))))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as err:
            raise UserError(_('Failed to load private key: {}'.format(str(err))))

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)
        self._public_key = self._signer.get_public_key().as_hex()

        self._address = _hash(self._family_name.encode('utf-8'))[0:6] + \
                        _hash(self._public_key.encode('utf-8'))[0:64]
                        
    def write_bc(self, family_name, args, wait=10):
        '''Create a transaction, then wrap it in a batch.

           Even single transactions must be wrapped into a batch.
        '''
        self.init_bc(family_name=family_name)
        _logger.info('Wrapping and sending to blockchain with TP {} and Public Key {}'.format(self._family_name, self._public_key))
        payload = str(json.dumps(args))

        payload = payload.encode()  # Convert Unicode to bytes

        # Construct the address where we'll store our state.
        # We just have one input and output address (the same one).
        input_and_output_address_list = [self._address]

        # Create a TransactionHeader.
        header = TransactionHeader(
            signer_public_key=self._public_key,
            family_name=self._family_name,
            family_version="1.0",
            inputs=input_and_output_address_list,
            outputs=input_and_output_address_list,
            dependencies=[],
            payload_sha512=_hash(payload),
            batcher_public_key=self._public_key,
            nonce=random.random().hex().encode()
        ).SerializeToString()

        # Create a Transaction from the header and payload above.
        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        transaction_list = [transaction]

        # Create a BatchHeader from transaction_list above.
        header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in transaction_list]
        ).SerializeToString()

        # Create Batch using the BatchHeader and transaction_list above.
        batch = Batch(
            header=header,
            transactions=transaction_list,
            header_signature=self._signer.sign(header))

        # Create a Batch List from Batch above
        batch_list = BatchList(batches=[batch])
        batch_id = batch_list.batches[0].header_signature

        _logger.info('Transaction builded')
        # Send batch_list to the REST API
        result = self._send_to_rest_api(suffix="batches",
                                        data=batch_list.SerializeToString(),
                                        content_type='application/octet-stream', 
                                        timeout=wait)
        _logger.info('Request sended')
        # Wait until transaction status is COMMITTED, error, or timed out
        return self._wait_for_status(batch_id, wait, result)

    def read_bc(self, family_name, start, count, reverse=True):
        self.init_bc(family_name)
        pagination = '?'
        if reverse:
            pagination += 'reverse&'
        if count:
            pagination += "start=0x{}&limit={}".format(start, count)
        response = self._send_to_rest_api("blocks{}".format(pagination))
        line_ids = []
        signer_keys = []
        for batch in json.loads(response)['data']:
            if (batch['batches'][0]['transactions'][0]['header']['family_name'] == family_name):
                signer_keys.append(batch['batches'][0]['header']['signer_public_key'])
                line_ids.append(json.loads(base64.b64decode(batch['batches'][0]['transactions'][0]['payload'])))
        return line_ids, signer_keys, response