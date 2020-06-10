from base.transaction_handler_base import TransactionHandlerBase
import logging
_logger = logging.getLogger(__name__)

'''
Generic class for implement transaction's families. As you see, only need indicate family name, version (optional) and implement apply method
'''
class GenericFamily(TransactionHandlerBase):
    _FAMILY_NAME = 'generic-family'
    _VERSION = '1.0'

    def apply(self, transaction, context):
        _logger.info('Applying transaction family {} v: {}'.format(self.family_name, self.family_versions))
        super(GenericFamily, self).apply(transaction, context)