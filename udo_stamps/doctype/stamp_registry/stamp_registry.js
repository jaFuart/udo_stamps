frappe.ui.form.on('Stamp Registry', {
	refresh(frm) {
		// Кнопка добавить изображение
		frm.add_custom_button(__('Добавить изображение'), () => {
			frappe.ui.get_file((file) => {
				if (file && file.file_url) {
					frm.set_value('imprint_image', file.file_url);
					frm.save();
				}
			});
		}, __('Действия'));

		// Быстрые действия статусов
		frm.add_custom_button(__('Отметить возврат'), () => {
			frm.set_value('return_date', frappe.datetime.get_today());
			frm.set_value('status', 'Возвращена');
			frm.save();
		}, __('Статус'));

		frm.add_custom_button(__('Отметить уничтожение'), () => {
			frm.set_value('destruction_date', frappe.datetime.get_today());
			frm.set_value('status', 'Уничтожена');
			frm.save();
		}, __('Статус'));
	}
});


