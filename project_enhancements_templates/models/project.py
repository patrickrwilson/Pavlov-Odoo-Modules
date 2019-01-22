from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Project(models.Model):
    _inherit = 'project.project'

# TEMPLATE
    is_template = fields.Boolean(string="Is Template",
                                 copy=False)

    # CREATE A PROJECT FROM A TEMPLATE AND OPEN THE NEWLY CREATED PROJECT
    def create_project_from_template(self):
        if " (TEMPLATE)" in self.name:
            new_name = self.name.replace(" (TEMPLATE)"," (COPY)")

        new_project = self.copy(default={'name': new_name,
                                         'active': True,
                                         'total_planned_hours': 0.0})
        new_project.next_task_number = self.next_task_number
        if new_project.subtask_project_id != new_project.id:
            new_project.subtask_project_id = new_project.id
        # Clear Email Alias if it was set in the Template
        if new_project.alias_name:
            new_project.alias_name = False

        # SINCE THE END DATE DOESN'T COPY OVER ON TASKS, POPULATE END DATES ON THE TASK
        for record in new_project.tasks:
            if record.date_start and record.date_end == False:
                record.write({'date_end': (record.date_start + relativedelta(days =+ 7))})

        # OPEN THE NEWLY CREATED PROJECT FORM
        return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.project',
                'target': 'current',
                'res_id': new_project.id,
                'type': 'ir.actions.act_window'
        }
        # FORCE PAGE REFRESH TO ALLOW FOR PROPER ONCHANGE EVENTS LIKE SHIFTING DATES
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # ADD "(TEMPLATE)" TO THE NAME WHEN PROJECT IS MARKED AS A TEMPLATE
    @api.onchange('is_template')
    def on_change_is_template(self):
        # Add "(TEMPLATE)" to the Name if is_template == true
        if self.name:
            if self.is_template == True:
                if "(TEMPLATE)" not in self.name:
                    self.name = self.name + " (TEMPLATE)"
                if self.user_id:
                    self.user_id = False
                if self.partner_id:
                    self.partner_id = False
                if self.alias_name:
                    self.alias_name = False

            else:
                if " (TEMPLATE)" in self.name:
                    self.name = self.name.replace(" (TEMPLATE)","")
