

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime, time
import requests, json
import random
import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz
class fuel(models.Model):
    _inherit = "fleet.vehicle.log.fuel"
class services(models.Model):
    _inherit = "fleet.vehicle.log.services"
class cost(models.Model):
    _inherit = "fleet.vehicle.cost"
class contract(models.Model):
    _inherit = "fleet.vehicle.log.contract"
class vehicle_model(models.Model):
    _inherit = "fleet.vehicle.model"
class vehicle_model_brand(models.Model):
    _inherit = "fleet.vehicle.model.brand"

# CLONAR BD
# CREATE DATABASE traccar_developer WITH TEMPLATE traccar; 
# GRANT CONNECT ON DATABASE solesgps TO odoo;
# GRANT CONNECT ON DATABASE solesgps TO admin_evigra;

class odometer(models.Model):
    _inherit = "fleet.vehicle.odometer"
    _order = "date ASC"    
    activeTime                                       = fields.Float('Active Time',digits=(3,2))
    
    @api.model    
    def run_scheduler_set_odometer(self):    
        self.env.cr.execute("""

SELECT  vehicle_id,deviceid,date_trunc('day', fecha) as fecha,  ROUND(count(fecha)/60::numeric,2) as horas, round(max(distance)::numeric / 1000,3) as km
FROM ( 
	SELECT fv.id as vehicle_id, tp.deviceid, date_trunc('minute', tp.devicetime) as fecha,  max(tp.attributes::json->>'totalDistance') as distance
	FROM tc_positions tp JOIN fleet_vehicle fv on fv.gps1_id=tp.deviceid
	WHERE tp.attributes::json->>'motion'='true' AND tp.speed>2 	
	AND  date_trunc('day', now())=date_trunc('day', tp.devicetime)
	GROUP BY tp.deviceid, date_trunc('minute', tp.devicetime),fv.id
	ORDER BY date_trunc('minute', tp.devicetime) DESC
) tabla
GROUP BY vehicle_id,deviceid, date_trunc('day', fecha)
ORDER BY date_trunc('day', fecha) DESC       

""")
        positions                           =self.env.cr.dictfetchall()
        
        for position in positions:
            odometer_data                     ={}
            
            odometer_data["vehicle_id"]     =position["vehicle_id"]
            odometer_data["date"]           =position["fecha"]
            odometer_data["value"]          =position["km"]
            odometer_data["activeTime"]          =position["horas"]
            
            self.create(odometer_data)            
                
            #print("Device==",position["deviceid"]," fecha==",position["fecha"]," horas===",position["horas"]," km==",position["km"])

class tc_devices(models.Model):
    _name = "tc_devices"
    _description = 'traccar devices'
    _order = "name DESC"
        
    name                                        = fields.Char('Name', size=128)
    uniqueid                                    = fields.Char('IMEI', size=128)
    icc                                         = fields.Char('ICC', size=30)
    phone                                       = fields.Char('Phone', size=128)
    model                                       = fields.Char('Model', size=128)
    lastupdate                                  = fields.Datetime('Lastupdate')
    disabled                                    = fields.Boolean('Disable', default=False)
    telcel                                      = fields.Boolean('Telcel', default=True)
    signal                                      = fields.Boolean('Good signal', default=True)
    company_ids                                 = fields.Many2many('res.company', 'tcdevices_res_company_rel', 'user_id', 'cid', string='Companies', default=lambda self: self.env.user.company_id)
    

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

class speed(models.Model):
    _name = "gpsmap.speed"
    _description = 'Positions Speed'
    _order = "starttime DESC"
    deviceid                                    = fields.Many2one('fleet.vehicle',ondelete='set null', string="Vehiculo", index=True)
    starttime                                   = fields.Datetime('Start Time')
    endtime                                     = fields.Datetime('End Time')
    speed                                       = fields.Float('Velocidad',digits=(3,2))


class positions(models.Model):
    _name = "gpsmap.positions"
    _description = 'GPS Positions'
    _order = "devicetime DESC"
    _pointOnVertex=""
    protocol                                    = fields.Char('Protocolo', size=15)
    deviceid                                    = fields.Many2one('fleet.vehicle',ondelete='set null', string="Vehiculo", index=True)
    servertime                                  = fields.Datetime('Server Time')
    devicetime                                  = fields.Datetime('Device Time')
    devicetime_compu                            = fields.Datetime('Device Time', compute='_get_date')
    fixtime                                     = fields.Datetime('Error Time')
    valid                                       = fields.Integer('Valido')
    latitude                                    = fields.Float('Latitud',digits=(5,10))
    longitude                                   = fields.Float('Longitud',digits=(5,10))
    altitude                                    = fields.Float('Altura',digits=(6,2))
    speed                                       = fields.Float('Velocidad',digits=(3,2))
    speed_compu                                 = fields.Float('Velocidad', compute='_get_speed', digits=(3,2))
    #gas_compu                                   = fields.Float('Gas', compute='_get_gas', digits=(5,2))
    gas                                         = fields.Float('Gas', digits=(5,2))
    course                                      = fields.Float('Curso',digits=(3,2))
    address                                     = fields.Char('Calle', size=150)
    attributes                                  = fields.Char('Atributos', size=5000)
    status                                      = fields.Char('Type', size=5000)
    #status_compu                                = fields.Char('Type', compute='_get_status', size=5000)
    leido                                       = fields.Integer('Leido',default=0)
    event                                       = fields.Char('Evento', size=70)
    online                                      = fields.Boolean('Online', default=True)
    @api.one
    def _get_speed(self):    
        vehicle_obj                             =self.env['fleet.vehicle']        
        vehicle                                 =vehicle_obj.browse(self.deviceid.id)

        if(vehicle.odometer_unit=="kilometers"):     ts=1.852
        if(vehicle.odometer_unit=="miles"):          ts=1.15
        else:                                        ts=1.852
            
        self.speed_compu=self.speed * ts        
    @api.one
    def _get_date(self):            
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc                            
        self.devicetime_compu=tz.localize(fields.Datetime.from_string(self.devicetime)).astimezone(pytz.utc)
        
    def get_system_para(self):
        para_value                              =self.env['ir.config_parameter'].get_param('gpsmap_key','')
        return para_value
    def action_addpositions(self):
        self.run_scheduler()
        
    @api.model    
    def js_positions(self):
        vehicle_obj                             =self.env['fleet.vehicle']        
        vehicle_args                            =[]        
        return_positions                        ={}
        vehicle_data                            =vehicle_obj.search(vehicle_args, offset=0, limit=None, order=None)
        if len(vehicle_data)>0:         
            for vehicle in vehicle_data:    

                #print("Anterior VEHICULO JS POSITION=== ", vehicle.positionid)
                positions_arg                   =[('deviceid','=',vehicle.id)]                
                positions_data                  =self.search_read(positions_arg, offset=0, limit=1, order='devicetime DESC')        
                if len(positions_data)>0:                            
                    return_positions[vehicle.id]    =positions_data[0]        
            

        return return_positions
    def run_scheduler_del_position(self):
        positions_arg                           =[('leido','=',0)]                
        positions_data                          =self.search(positions_arg, offset=0, limit=1000, order='devicetime DESC')        

    def run_scheduler_get_position(self):    
        now                                     = datetime.datetime.now()
                
        positions_obj                           =self.env['gpsmap.positions']
        vehicle_obj                             =self.env['fleet.vehicle']
        speed_obj                               =self.env['gpsmap.speed']
        #mail_obj                                =self.env['mail.message']
        geofence_obj                            =self.env['gpsmap.geofence']
                
        alerts_data                             =geofence_obj.geofences()
        
        positions_arg                           =[('leido','!=',1)]                
        positions_data                          =positions_obj.search(positions_arg, offset=0, limit=200, order='devicetime DESC')        
        
        
        #if type(positions_data) is list and len(positions_data)>0:     
        if len(positions_data)>0:
            #print('=============== READ POSITIONS ===================',len(positions_data))  
            for position in positions_data:
                vehicle_arg                     =[('id','=',position.deviceid.id)]                
                vehicle                         =vehicle_obj.search(vehicle_arg)        
                
                if len(vehicle)>0:                                                                     
                    if(vehicle.positionid.id==False):
                        vehicle["positionid"]=position.id
                    elif(vehicle.positionid.devicetime < position.devicetime):
                        vehicle["positionid"]=position.id
                                        
                    if vehicle.speed=='':
                        vehicle.speed               =100
                    if vehicle.speed==0:
                        vehicle.speed               =100    

                    speed_arg                       =[['deviceid','=',position.deviceid.id],['endtime','=',False]]                
                    speed_data                      =speed_obj.search(speed_arg, offset=0, limit=50000)        
                                                                                    
                    if float(vehicle.speed) < float(position.speed_compu):
                        position["event"]    ="speeding"
                        position["status"]   ="alarm"
                        if(len(speed_data)==0):
                            speed                       ={}
                            speed["deviceid"]           =position.deviceid.id
                            speed["starttime"]          =position.devicetime
                            speed["speed"]              =position.speed_compu
                            speed_obj.create(speed)
                            
                            mail                        ={}
                            mail["model"]               ="gpsmap.positions"        
                            mail["res_id"]              =position.id                        
                            mail["message_type"]        ="comment"                        
                            mail["body"]                ="Contenido del mensaje %s" %(vehicle.name) 
                            
                            #ail_obj.create(mail)        
                            print('Exceso de velocidad===================')
                            print(mail)                                                
                    else:
                        if(len(speed_data)>0):
                            speed                       ={}
                            for speed in speed_data:
                                speed["endtime"]        =position.devicetime
                                speed_obj.write(speed)                        
                                #print('Saliendo del exceso de velocidad')
                        #if len(speed_data)>0:
                    attributes = json.loads(position.attributes)
                    
                    if("io3" in attributes):                    gas     =attributes["io3"]        
                    elif("fuel" in attributes):                 gas     =attributes["fuel"]        
                    elif("fuel1" in attributes):                gas     =attributes["fuel1"]        
                    else:                                       gas     =0
                    
                    if("alarm" in attributes):                  
                        position["event"]                       =attributes["alarm"]
                        position["status"]                      ="alarm"
                
                    position["gas"]                             =gas
                position["leido"]                           =1                                
                positions_obj.write(position)
                vehicle_obj.write(vehicle)

class route(models.Model):
    _name = "gpsmap.route"
    _description = 'GPS Route'
    _pointOnVertex=""
    name = fields.Char('Name', size=75)
    description = fields.Char('Description', size=150)
    area = fields.Text('area')
    attributes = fields.Text('Attributes')
    points = fields.Text('Points')
    hidden = fields.Boolean('Hidden')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)
    company_ids = fields.Many2many('res.company', 'route_res_company_rel', 'user_id', 'cid', string='Companies', default=lambda self: self.env.user.company_id)


class geofence(models.Model):
    _name = "gpsmap.geofence"
    _description = 'GPS Geofence'
    _pointOnVertex=""
    name = fields.Char('Name', size=75)
    description = fields.Char('Description', size=150)
    area = fields.Text('area')
    attributes = fields.Text('Attributes')
    points = fields.Text('Points')
    color = fields.Selection([
        ('green', 'Green'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('black', 'Black'),
        ('grey', 'Grey'),
        ('yellow', 'Yellow'),
        ], 'Color', default='green', help='Color of geofence', required=True)
    hidden = fields.Boolean('Hidden')
    
    #company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)    
    company_ids = fields.Many2many('res.company', 'geofence_res_company_rel', 'user_id', 'cid', string='Companies', default=lambda self: self.env.user.company_id)
                 
    
    def geofences(self):
        alerts_obj      =self.env['gpsmap.geofence_device']

        alerts_args    =[]
        alerts_data    =alerts_obj.search(alerts_args, offset=0, limit=None, order=None)

        #if len(alerts_data)>0:                     
            #for alerts in alerts_data:
            #    print('ALERT ====================',alerts.name)        
        
        return alerts_data
                
        
        
class geofence_device(models.Model):
    _name = "gpsmap.geofence_device"
    _description = 'GPS Geofence Device'
    _pointOnVertex=""
    name = fields.Char('Name', size=75)
    description = fields.Char('Description', size=150)
    mail_in = fields.Char('Mail In', size=150)
    mail_out = fields.Char('Mail Out', size=150)    
    geofence_ids = fields.Many2many('gpsmap.geofence', 'alert_geofence', 'geofence_id', 'alert_id', string='Geofence')
    device_ids = fields.Many2many('fleet.vehicle', 'alert_device', 'device_id', 'alert_id', string='Device')            
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)
    company_ids = fields.Many2many('res.company', 'geofence_device_res_company_rel', 'user_id', 'cid', string='Companies', default=lambda self: self.env.user.company_id)
    
    
    
class tc_geofences(models.Model):
    _name = "tc_geofences"
    _description = 'GPS Geofence'
    
    name = fields.Char('Name', size=75)
    description = fields.Char('Description', size=150)
    area = fields.Text('area')
    attributes = fields.Text('Attributes')
    color = fields.Selection([
        ('green', 'Green'),
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('black', 'Black'),
        ('grey', 'Grey'),
        ('yellow', 'Yellow'),
        ], 'Color', default='green', help='Color of geofence')
    hidden = fields.Boolean('Hidden')   
    company_ids = fields.Many2many('res.company', 'tc_geofences_res_company_rel', 'user_id', 'cid', string='Companies', default=lambda self: self.env.user.company_id)



    @api.model
    def create(self, vals):
        rec = super(tc_geofences, self).create(self.save(vals))
        return rec
    @api.model
    def write(self, vals):        
        rec = super(tc_geofences, self).writ(self.save(vals))
        return rec

    def save(self, vals):        
        vals["attributes"]={}
        if("color" in vals):                  
            vals["attributes"]["color"]=vals["color"]    
    
        vals["attributes"] = json.dumps(vals["attributes"])
    
        return vals
    
    def geofences(self):
        alerts_obj      =self.env['gpsmap.geofence_device']

        alerts_args    =[]
        alerts_data    =alerts_obj.search(alerts_args, offset=0, limit=None, order=None)

        #if len(alerts_data)>0:                     
            #for alerts in alerts_data:
            #    print('ALERT ====================',alerts.name)        
        
        return alerts_data
                
        
class gpsmap_device(models.Model):
    _name = "gpsmap_device"
    _description = 'GPS Device'
    name        = fields.Char('Device Name', size=75)
    protocol    = fields.Char('protocol', size=75)

class gpsmap_commands(models.Model):
    _name = "gpsmap_commands"
    _description = 'GPS Commands'
    name            = fields.Char('Command', size=75)
    priority        = fields.Char('priority', size=75)
    #deviceid    = fields.Many2one('gpsmap_device',ondelete='set null', string="Device", index=True)

class device_commands(models.Model):
    _name = "device_commands"
    _description = 'GPS Device Commands'
    commands_id = fields.Many2many('gpsmap_device', 'gpsmap_commands', 'device_id', 'command_id', string='Commands')


