import frappe
from frappe import _
from frappe.utils import cstr

@frappe.whitelist()
def create_registry_from_application(application_name: str) -> str:
	"""Создать запись реестра из утвержденной/выданной заявки."""
	app = frappe.get_doc("Stamp Application", application_name)
	if not app:
		frappe.throw(_("Заявка не найдена"))

	# Проверка прав
	if not frappe.has_permission("Stamp Registry", ptype="create"):
		frappe.throw(_("Нет прав на создание записи реестра"))

	# Поиск существующей связки
	existing = frappe.db.exists("Stamp Registry", {"application": app.name})
	if existing:
		return cstr(existing)

	reg = frappe.new_doc("Stamp Registry")
	reg.company = app.company
	reg.department = app.department
	reg.stamp_type = app.stamp_type
	reg.source_kind = app.source_kind
	reg.receiver = app.receiver
	reg.manufacturer_org = app.manufacturer_org
	reg.application = app.name
	# title заполнится в validate по общему правилу
	reg.insert(ignore_permissions=True)

	# Лог
	frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Info",
		"reference_doctype": "Stamp Application",
		"reference_name": app.name,
		"content": _("Автоматически создана запись реестра: {0}").format(reg.name),
	}).insert(ignore_permissions=True)
	frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Info",
		"reference_doctype": "Stamp Registry",
		"reference_name": reg.name,
		"content": _("Создано из заявки: {0}").format(app.name),
	}).insert(ignore_permissions=True)

	return reg.name


