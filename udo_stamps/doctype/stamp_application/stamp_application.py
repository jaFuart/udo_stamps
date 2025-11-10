import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

TITLE_MAX_LEN = 140

def build_title(stamp_type: str, source_kind: str, receiver_fullname: str, company: str, department: str | None) -> str:
	parts = [p for p in [stamp_type, source_kind, receiver_fullname, f"{company}/{department}" if department else company] if p]
	title = ". ".join(parts)
	if len(title) <= TITLE_MAX_LEN:
		return title
	# укорачиваем: сначала department до инициалов (аббрев. первых букв слов)
	if department:
		dep_short = "".join([w[0] for w in department.split() if w])[:10]
		parts[-1] = f"{company}/{dep_short}"
		title = ". ".join(parts)
	if len(title) <= TITLE_MAX_LEN:
		return title
	# укорачиваем source_kind
	parts[1] = (source_kind or "")[:10]
	title = ". ".join(parts)
	if len(title) <= TITLE_MAX_LEN:
		return title
	# последний рубеж — обрезка ФИО
	parts[2] = (receiver_fullname or "")[:24]
	return ". ".join(parts)[:TITLE_MAX_LEN]

def _get_employee_name(employee: str) -> str:
	return frappe.db.get_value("Employee", employee, "employee_name") or employee

def on_validate(doc: Document, method: str | None = None):
	# Обязательность "Изготовить по образцу" для заявок на печать
	if doc.document_kind == "Заявка на изготовление печати" and not doc.make_from_sample:
		frappe.throw(_("Поле «Изготовить по образцу» обязательно для заявок на печать"))

	# Обоснования
	if doc.basis == "Иное" and not doc.justification_other:
		frappe.throw(_("Заполните поле «Обоснование (Иное)»"))
	if doc.basis == "Утеря печати, штампа" and not doc.justification_loss:
		frappe.throw(_("Заполните поле «Обоснование (при утрате)»"))

	# Если указана дата уничтожения — требуем файл приказа
	if doc.destruction_date and not doc.destruction_order:
		frappe.throw(_("При заполнении «Дата уничтожения печати» необходимо приложить «Приказ об уничтожении»"))

	# Рекомендация приложить файл
	if doc.basis in ("Приказ о создании обособленного подразделения", "Приказ о переименовании структурного подразделения", "Выписка из ЕГРЮЛ (названия компании)"):
		if not doc.attachments or not any([r.file for r in doc.attachments]):
			frappe.msgprint(_("Рекомендуется приложить файл подтверждающего документа"), alert=True, indicator="orange")

	# Валидация выбранного образца из реестра по фильтрам
	if doc.make_from_sample:
		reg = frappe.db.get_value("Stamp Registry", doc.make_from_sample, ["company", "department", "stamp_type", "source_kind", "status"], as_dict=True)
		if not reg:
			frappe.throw(_("Запись реестра не найдена"))
		if reg.company != doc.company or (doc.department and reg.department != doc.department) or reg.stamp_type != doc.stamp_type or reg.source_kind != doc.source_kind:
			frappe.throw(_("Выбранная запись реестра не соответствует фильтрам Company/Department/Тип/Выбор из"))
		if reg.status in ("Возвращена", "Уничтожена"):
			frappe.msgprint(_("Выбран образец помечен как «{0}»").format(reg.status), alert=True, indicator="orange")

	# Формирование title
	receiver_name = _get_employee_name(doc.receiver) if doc.receiver else ""
	doc.title = build_title(doc.stamp_type, doc.source_kind, receiver_name, doc.company, doc.department)

def on_update(doc: Document, method: str | None = None):
	# Автосоздание записи реестра при переходе в «Выдано получателю»
	state = getattr(doc, "workflow_state", None)
	if state == "Выдано получателю":
		existing = frappe.db.exists("Stamp Registry", {"application": doc.name})
		if not existing:
			frappe.enqueue("udo_stamps.udo_stamps.api.create_registry_from_application", queue="short", application_name=doc.name)

def has_permission(doc: Document, ptype: str, user: str) -> bool | None:
	# UDO Registry Manager — редактирование после утверждения
	if "UDO Registry Manager" in frappe.get_roles(user):
		state = getattr(doc, "workflow_state", None)
		if state and state not in ("Draft", "На согласовании"):
			return True
	# Остальное по стандартным правилам
	return None


