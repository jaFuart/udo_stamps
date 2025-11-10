import frappe

def after_install():
	# Ensure roles exist
	for role in ("UDO Registry Manager", "UDO Auditor"):
		if not frappe.db.exists("Role", role):
			doc = frappe.new_doc("Role")
			doc.role_name = role
			doc.save(ignore_permissions=True)


