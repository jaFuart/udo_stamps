app_name = "udo_stamps"
app_title = "Печати и штампы"
app_publisher = "UDO"
app_description = "Заявки на изготовление и реестр печатей/штампов"
app_email = "it@udo.local"
app_license = "MIT"

after_install = "udo_stamps.install.after_install"

fixtures = [
	# Роли (создаём при отсутствии)
	{"doctype": "Role", "filters": [["role_name", "in", ["UDO Registry Manager", "UDO Auditor"]]]},
	# Workflow, Notifications, Print Formats, Reports, Workspace
	{"doctype": "Workflow", "filters": [["document_type", "=", "Stamp Application"]]},
	{"doctype": "Notification", "filters": [["name", "like", "UDO Stamps%"]]},
	{"doctype": "Print Format", "filters": [["doc_type", "in", ["Stamp Application", "Stamp Registry"]]]},
	{"doctype": "Report", "filters": [["ref_doctype", "=", "Stamp Registry"]]},
	{"doctype": "Workspace", "filters": [["label", "=", "Печати и штампы"]]},
]

doctype_js = {
	"Stamp Application": "udo_stamps/doctype/stamp_application/stamp_application.js",
	"Stamp Registry": "udo_stamps/doctype/stamp_registry/stamp_registry.js",
}

document_events = {
	"Stamp Application": {
		"validate": "udo_stamps.udo_stamps.doctype.stamp_application.stamp_application.on_validate",
		"on_update": "udo_stamps.udo_stamps.doctype.stamp_application.stamp_application.on_update",
	},
	"Stamp Registry": {
		"validate": "udo_stamps.udo_stamps.doctype.stamp_registry.stamp_registry.on_validate",
	},
}


