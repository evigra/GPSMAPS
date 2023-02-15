
import datetime, time
import requests, json
#import random
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
    company_id                                  = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)   
    #motor                                       = fields.Boolean('Motor', default=True, track_visibility="onchange")
    motor                                       = fields.Boolean('Motor', default=True)

    _sql_constraints = [
        ('uniqueid_uniq', 'unique(uniqueid)', "The imei of the GPS device already exists"),
    ]    

    @api.model
    def create(self, vals):
        print("#######################")
        print(vals)
        if "uniqueid" in vals:            
            devices_arg = [('uniqueid', '=', vals["uniqueid"])]
            data = self.search(devices_arg)            
            
            if(data and len(data)>0):
                print(data)
                return data 

        return  super().create(vals)

    def execute_commands(self, vals):
        data_return={"device":{},"status_command":{}}
        traccar_host                 =self.env['ir.config_parameter'].sudo().get_param('traccar_host','')

        device=vals[0]["device"]
        command=vals[0]["command"]
        sql ="""            
            SELECT *
            FROM    
                tc_devices td JOIN                
				tcdevices_res_company_rel on user_id=td.id AND cid='%s'
            WHERE td.id='%s'
        """ %(self.env.user.company_id.id, device)

        self.env.cr.execute(sql)

        device = self.env.cr.dictfetchall()[0]

        if(self.env.user.login=="developer"):
            return {"status": "error", "message": "Developer user does not have permissions, needs a paid account"}

        if(device["uniqueid"]):
            path="/api/commands/send"
            #url = "http://odoo.solesgps.com:8082/api/commands/send"
            url = "%s%s" %(traccar_host,path)
            payload = {
                "id"            :0,
                "description"   :"Nuevo...",
                "deviceId"      :device["id"],
                "type"          :command,
                "textChannel"   :"false",
                "attributes"    :{}
            } 
             
            headers                 = {	"Authorization": "Basic YWRtaW46YWRtaW4=","content-type": "application/json"}
            req                     = requests.post(url, data=json.dumps(payload), headers=headers)
            req.raise_for_status()
 
            json_traccar            = req.json()

        return json.dumps(json_traccar)