from odoo import models, fields, api

class ProjectMilestone(models.Model):
     _name = 'project.milestone'

#General
     name = fields.Char(string="Title", required=True)
     target_date = fields.Date(string="Target Date", required=False)
     actual_date = fields.Date(string="Actual Date", required=False)
     percent_complete = fields.Integer(string="Percent Complete")

     project_id = fields.Many2one('project.project', string="Project")
     project_tasks = fields.One2many('project.task', 'milestone_id', string="Project Tasks")
     fold = fields.Boolean(string="KanBan Folded?")
     sequence = fields.Integer(string="KanBan Sequence")
