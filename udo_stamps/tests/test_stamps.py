import frappe
from frappe.tests.utils import FrappeTestCase

class TestUDOStamps(FrappeTestCase):
	def test_title_building(self):
		app = frappe.new_doc("Stamp Application")
		app.document_kind = "Заявка на изготовление печати"
		app.company = frappe.get_all("Company", limit=1)[0].name if frappe.db.exists("Company", {}) else "Test Company"
		app.department = None
		app.stamp_type = "Печать"
		app.source_kind = "Макет"
		# Создаём сотрудника-заглушку если нет
		emp_name = None
		emps = frappe.get_all("Employee")
		if emps:
			emp_name = emps[0].name
		else:
			emp = frappe.new_doc("Employee")
			emp.employee_name = "Иванов Иван"
			emp.company = app.company
			emp.insert(ignore_permissions=True)
			emp_name = emp.name
		app.receiver = emp_name
		app.insert(ignore_permissions=True)
		self.assertTrue(app.title.startswith("Печать. Макет"))

	def test_make_from_sample_required_for_seal(self):
		app = frappe.new_doc("Stamp Application")
		app.document_kind = "Заявка на изготовление печати"
		app.company = frappe.get_all("Company", limit=1)[0].name if frappe.db.exists("Company", {}) else "Test Company"
		app.stamp_type = "Печать"
		app.source_kind = "Макет"
		emps = frappe.get_all("Employee")
		if not emps:
			emp = frappe.new_doc("Employee")
			emp.employee_name = "Петров Петр"
			emp.company = app.company
			emp.insert(ignore_permissions=True)
			emps = [emp]
		app.receiver = emps[0].name
		with self.assertRaises(frappe.ValidationError):
			app.insert(ignore_permissions=True)

	def test_create_registry_from_application(self):
		# Предусловия
		company = frappe.get_all("Company", limit=1)[0].name if frappe.db.exists("Company", {}) else "Test Company"
		emps = frappe.get_all("Employee")
		if not emps:
			emp = frappe.new_doc("Employee")
			emp.employee_name = "Сидоров Сидор"
			emp.company = company
			emp.insert(ignore_permissions=True)
			emp_name = emp.name
		else:
			emp_name = emps[0].name

		app = frappe.new_doc("Stamp Application")
		app.document_kind = "Заявка на изготовление штампа"
		app.company = company
		app.stamp_type = "Штамп"
		app.source_kind = "Макет"
		app.receiver = emp_name
		app.insert(ignore_permissions=True)

		name = frappe.call("udo_stamps.udo_stamps.api.create_registry_from_application", application_name=app.name)
		self.assertTrue(frappe.db.exists("Stamp Registry", name))

	def test_auto_create_on_state(self):
		company = frappe.get_all("Company", limit=1)[0].name if frappe.db.exists("Company", {}) else "Test Company"
		emps = frappe.get_all("Employee")
		if not emps:
			emp = frappe.new_doc("Employee")
			emp.employee_name = "Смирнов Семен"
			emp.company = company
			emp.insert(ignore_permissions=True)
			emp_name = emp.name
		else:
			emp_name = emps[0].name

		app = frappe.new_doc("Stamp Application")
		app.document_kind = "Заявка на изготовление штампа"
		app.company = company
		app.stamp_type = "Штамп"
		app.source_kind = "Макет"
		app.receiver = emp_name
		app.insert(ignore_permissions=True)

		# Эмулируем смену статуса workflow
		app.workflow_state = "Выдано получателю"
		from udo_stamps.udo_stamps.doctype.stamp_application import stamp_application as sa
		sa.on_update(app, None)
		frappe.db.commit()

		self.assertTrue(frappe.db.exists("Stamp Registry", {"application": app.name}))


