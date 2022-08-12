import datetime, time
import requests, json
import random
import base64
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import pytz

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
