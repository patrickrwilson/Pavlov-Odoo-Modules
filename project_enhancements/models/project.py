from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Project(models.Model):
    _inherit = 'project.project'

# GLOBAL ENHANCEMENTS
    next_task_number = fields.Integer(string="Next Task Number", default="1", copy=False)
    project_status = fields.Many2one('project.status', string="Status")
    department = fields.Many2one('hr.department', string="Department")
    old_start_date = fields.Date(string='Old Start Date')

# UPDATE TASK NUMBER LABELS IF THE MAIN LABEL CHANGED
    @api.onchange('label_tasks')
    def on_change_label_tasks(self):
        if self._origin.label_tasks:
            old_label = self._origin.label_tasks
            new_label = self.label_tasks
            for record in self.task_ids:
                new_task_number = record.task_number
                new_task_number = new_task_number.replace(old_label, new_label)
                record.write({'task_number': new_task_number})

# UPDATE ANALYTIC ACCOUNT IF PROJECT NAME CHANGES
    @api.onchange('name')
    def on_change_name(self):
        if self.analytic_account_id:
            # ONLY CHANGE IF THE ANALYTIC ACCOUNT SHARES THE SAME NAME AS THE PROJECT NAME (COMPANY MAY WANT TO LINK PROJECTS TO CUSTOMERS AND WE WOULDN'T WANT TO CHANGE THAT)
            if self._origin.name == self.analytic_account_id.name:
                for record in self.analytic_account_id:
                    record.write({'name': self.name})

# SET OLD DATA VALUES WHEN CHANGED *USED FOR DATE SHIFTING
    @api.onchange('date_start')
    def on_change_dates(self):
        if self.old_start_date == False:
            self.old_start_date = self._origin.date_start
        if self.old_start_date == self.date_start:
            self.old_start_date = False

# SHIFT TASK DATES
    def shift_dates(self):
        # ONLY RUN IS SHIFT DATES IS TRUE
        if self.shift_task_dates and (self.old_start_date != self.date_start):
            original_start_dt = fields.Datetime.from_string(self.old_start_date)
            new_start_dt = fields.Datetime.from_string(self.date_start)
            difference = relativedelta(new_start_dt, original_start_dt)
            years = difference.years
            months = difference.months
            days = difference.days

            # SHIFT TASK DATES
            for record in self.task_ids:
                if record.date_start:
                    record.write({'date_start': (record.date_start + relativedelta(years =+ years) + relativedelta(months =+ months) + relativedelta(days =+ days))})
                else:
                    record.write({'date_start': record.project_id.date_start})

                if record.date_end:
                    record.write({'date_end': (record.date_end + relativedelta(years =+ years) + relativedelta(months =+ months) + relativedelta(days =+ days))})
                else:
                    record.write({'date_end': record.project_id.date})

                if record.date_end > record.project_id.date:
                    record.project_id.write({'date': record.date_end})

                if record.date_deadline:
                    record.write({'date_deadline': (record.date_deadline + relativedelta(years =+ years) + relativedelta(months =+ months) + relativedelta(days =+ days))})
                else:
                    record.write({'date_deadline': record.project_id.date})

                # SHIFT MILESTONE DATES
            for record2 in self.milestones:
                if record2.target_date:
                    record2.write({'target_date': (record2.target_date + relativedelta(years =+ years) + relativedelta(months =+ months) + relativedelta(days =+ days))})
        self.old_start_date = False

# SCRUM
    sprints = fields.Many2many('project.scrum_sprint', relation='project_sprint_rel', column1='project_id', column2='sprint_id', string="Sprints", copy=False)
    use_scrum = fields.Boolean(string="Use Scrum", copy=True, context="{'default_use_scrum': use_scrum}")
    releases = fields.One2many('project.scrum_release', 'project_id', string="Releases", copy=False)

# MILESTONES
    milestones = fields.One2many('project.milestone', 'project_id', string="Milestones", copy=True)
    use_milestones = fields.Boolean(string="Use Milestones", copy=True)

# TEMPLATE
    is_template = fields.Boolean(string="Is Template", copy=False)
    shift_task_dates = fields.Boolean(string="Shift Task Dates?", default=True, help="If checked, when you change the start date of a project, the dates on the Tasks will shift the number of days you change the start date of the Project. If the Project start dates were originally empty, the Start/End dates on the tasks will be set to the Project Start/End Dates unless they were previously set on the Tasks.")

    # CREATE A PROJECT FROM A TEMPLATE AND OPEN THE NEWLY CREATED PROJECT
    def create_project_from_template(self):
        new_project = self.copy(default={'name': 'NEW PROJECT FROM TEMPLATE', 'active': True})
        new_project.next_task_number = self.next_task_number

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
        if self.is_template == True:
            if "(TEMPLATE)" not in self.name:
                self.name = self.name + " (TEMPLATE)"
            if self.user_id:
                self.user_id = False
        else:
            if " (TEMPLATE)" in self.name:
                self.name = self.name.replace(" (TEMPLATE)","")
