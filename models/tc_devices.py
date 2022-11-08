
import datetime, time
import requests, json
import random
import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz

class tc_devices(models.Model):
    _name = "tc_devices"
    _description = 'traccar devices'
    _order = "name DESC"
        
    name                                        = fields.Char('Name', size=128)
    uniqueid                                    = fields.Char('IMEI', size=128, required=True)
    icc                                         = fields.Char('ICC', size=30)
    phone                                       = fields.Char('Phone', size=128)
    model                                       = fields.Char('Model', size=128)
    lastupdate                                  = fields.Datetime('Lastupdate')
    disabled                                    = fields.Boolean('Disable', default=False)
    telcel                                      = fields.Boolean('Telcel', default=True)
    signal                                      = fields.Boolean('Good signal', default=True)
    company_ids                                 = fields.Many2many('res.company', 'tcdevices_res_company_rel', 'user_id', 'cid', string='Companies', default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('uniqueid_uniq', 'unique(uniqueid)', "The imei of the GPS device already exists"),
    ]    

    @api.model
    def create(self, vals):
        if "uniqueid" in vals:            
            devices_arg = [('uniqueid', '=', vals["uniqueid"])]
            data = self.search(devices_arg)
            if(data):
                return data 

        return  super(tc_devices, self).create(vals)
    
"""    
    @api.one
    def write(self, vals):  
        return super(tc_devices, self).write(vals)
"""
