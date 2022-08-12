import xmlrpc.client
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
    solesgps_id                                 = fields.Integer()
    uniqueid                                    = fields.Char('IMEI', size=128)
    icc                                         = fields.Char('ICC', size=30)
    phone                                       = fields.Char('Phone', size=128)
    model                                       = fields.Char('Model', size=128)
    lastupdate                                  = fields.Datetime('Lastupdate')
    disabled                                    = fields.Boolean('Disable', default=False)
    telcel                                      = fields.Boolean('Telcel', default=True)
    signal                                      = fields.Boolean('Good signal', default=True)
    company_ids                                 = fields.Many2many('res.company', 'tcdevices_res_company_rel', 'user_id', 'cid', string='Companies', default=lambda self: self.env.user.company_id)

    
    def create(self, **vals):
        data =self._get_session_information()
        print("#### data=",data)
        
        #models=data["models"]
        #db=data["db"]
        #uid=data["uid"]
        #gpsmap_pass=data["gpsmap_pass"]
        #models.execute_kw(db, uid, gpsmap_pass,'tc_devices', 'create',[vals])
        return super().create(vals)
    
    def write(self, vals):        
        rec = super().write(vals)
        return rec
    
    @api.one
    def _get_session_information(self):
        print("################################ GET INFORMATION ########################")
        gpsmap_host =self.env['ir.config_parameter'].get_param('gpsmap_host')
        gpsmap_user =self.env['ir.config_parameter'].get_param('gpsmap_user')
        gpsmap_pass =self.env['ir.config_parameter'].get_param('gpsmap_pass')
        db="produccion"
                
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(gpsmap_host))
        uid = common.authenticate(db, gpsmap_user, gpsmap_pass, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(gpsmap_host))

        return {"models":models, "db":db, "uid":uid, "gpsmap_pass":gpsmap_pass}
    