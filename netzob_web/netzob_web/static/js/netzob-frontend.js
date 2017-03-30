function initialize_left_nav(current_sid) {
    refresh_left_nav(current_sid);

    initialize_new_symbol_form();
    
}

function initialize_new_symbol_form() {
    $("#new_symbol_button").click(function() {

	var symbol_name = $("#new_symbol_name").val();

	create_symbol(symbol_name, function(result) {
	    refresh_left_nav_symbols();

	    $("#new_symbol_modal").modal('toggle');	    	    
	});
	
    });
}

function refresh_left_nav(current_sid) {

    refresh_left_nav_symbols(current_sid);

    refresh_left_nav_captures();

}

function refresh_left_nav_symbols(current_sid) {
    $("#list-symbols").empty()
    console.log(current_sid);
    
    get_symbols(function(symbols) {
	$("#list-symbols").empty()
	
	for (i=0; i< symbols.length; i++) {

	    var active_class = "";
	    if (symbols[i].id === current_sid) {
		
		active_class = " active";
	    }
	    
	    $("#list-symbols").append('<a href="/symbols/'+symbols[i].id+'" class="list-group-item'+active_class+'">'+symbols[i].name+'</a>');
	}
	if (symbols.length === 0) {
	    $("#list-symbols").append('<a href="#" class="list-group-item">No symbol found</a>');
	}
	
    });
}

function refresh_left_nav_captures() {
    $("#list-captures").empty()
    
    get_captures(function(captures) {
	$("#list-captures").empty()
	for (i=0; i< captures.length; i++) {
	    $("#list-captures").append('<li class="list-group-item"><a href="/captures/'+captures[i].id+'">'+captures[i].name+'</a></li>');
	}
	if (captures.length === 0) {
	    $("#list-captures").append('<li class="list-group-item">No capture found</li>');
	}	
    });
}


