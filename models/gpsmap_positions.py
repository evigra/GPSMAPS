import datetime, time
import requests, json
import random
import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz

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