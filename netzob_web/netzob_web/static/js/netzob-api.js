
var APIClient = (function() {
    var instance;
 
    function createInstance() {
        var client = new $.RestClient('http://localhost:5000/api/p/1/', {stringifyData: true});

	client.add('misc', {
	    stripTrailingSlash: true,
	});
	//client.misc.add('parse_pcap');
	
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

function create_message(cid, message, function_cb) {
    var client = APIClient.getInstance();
    message.cid = cid;
    client.messages.create(message).done(function_cb);
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


function delete_symbol(sid) {
    
    var client = APIClient.getInstance();
    
    return client.symbols.del(sid).done();
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
function symbol_split_align(sid) {

    
    var deferred = new $.Deferred();
    var client = APIClient.getInstance();
    return client.symbols.split_align.read(sid).done();
	
}

function get_captures(function_cb) {
    var client = APIClient.getInstance();
    
    client.captures.read().done(function_cb);
}

function parse_raw(raw_filename, raw_file_content, delimiter, function_cb) {
    var client = APIClient.getInstance();

    client.misc.create("parse_raw", {"filename": raw_filename, "delimiter": delimiter, "raw": raw_file_content}).done(function_cb);
}

function parse_pcap(pcap_filename, pcap_file_content, layer, bpf_filter) {
    var client = APIClient.getInstance();

    return client.misc.create("parse_pcap", {"filename": pcap_filename, "layer": layer, "bpf": bpf_filter, "pcap": pcap_file_content}).done();
}
