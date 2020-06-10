from odoo import fields, api, models
import logging, json
import base64

_logger = logging.getLogger(__name__)


class BlockchainReader(models.TransientModel):
    _name = 'blockchain.reader'
    _description = 'Odoo model to test result from Blockchain'
    _inherit = 'blockchain.wrapper'
    _rec_name = 'family_name'

    family_name = fields.Char(string='Family name (Smart contract)')
    payload = fields.Text(string='Payload')
    reverse = fields.Boolean(string='Reverse')
    
    
    start = fields.Integer(string='Start at')
    count = fields.Integer(string='Records to request')
    response = fields.Text(string='Response', readonly=True)
    line_ids = fields.One2many(string='Lines', comodel_name='blockchain.reader.line', inverse_name='reader_id', readonly=True)

    def write_save_log(self, ):
        self.write_bc(self.family_name, self.payload)
        
    def read_save_log(self, ):
        self.line_ids.unlink()
        line_ids, signer_keys, response = self.read_bc(self.family_name, self.start, self.count, self.reverse)
        i = 0
        for line_id in line_ids:
            self.env['blockchain.reader.line'].create({
                        'reader_id': self.id,
                        'payload': line_id,
                        'signer_key': signer_keys[i]
                    })
            i += 1
        self.response = response

class BlockchainReaderLine(models.TransientModel):
    _name = 'blockchain.reader.line'
    _description = 'Lines for resutls from Blockchain'
    _inherit = 'blockchain.wrapper'
    
    sequence = fields.Integer(string='Order')
    payload = fields.Text('Payload')
    reader_id = fields.Many2one(comodel_name='blockchain.reader')
    signer_key = fields.Text(string='Signer node key', )
    

    