

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime, time
import requests, json
import random
import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz
#class fuel(models.Model):
#    _inherit = "fleet.vehicle.log.fuel"
class services(models.Model):
    _inherit = "fleet.vehicle.log.services"
#class cost(models.Model):
#    _inherit = "fleet.vehicle.cost"
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


