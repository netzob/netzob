
var APIClient = (function() {
    var instance;
 
    function createInstance() {
        var client = new $.RestClient('http://localhost:5000/api/p/1/', {stringifyData: true});
	
	client.add('captures');
	client.add('messages');
	client.add('symbols', {
	    verbs: {
		create: "POST",
		read: "GET",
		patch: "PATCH"
	    }
	});
	
	client.symbols.add('messages', {
	    stripTrailingSlash: true,
	});
	client.symbols.add('cells', {
	    stripTrailingSlash: true,
	});
	client.symbols.add('split_align', {
	   stripTrailingSlash: true,
	}); 
        return client;
    }
 
    return {
        getInstance: function () {
            if (!instance) {
                instance = createInstance();
            }
            return instance;
        }
    };
})();

function create_message(cid, source, destination, data, function_cb) {
    var client = APIClient.getInstance();
    console.log("cid="+cid);
    payload = {"cid":cid,"source": source, "destination": destination, "data": data};
    
    client.messages.create(payload).done(function_cb);
}

function create_capture(name, function_cb) {

    var client = APIClient.getInstance();
    
    client.captures.create({"name":name,}).done(function_cb);
}

function create_symbol(name, function_cb) {

    var client = APIClient.getInstance();
    
    client.symbols.create({"name":name,}).done(function_cb);
}

function patch_symbol_name(sid, name, function_cb) {

    var client = APIClient.getInstance();
    
    client.symbols.patch(sid, {"name":name }).done(function_cb);
}
function patch_symbol_description(sid, description, function_cb) {

    var client = APIClient.getInstance();
    
    client.symbols.patch(sid, {"description":description }).done(function_cb);
}


function delete_symbol(sid, function_cb) {
    
    var client = APIClient.getInstance();
    
    client.symbols.del(sid).done(function_cb);
}

function put_message_in_symbol(sid, mid, function_cb) {    
    var client = APIClient.getInstance();
    
    client.symbols.messages.update(sid, mid).done(function_cb);

}
function get_symbols(function_cb) {
    var client = APIClient.getInstance();
    
    client.symbols.read().done(function_cb);
}
function get_symbol(sid, function_cb) {
    var client = APIClient.getInstance();
    
    client.symbols.read(sid).done(function_cb);
}
function get_symbol_cells(sid, function_cb) {
    var client = APIClient.getInstance();
    
    client.symbols.cells.read(sid).done(function_cb);
}
function symbol_split_align(sid, function_cb) {
    var client = APIClient.getInstance();
    
    client.symbols.split_align.read(sid).done(function_cb);
}

function get_captures(function_cb) {
    var client = APIClient.getInstance();
    
    client.captures.read().done(function_cb);
}

