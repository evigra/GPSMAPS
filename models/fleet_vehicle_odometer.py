

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime, time
import requests, json
import random
import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz
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
