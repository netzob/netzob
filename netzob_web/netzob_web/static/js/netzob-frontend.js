function initialize_nav(current_sid) {
    refresh_nav(current_sid);

    initialize_new_symbol_form();

    reset_job_progress_bar();    
}

/** 
 * start - JOB PROGRESS BAR
 */

function reset_job_progress_bar() {
    set_job_progress_bar_value(0);
}

function set_job_progress_bar_value(value) {
    $("#job_progress_bar").css('width',value+'%').attr('aria-valuenow', value);
}

function start_job(job) {
    set_job_progress_bar_value(10);
    
    job.then(() => {
	
	set_job_progress_bar_value(100);

	new Promise(resolve => setTimeout(resolve, 2000)).then(
	    () => {
		reset_job_progress_bar();
	    }
	);
	
    });    

    return job
}

/** 
 * end - JOB PROGRESS BAR
 */


function initialize_new_symbol_form() {
    $("#new_symbol_button").click(function() {

	var symbol_name = $("#new_symbol_name").val();

	create_symbol(symbol_name, function(result) {
	    refresh_nav_symbols();

	    $("#new_symbol_modal").modal('toggle');	    	    
	});
	
    });
}

function refresh_nav(current_sid) {

    refresh_nav_symbols(current_sid);

    refresh_nav_captures();

}

function refresh_nav_symbols(current_sid) {
    $("li.list-symbols-entry").remove()
    
    get_symbols(function(symbols) {
	
	for (i=0; i< symbols.length; i++) {

	    var active_class = "";
	    if (symbols[i].id === current_sid) {
		
		active_class = " active";
	    }
	    
	    $("#list-symbols").prepend('<li class="list-symbols-entry"><a href="/symbols/'+symbols[i].id+'" class="'+active_class+'">'+symbols[i].name+'</a></li>');
	}
	if (symbols.length === 0) {
	    $("#list-symbols").prepend('<li class="list-symbols-entry"><a href="#" >No symbol found</a></li>');
	}
	
    });
}

function refresh_nav_captures() {
    $("li.list-captures-entry").remove()
    
    get_captures(function(captures) {
	for (i=0; i< captures.length; i++) {
	    $("#list-captures").append('<li class="list-captures-entry"><a href="/captures/'+captures[i].id+'">'+captures[i].name+'</a></li>');
	}
	if (captures.length === 0) {
	    $("#list-captures").append('<li class="list-captures-entry"><a href="#">No capture found</a></li>');
	}

	
    });
    
}


