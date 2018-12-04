from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

# SCRUM
    story_point_estimate = fields.Many2one('project.scrum_point', string="Story Points")
    task_number = fields.Char(string="Task Number")
    fix_versions = fields.Many2many('project.scrum_release', relation='fixedversion_task_rel', column1='task_id', column2='version_id', string="Fix Version/s")
    affects_versions = fields.Many2many('project.scrum_release', relation='affectver_task_rel',string="Affects Version/s")
    acceptance_criteria = fields.Text(string="Acceptance Criteria")
    categories = fields.Many2many('project.scrum_category', string="Categories")
    blocking_tasks = fields.Many2many('project.task', relation='blocking_tasks_rel', column1='task1', column2='task2',string="Blocking Tasks")
    source = fields.Many2one('project.scrum_source', string="Source")
    issue_type = fields.Many2one('project.scrum_issuetype', string="Issue Type")
    labels = fields.Many2many('project.scrum_label', string="Labels")
    use_scrum = fields.Boolean(string="Use Scrum", related='project_id.use_scrum')
    issue_type_image = fields.Binary(string="Issue Type Image", related='issue_type.issue_type_image')
    reporter = fields.Many2one('res.user', string="Reporter")

    forecasts = fields.One2many('project.forecast', 'task_id', string="Forecasts")

    # USED IN THE LIST VIEWS ON FORMS
    def open_rec(self):
        return {
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'project.task',
          'res_id': self.id,
          'type': 'ir.actions.act_window',
          'target': 'new',
          'flags': {'form': {'action_buttons': True}}
        }

    #USED FOR GROUP BY SPRINTS
    @api.model
    def _read_group_sprint_ids(self, sprints, domain, order):
        # write the domain
        # - ('id', 'in', sprints.ids): add columns that should be present
        # - OR ('team_ids', '=', team_id) if team_id: add team columns
        search_domain = [('id', 'in', sprints.ids)]
        if self.env.context.get('sprint_id'):
            search_domain = ['|', ('sprint_ids', 'in', self.env.context['sprint_id'])] + search_domain

            return sprints.search(search_domain, order=order)

    sprint_id = fields.Many2one('project.scrum_sprint', string="Sprint", group_expand='_read_group_sprint_ids')

    #USED TO SET STORY NUMBER (WITH PREFIX) AND UPDATE NEXT NUMBER ON PROJECT
    @api.model
    def create(self, values):
        # Override the original create function for the res.partner model
        record = super(ProjectTask, self).create(values)
        record['task_number'] = record.project_id.label_tasks + '-' + str(record.project_id.next_task_number)
        next_num = record.project_id.next_task_number + 1
        record.project_id.write({'next_task_number': next_num})

        # Get EmployeeID from the user_id
        if record.allow_forecast:
            employee_id = self.env['hr.employee'].search([('user_id','=',record.user_id.id)])
            if employee_id.id:
                # Set EmployeeID field and if estimate already exists, create forecast record
                if record.planned_hours:
                    #Create Forecast record if planned hours is populated
                    self.env['project.forecast'].create({'employee_id': employee_id.id, 'project_id': record.project_id.id, 'task_id': record.id, 'resource_hours': record.planned_hours, 'start_date': record.date_start, 'end_date': record.date_end})

        return record

    #Create Forecast if planned_hours or user_id changes *Only if user_id AND planned_hours is populated
    @api.onchange('planned_hours', 'user_id')
    def on_change_planned_hours(self):
        # Check to make sure Task is Assigned AND has Planned Hours
        if self.user_id and self.planned_hours and self.allow_forecast:
            # Get EmployeeID from the user_id
            employee_id = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)])

            # If there is a employee record for the user_id, then a forecast record can be created...
            if employee_id.id:
                self.env['project.forecast'].create({'employee_id': employee_id.id, 'project_id': self.project_id.id, 'resource_hours': self.planned_hours, 'task_id': self._origin.id, 'start_date': self._origin.date_start, 'end_date': self._origin.date_end})

    @api.onchange('date_start', 'date_end')
    def on_change_dates(self):
        # Check to make sure there are forecasts and if so, update them
        if self.forecasts:
            # Get EmployeeID from the user_id
            for record in self.forecasts:
                record.write({'start_date': self.date_start, 'end_date': self.date_end})

# MILESTONES
    milestone_id = fields.Many2one('project.milestone', string="Milestones")
    use_milestones = fields.Boolean(string="Use Milestones", related='project_id.use_milestones')