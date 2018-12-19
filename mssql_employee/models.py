# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.sql import drop_view_if_exists




class MsslEmployee(models.Model):
    _name = "mssql.employee"
    _auto = False

    name = fields.Char(readonly=True)
    employee_no = fields.Char(readonly=True)
    street2 = fields.Char(readonly=True)

    #@api.model_cr
    def init(self, cr):
    	drop_view_if_exists(cr, 'mssql_employee')
        cr.execute("""
	        create or REPLACE view mssql_employee as (
		        SELECT 
		        	A.id as id,  
		        	A.login as name, 
		        	B.street as employee_no,
		        	B.street2 as street2
	        
	        FROM res_users A
		        left join res_partner B
		        on (A.partner_id = B.id)       
        )""" )

