# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests import tagged, new_test_user
from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


class TestPosHrHttpCommon(TestPointOfSaleHttpCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.env.user.groups_id += cls.env.ref('hr.group_hr_user')

        cls.main_pos_config.write({"module_pos_hr": True})

        # Admin employee
        admin = cls.env.ref("hr.employee_admin").sudo().copy({
            "company_id": cls.env.company.id,
            "user_id": cls.pos_admin.id,
            "name": "Mitchell Admin",
            "pin": False,
        })

        # User employee
        emp1 = cls.env['hr.employee'].create({
            'name': 'Test Employee 1',
            "company_id": cls.env.company.id,
        })
        emp1_user = new_test_user(
            cls.env,
            login="emp1_user",
            groups="base.group_user",
            name="Pos Employee1",
            email="emp1_user@pos.com",
        )
        emp1.write({"name": "Pos Employee1", "pin": "2580", "user_id": emp1_user.id})

        # Non-user employee
        emp2 = cls.env['hr.employee'].create({
            'name': 'Test Employee 2',
            "company_id": cls.env.company.id,
        })
        emp2.write({"name": "Pos Employee2", "pin": "1234"})
        (admin + emp1 + emp2).company_id = cls.env.company

        emp3 = cls.env['hr.employee'].create({
            'name': 'Test Employee 3',
            "user_id": cls.pos_user.id,
            "company_id": cls.env.company.id,
        })

        cls.main_pos_config.write({
            'basic_employee_ids': [Command.link(emp1.id), Command.link(emp2.id), Command.link(emp3.id)]
        })


@tagged("post_install", "-at_install")
class TestUi(TestPosHrHttpCommon):
    def test_01_pos_hr_tour(self):
        # open a session, the /pos/ui controller will redirect to it
        self.main_pos_config.with_user(self.pos_admin).open_ui()

        self.start_tour(
            "/pos/ui?config_id=%d" % self.main_pos_config.id,
            "PosHrTour",
            login="pos_admin",
        )

    def test_cashier_stay_logged_in(self):
        # open a session, the /pos/ui controller will redirect to it
        self.main_pos_config.with_user(self.pos_admin).open_ui()

        self.start_tour(
            "/pos/ui?config_id=%d" % self.main_pos_config.id,
            "CashierStayLogged",
            login="pos_admin",
        )

    def test_basic_user_cannot_close_session(self):
        # open a session, the /pos/ui controller will redirect to it
        self.main_pos_config.with_user(self.pos_admin).open_ui()

        self.start_tour(
            "/pos/ui?config_id=%d" % self.main_pos_config.id,
            "CashierCannotClose",
            login="pos_user",
        )
