from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

#Used for Kanban grouped_by view
    @api.model
    def _read_group_milestone_ids(self,milestone,domain,order):
        milestone_ids = self.env['project_milestones.milestones'].search([('projects', '=', self.env.context['default_project_id'])])
        return milestone_ids

    milestone = fields.Many2one('project_milestones.milestones', string="Milestones", group_expand='_read_group_milestone_ids')
