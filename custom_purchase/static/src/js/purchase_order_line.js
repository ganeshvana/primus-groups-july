var editPLine = function(row_id){
	$.ajax({
		url: encodeURI('/purchase_order_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&purchase_line_id='+$('#order').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#plineid').val(data[0].plineid);
			$('#purchase_order_id').val(data[0].purchase_order_id);
			$('#purchase_line_desc').val(data[0].purchase_line_desc);
			$('#date_planned').val(data[0].date_planned);
			$('#oqty').val(data[0].ordered_qty);
			$('#bqty').val(data[0].bal_to_ship);
			$('#btn_update_pline').click();	
		}
	});	
	return false;
}

var editBOMLine = function(row_id){
	$.ajax({
		url: encodeURI('/bom_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&bom_line_id='+$('#bom').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#plineidd').val(data[0].polineid);
			$('#product').val(data[0].product);
			$('#jtype').val(data[0].jtype);
			$('#bracelet_clasp').val(data[0].bracelet_clasp);
			$('#safety').val(data[0].safety);
			$('#extender').val(data[0].extender);
			$('#bracelet_extender_length').val(data[0].bracelet_extender_length);
			$('#trademark').val(data[0].trademark);
			$('#btn_update_bom').click();	
		}
	});	
	return false;
}

var editEarring = function(row_id){
	$.ajax({
		url: encodeURI('/bom_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&purchase_line_id='+$('#bom').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#product').val(data[0].product);
			$('#ejtype').val(data[0].ejtype);
			$('#inside_dia').val(data[0].inside_dia);
			$('#earring_drop_length').val(data[0].earring_drop_length);
			$('#earring_drop_width').val(data[0].earring_drop_width);
			$('#etrademark').val(data[0].etrademark);
			$('#eproduct').val(data[0].eproduct);
			$('#ear_clasp').val(data[0].ear_clasp);
			$('#btn_update_earring').click();	
		}
	});	
	return false;
}

var editRing = function(row_id){
	$.ajax({
		url: encodeURI('/bom_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&bom_line_id='+$('#bom').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#rplineid').val(data[0].polineid);
			$('#rproduct').val(data[0].product);
			$('#rjtype').val(data[0].jtype);
			$('#rtrademark').val(data[0].trademark);
			$('#shank_width').val(data[0].shank_width);
			$('#btn_update_ring').click();	
		}
	});	
	return false;
}

var editPendant = function(row_id){
	$.ajax({
		url: encodeURI('/bom_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&bom_line_id='+$('#bom').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#pplineid').val(data[0].polineid);
			$('#pproduct').val(data[0].product);
			$('#pjtype').val(data[0].jtype);
			$('#ptrademark').val(data[0].trademark);
			$('#pchain_length').val(data[0].pchain_length);
			$('#pchain_drop_length').val(data[0].pchain_drop_length);
			$('#pchain_type').val(data[0].pchain_type);
			$('#btn_update_pendant').click();	
		}
	});	
	return false;
}

var editNecklace = function(row_id){
	$.ajax({
		url: encodeURI('/bom_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&bom_line_id='+$('#bom').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#nplineid').val(data[0].polineid);
			$('#nproduct').val(data[0].product);
			$('#njtype').val(data[0].jtype);
			$('#ntrademark').val(data[0].trademark);
			$('#necklace_extender_length').val(data[0].necklace_extender_length);
			$('#btn_update_necklace').click();	
		}
	});	
	return false;
}

var editBangle = function(row_id){
	$.ajax({
		url: encodeURI('/bom_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&bom_line_id='+$('#bom').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#bplineid').val(data[0].polineid);
			$('#bproduct').val(data[0].product);
			$('#bjtype').val(data[0].jtype);
			$('#btrademark').val(data[0].trademark);
			$('#bangle_clasp').val(data[0].bangle_clasp);
			$('#btn_update_bangle').click();	
		}
	});	
	return false;
}

var editBrooche = function(row_id){
	$.ajax({
		url: encodeURI('/bom_line_get_details'),
		type: 'GET',
		data: 'wid=' + row_id +'&bom_line_id='+$('#bom').val(),
		dataType: 'json',
		error: function(jqXHR, textStatus, errorThrown) {
			if(jqXHR.responseText.indexOf('400 Bad Request: Session expired (invalid CSRF token)') >= 0){
				alert('400 Bad Request: Session expired (invalid CSRF token)\n\rRefreshing page to renew CSRF token.');
				location.reload();
			} else {
				alert(errorThrown);
			}
	    },	
		success: function(data) {
			$('#brplineid').val(data[0].polineid);
			$('#brproduct').val(data[0].product);
			$('#brjtype').val(data[0].jtype);
			$('#brtrademark').val(data[0].trademark);
			$('#brooche_desc').val(data[0].brooche_desc);
			$('#btn_update_brooche').click();	
		}
	});	
	return false;
}