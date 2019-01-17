# -*- coding: utf-8 -*-
{
    'name': "Project Enhancements",

    'summary': """
        Project Milestones, Scrum, Templates, Task Date Shifting""",

    'description': """
        This module adds Milestones, Scrum (Sprints, Releases, etc) and Templates to the Project model.
        Dependencies: Projects, Timesheets, Employees, Forecasts
    """,

    'author': "Patrick Wilson: Pavlov Media",
    'website': "https://www.pavlovmedia.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project',
    'version': '11.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'timesheet_grid', 'hr', 'project_forecast'],

    # always loaded
    'data': [
        'report/sprint_capacity_report.xml',
        'views/project_status.xml',
        'views/project_type.xml',
        'views/project.xml',
        'views/project_milestone.xml',
        'views/project_forecast.xml',
        'views/project_scrum_sprint.xml',
        'views/project_scrum_category.xml',
        'views/project_scrum_issuetype.xml',
        'views/project_scrum_label.xml',
        'views/project_scrum_point.xml',
        'views/project_scrum_release.xml',
        'views/project_scrum_source.xml',
        'views/project_scrum_epic.xml',
        'views/project_task.xml',
        'views/project_scrum_team.xml',
        'views/project_task_type.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable':True,
    'auto_install':False,
    'application':True,
}