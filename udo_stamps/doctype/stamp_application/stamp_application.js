frappe.ui.form.on('Stamp Application', {
	refresh(frm) {
		// Быстро создать запись реестра (для UDO Registry Manager)
		if (frappe.user.has_role('UDO Registry Manager') && frm.doc.workflow_state && frm.doc.workflow_state !== 'Draft') {
			frm.add_custom_button(__('Быстро создать запись реестра'), () => {
				frappe.call({
					method: 'udo_stamps.udo_stamps.api.create_registry_from_application',
					args: { application_name: frm.doc.name },
					freeze: true,
					callback: (r) => {
						if (r.message) {
							frappe.msgprint(__('Создана запись реестра: {0}', [r.message]));
							frappe.set_route('Form', 'Stamp Registry', r.message);
						}
					}
				});
			}, __('Действия'));
		}
	},
	onload(frm) {
		// Фильтр для «Изготовить по образцу»
		frm.set_query('make_from_sample', () => {
			return {
				filters: {
					company: frm.doc.company,
					department: frm.doc.department,
					stamp_type: frm.doc.stamp_type,
					source_kind: frm.doc.source_kind
				}
			};
		});
	},
	document_kind(frm) { toggle_mandatory_sample(frm); },
	basis(frm) { toggle_basis_fields(frm); },
	company(frm) { frm.refresh_field('make_from_sample'); },
	department(frm) { frm.refresh_field('make_from_sample'); },
	stamp_type(frm) { frm.refresh_field('make_from_sample'); },
	source_kind(frm) { frm.refresh_field('make_from_sample'); }
});

function toggle_mandatory_sample(frm) {
	const required = frm.doc.document_kind === 'Заявка на изготовление печати';
	frm.toggle_reqd('make_from_sample', required);
}

function toggle_basis_fields(frm) {
	frm.toggle_display('justification_other', frm.doc.basis === 'Иное');
	frm.toggle_reqd('justification_other', frm.doc.basis === 'Иное');
	frm.toggle_display('justification_loss', frm.doc.basis === 'Утеря печати, штампа');
	frm.toggle_reqd('justification_loss', frm.doc.basis === 'Утеря печати, штампа');
}


