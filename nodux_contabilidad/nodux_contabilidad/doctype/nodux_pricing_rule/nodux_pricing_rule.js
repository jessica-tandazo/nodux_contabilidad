// Copyright (c) 2016, nodux and contributors
// For license information, please see license.txt

frappe.ui.form.on('Nodux Pricing Rule', {
	refresh: function(frm) {

	}
});


//Dynamically change the description based on type of margin
cur_frm.cscript.margin_type = function(doc){
	cur_frm.set_df_property('margin_rate_or_amount', 'description', doc.margin_type=='Percentage'?'In Percentage %':'In Amount')
}
