from odoo import api, fields, models

class ProjectTask(models.Model):
    _inherit = "project.task"

    timer_ids = fields.One2many('timer.timer', 'task_id', string="Timers")
    timer_started = fields.Boolean(string="Timer Started")

    @api.multi
    def task_start_timer(self):
        active_timers = self.env['timer.timer'].search([('user_id','=',self._uid)])
        if active_timers:
            context = dict(self.env.context)
            context.update({'timer_id': active_timers.id})
            view_id = self.env.ref('project_enhancements_timer.timer_warning_view_form')
            return {
                    'view_id': view_id.ids,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'timer_warning',
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'target': 'new'
                    }
        else:
            self.write({'timer_started': True,
                        'timer_ids':[ (0, 0, {
                                    'name': self.name,
                                    'task_id': self.id,
                                    'project_id': self.project_id.id,
                                    'start_timer_date': fields.Datetime.now(),
                                    'user_id': self._uid})]})

    @api.multi
    def task_end_timer(self):
        active_timer = self.env['timer.timer'].search([('user_id','=',self._uid)])
        active_timer.write({'end_timer_date': fields.Datetime.now()})
        context = dict(self.env.context)
        context.update({'default_timer_id': active_timer.id,
                        'start_timer_date': active_timer.start_timer_date,
                        'end_timer_date': active_timer.end_timer_date,
                        'default_project_id': active_timer.project_id.id,
                        'default_task_id': active_timer.task_id.id})
        view_id = self.env.ref('project_enhancements_timer.task_timesheet_entry_view_form')
        return {
            'view_id': view_id.ids,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'task_timesheet_entry',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
