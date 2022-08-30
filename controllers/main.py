import json
from odoo import http, _
from odoo.http import request

class map_online(http.Controller):
    @http.route('/map_online', type='http', auth='public', website=True)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        print("##### ROUTE ##########################")

        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        mirror = env['gps_mirror']

        data = mirror.search([('name', '=', '0611251ae1f79a45c0ff3969d94b3566')])
        print(data.vehicle_ids)

        positions = {}
        for vehicle in data.vehicle_ids:
            if(vehicle.positionid):
                pos = vehicle.positionid

                position = {
                    "idv": vehicle.id,
                    "nam": vehicle.name,
                    "lic": vehicle.license_plate,
                    "ima": vehicle.image_vehicle,
                    "vsp": vehicle.speed,
                    "oun": vehicle.odometer_unit,
                    "idp": pos.id,
                    "lat": pos.latitude,
                    "lon": pos.longitude,
                    "alt": pos.altitude,
                    "psp": pos.speed,
                    "tde": pos.devicetime,
                    "dat": pos.devicetime.strftime("%Y-%m-%d"),
                    "tim": pos.devicetime.strftime("%H:%M"),
                    "tse": pos.servertime,
                    "tfi": pos.fixtime,
                    "sta": pos.status,
                    "eve": pos.event,
                    "gas": pos.gas,
                    "dis": pos.distance,
                    #"dto" :totalDistance,
                    "cou": pos.course,
                    "bat": pos.batery,

                }
                print(position)
        #return request.render("gpsmap.gpsmaps_maponline", {'vehicles':vehicle})
        return request.render("gpsmap.maponline")