function api_get_BOMmaster_only(bom_number, done_callback) {
    $.ajax({
        url: "/bom/master/"+bom_number+"/",
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

function api_get_BOMmaster(customer, bom_name, done_callback) {
    let query = "?";
    if (customer !== null) query += "master_customer=" + customer + "&";
    if (bom_name !== null) query += "bom_name=" + bom_name;
    console.log(query)
    $.ajax({
        url: "/bom/master/" + query,
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}
function api_lookup_BOMmaster(param, done_callback) {
    let query = "?";

    if (param != null) {
        console.log(param)
        if (param[0] !== null) query += "product_name=" + param[0] + "&";
        if (param[1] !== null) query += "model_name=" + param[1] + "&";
        if (param[2] !== null) query += "version=" + param[2] + "&";
        //if (param[3] !== null) query += "manufacturer__name=" + param[3] + "&";
        if (param[3] !== null) query += "master_customer__name=" + param[3] + "&";
        if (param[4] !== null) query += "created_at_after=" + param[4] + "&";
        if (param[5] !== null) query += "created_at_before=" + param[5];
    }

    console.log(query)
    $.ajax({
        url: "/bom/master/" + query,
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

function api_get_BOM(done_callback) {
    $.ajax({
        url: "/bom/",
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

function api_post_detail_BOMmaster(allData, done_callback) {
    $.ajax({
        type: "POST",
        url: "/bom/master/",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        processData: false,
        contentType: false,
        data: allData
    })
        .done(function () {
            // add cookie
            done_callback();
        })
        .fail(handle_error);
}

function api_patch_detail_BOMmaster(bom_number, allData, done_callback) {
    $.ajax({
        type: "PATCH",
        url: "/bom/master/"+bom_number+"/",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        processData: false,
        contentType: false,
        data: allData
    })
        .done(function () {
            // add cookie
            done_callback();
        })
        .fail(handle_error);
}

function api_delete_detail_BOMmaster(bom_number, done_callback) {
    $.ajax({
        url: "/bom/master/"+bom_number+"/",
        type: "DELETE",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            // add cookie
            done_callback();
        })
        .fail(handle_error);
}



