

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime, time
import requests, json
import random
import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz

class vehicle(models.Model):
    _inherit = "fleet.vehicle"
    image_vehicle = fields.Selection([
        ('01', 'Gray Vehicle'),
        ('02', 'Red Vehicle'),
        ('03', 'Camioneta Gris'),
        ('04', 'Camioneta Gris'),
        ('05', 'White truck'),
        ('06', 'White van'),
        ('07', 'Blue van'),
        ('30', 'Moto'),
        ('90', 'Black Phone'),
        ('91', 'Blue  Phone'),
        ('92', 'Green Phone'),
        ('93', 'Red  Phone')
        ], 'Img GPS', default='01', help='Image of GPS Vehicle', required=True)
    temporal_id                                 = fields.Many2one('res.partner', 'temporal')
    #phone                                       = fields.Char('Phone', size=50)    
    economic_number                             = fields.Char('Economic Number', size=50)
    #imei                                        = fields.Char('Imei', size=50)
    speed                                       = fields.Char('Exceso de Velocidad', default=100, size=3)   
    positionid                                  = fields.Many2one('gpsmap.positions',ondelete='set null', string="Position", index=True)    
    motor                                       = fields.Boolean('Motor', default=True, track_visibility="onchange")
    #devicetime                                  = fields.Datetime('Device Time')
    #devicetime_compu                            = fields.Datetime('Device Time', compute='_get_date')
    
    
    gps1_id                                     = fields.Many2one('tc_devices',ondelete='set null', string="GPS", index=True)
    



    def run_scheduler_recarga(self):
        taecel_obj                             =self.env['taecel']
        
        ahora = datetime.datetime.utcnow()
        ayer = ahora - datetime.timedelta(days=25)
        antes = ahora - datetime.timedelta(minutes=20)
    
        vehicle_args                            =[]        
        return_positions                        ={}
        vehicle_data                            =self.search(vehicle_args, offset=0, limit=None, order=None)
        #vehicle_data                            =self.search(vehicle_args, offset=0, limit=1, order=None)

        for vehicle in vehicle_data:
            recargar=0
            
            #print("# VEHICLE ========================",vehicle["name"])
            if(vehicle["recargado"] not in {"",False}): 
                if(str(vehicle["recargado"]) < str(ayer)):  
                    if(str(vehicle["devicetime_compu"]) < str(antes)):        
                        recargar=1
            else:
                recargar=2
                                
            if(recargar>0 and vehicle["phone"] not in {"",False}):
                #print("# POSIBLE RECARGA NUEVA=", recargar)
                taecel_data                     ={}
                taecel_data["name"]             ="TEL030"
                taecel_data["referencia"]       =vehicle["phone"]

                taecel_new                      =taecel_obj.create(taecel_data)
                
                #print("# taecel_new=", taecel_new)
                  
                if(taecel_new["status"]!="Error"):                                    
                    if("mensaje2" in taecel_new and taecel_new["mensaje2"]=="Recarga Exitosa" and taecel_new["status"]=="Exitosa"):              
                    #if(taecel_new["mensaje2"]=="Recarga Exitosa" and taecel_new["status"]=="Exitosa"):
                        hoy_fecha    ="%s" %(datetime.datetime.now())
                        vehicle["recargado"]=hoy_fecha[0:19]                
                        #print("mensaje2==", taecel_new["mensaje2"])
                        self.write(vehicle)

    
    @api.one
    def _get_date(self):      
        if(self.devicetime != False):          
            tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc                            
            self.devicetime_compu=tz.localize(fields.Datetime.from_string(self.devicetime)).astimezone(pytz.utc)
        else:    
            self.devicetime_compu=self.devicetime
    def toggle_motor(self):
        try:
            traccar_host                 =self.env['ir.config_parameter'].get_param('traccar_host','')
            devices_id                   =self.gps1_id["id"]
            
            if(self.motor==True):
                comando="engineStop"
            else:
                comando="engineResume"

            path="/api/commands/send"
            #url = "http://odoo.solesgps.com:8082/api/commands/send"
            url = "%s%s" %(traccar_host,path)
            payload = {
                "id"            :0,
                "description"   :"Nuevo...",
                "deviceId"      :devices_id,
                "type"          :comando,
                "textChannel"   :"false",
                "attributes"    :{}
            }                        
            
            ##headers = {	"Authorization": "Basic " + encoded		}
            headers                 = {	"Authorization": "Basic YWRtaW46YWRtaW4=","content-type": "application/json"}        

            req                     = requests.post(url, data=json.dumps(payload), headers=headers)
            req.raise_for_status()        
            json_traccar            = req.json()
            
            if(self.motor==True):
                self.motor=False
            else:
                self.motor=True                        
            
        except Exception:
            print("#####################################################")                
            print("Error al conectar con traccar")                
    @api.model    
    def js_vehicles(self):
        hoy_fecha                               ="%s" %(datetime.datetime.now())
        hoy                                     =hoy_fecha[0:19]
    
        hoy_antes                               ="%s" %(datetime.datetime.now() - datetime.timedelta(minutes=5))        
        hoy_antes                               =hoy_antes[0:19]

        #print("fecha=======",hoy)

        self.env.cr.execute("""
            SELECT tp.*, tp.deviceid as tp_deviceid, td.phone, fv.odometer_unit,
                CASE 		                
                    WHEN fv.odometer_unit='kilometers'                          THEN 1.852 * tp.speed
                    WHEN fv.odometer_unit='miles'                               THEN 1.15 * tp.speed
                    ELSE 1.852 * tp.speed                    
                END	AS speed_compu,
                CASE 				            
	                WHEN tp.attributes::json->>'alarm'!=''                      THEN tp.attributes::json->>'alarm'
	                WHEN tp.attributes::json->>'motion'='false'                 THEN 'Stopped'
	                WHEN tp.attributes::json->>'motion'='true' AND tp.speed>2   THEN 'Moving'
	                ELSE 'Stopped'
                END	as event,                                 

                CASE 				            
                    WHEN tp.attributes::json->>'alarm'!=''                      THEN 'alarm'
                    WHEN now() between tp.devicetime - INTERVAL '15' MINUTE AND tp.devicetime + INTERVAL '15' MINUTE THEN 'Online'
                    ELSE 'Offline'
                END  as status                
            FROM  fleet_vehicle fv
                join tc_devices td on fv.gps1_id=td.id
                join tc_positions tp on td.positionid=tp.id
        """)
        return_positions                    ={}
        positions                           =self.env.cr.dictfetchall()
        for position in positions:
            
            #if(position["status"]=="Offline"):
            #    print("status==",position["status"]," device==",position["devicetime"]," server===",position["servertime"]," fix==",position["fixtime"])
            position["de"]            =position["tp_deviceid"]                            
            tp_deviceid               =position["tp_deviceid"]
            
            return_positions[tp_deviceid]    =position
            
        return return_positions    

    @api.model    
    def cron_positions(self):
        sql ="""            
            SELECT 
                deviceid,protocol,tp.speed,tp.attributes,
				to_char(devicetime + INTERVAL '6' HOUR, 'YYYY-MM-DD HH24:MI:SS') as devicetime,
				to_char(servertime + INTERVAL '6' HOUR, 'YYYY-MM-DD HH24:MI:SS') as servertime,
				to_char(fixtime + INTERVAL '6' HOUR, 'YYYY-MM-DD HH24:MI:SS') as fixtime,                              
                latitude,longitude,altitude,course
            FROM    
                tc_positions tp JOIN 
                tc_devices td on td.positionid=tp.id JOIN                
				tcdevices_res_company_rel on user_id=td.id AND cid='%s'
        """ %(self.env.user.company_id.id)

        self.env.cr.execute(sql)
        return json.dumps(self.env.cr.dictfetchall())

    @api.multi
    def positions(self,datas):		   
        start_time  =datas["data"]["domain"][0][2]
        end_time    =datas["data"]["domain"][1][2]       
        type_report =datas["data"]["domain"][2][2]
        deviceid    =datas["data"]["domain"][3][2]
    
        where_report=""
        
        if(type_report=="stop"):
            where_report="AND tp.speed<2"
        if(type_report=="alarm"):
            where_report="AND tp.attributes::json->>'alarm'!=''"
        if(type_report=="offline"):
            where_report="AND tp.devicetime + INTERVAL '3' MINUTE < tp.servertime"
        if(type_report=="alarm_PowerCut"):
            where_report="AND tp.attributes::json->>'alarm'='powerCut'"
        if(type_report=="alarm_PowerOff"):
            where_report="AND tp.attributes::json->>'alarm'='powerOff'"
            
    
        sql="""
            SELECT tp.*, tp.deviceid as tp_deviceid, td.phone,
                CASE 		                
                    WHEN fv.odometer_unit='kilometers'                          THEN 1.852 * tp.speed
                    WHEN fv.odometer_unit='miles'                               THEN 1.15 * tp.speed
                    ELSE 1.852 * tp.speed                    
                END	AS speed_compu,
                CASE 				            
	                WHEN tp.attributes::json->>'alarm'!=''                      THEN tp.attributes::json->>'alarm'
	                WHEN tp.attributes::json->>'motion'='false'                 THEN 'Stopped'
	                WHEN tp.attributes::json->>'motion'='true' AND tp.speed>2   THEN 'Moving'
	                ELSE 'Stopped'
                END	as event,                                 
                CASE 				            
                    WHEN tp.attributes::json->>'alarm'!=''                      THEN 'alarm'
                    WHEN tp.devicetime + INTERVAL '3' MINUTE < tp.servertime    THEN 'Offline'
                    ELSE 'Online'
                END  as status, fv.image_vehicle
            FROM  fleet_vehicle fv
                join tc_devices td on fv.gps1_id=td.id
                join tc_positions tp on td.id=tp.deviceid
            WHERE  1=1          
                AND tp.devicetime>'%s'
                AND tp.devicetime<'%s'
                %s                 
        """ %(start_time,end_time,where_report)
        if int(deviceid)>0:
            sql="%s and td.id='%s' " %(sql,deviceid)
            
        sql="%s ORDER BY devicetime ASC" %(sql)    
                       
        self.env.cr.execute(sql)
        return_positions                    =[]
        positions                           =self.env.cr.dictfetchall()
        for position in positions:
            position["de"]            =position["tp_deviceid"]                            
            tp_deviceid               =position["tp_deviceid"]
                        
            return_positions.append(position)
            
        return return_positions    