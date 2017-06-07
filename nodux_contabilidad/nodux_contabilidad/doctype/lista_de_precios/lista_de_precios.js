// Copyright (c) 2016, nodux and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lista de Precios', {
	refresh: function(frm) {

	},
	porcentaje: function(frm){
		if (frm.doc.porcentaje) {
			var porcentaje = 0;
			var formula = "";

			porcentaje = frm.doc.porcentaje / 100;
			formula = 'product.cost_price * (1 + ' +porcentaje+')';
			frm.set_value("formula", formula);
		}
		frm.refresh_fields();
	},
	nueva_formula: function(frm){
		if (frm.doc.nueva_formula){
			var valor = "";
			var formulanueva = ""
			var porcentaje = 0;
			

			valor = frm.doc.nueva_formula;
			porcentaje = frm.doc.porcentaje / 100;
			formulanueva = 'product.cost_price / (1 - ' +porcentaje+')';
			if (valor == 1) {
				frm.set_value("ver_formula", formulanueva);

			};
			// else if(valor == 0){
			// 	frm.set_value("ver_formula", limpiar);
			// 	//frm.refresh_fields("ver_formula");
			// };

			
		}
		frm.refresh_fields();
	}
});
