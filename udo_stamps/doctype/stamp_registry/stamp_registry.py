import frappe
from frappe import _
from frappe.model.document import Document

from udo_stamps.udo_stamps.doctype.stamp_application.stamp_application import build_title, _get_employee_name

def on_validate(doc: Document, method: str | None = None):
	# Требовать приказ при заполненной дате уничтожения
	if doc.destruction_date and not doc.destruction_order:
		frappe.throw(_("При заполнении «Дата уничтожения печати» необходимо приложить «Приказ об уничтожении»"))

	# Автостатусы
	if doc.destruction_date:
		doc.status = "Уничтожена"
	elif doc.return_date:
		doc.status = "Возвращена"
	else:
		doc.status = "Активная"

	# Заголовок
	receiver_name = _get_employee_name(doc.receiver) if doc.receiver else ""
	doc.title = build_title(doc.stamp_type, doc.source_kind, receiver_name, doc.company, doc.department)

def has_permission(doc: Document, ptype: str, user: str) -> bool | None:
	# Получатель печати — право чтения, если user совпадает с Employee.user_id
	if ptype == "read" and user and doc.receiver:
		user_id = frappe.db.get_value("Employee", doc.receiver, "user_id")
		if user_id and user_id == user:
			return True
	return None


