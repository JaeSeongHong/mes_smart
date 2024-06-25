function warehouse_adjust(param, done_callback) {
    let query = "?";
    if (param != null) {
        if (param[0] !== null) query += "purchase_from__id=" + param[0] + "&";
        if (param[1] !== null) query += "item_division__name=" + param[1] + "&";
        if (param[2] !== null) query += "code=" + param[2] + "&";
        if (param[3] !== null) query += "name=" + param[3] + "&";
        if (param[4] !== null) query += "type__name=" + param[4] + "&";
        if (param[5] !== null) query += "model__name=" + param[5];
    }

    console.log(query);
    $.ajax({
        url: "/wh/adjust/status/" + query,
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

function warehouse_calculate_list(wh_code, done_callback) {
    $.ajax({
        url: "/wh/calculate/?warehouse_code=" + wh_code,
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

function warehouse_calculate_search(my_arr, wh_code, done_callback) {
    $.ajax({
        url: "/wh/calculate/?purchase_from=" + my_arr[0] +
            "&item_division=" + my_arr[1] +
            "&code=" + my_arr[2] +
            "&name=" + my_arr[3] +
            "&type=" + my_arr[4] +
            "&model=" + my_arr[5]+
            //"&log_from=" + my_arr[6]+
            //"&log_to=" + my_arr[7],
            "&warehouse_keep_location__name=" + my_arr[6] +
            "&warehouse_code=" + wh_code +
            "&log_from=" + (my_arr.length <= 7 ? "" : my_arr[7]) +
            "&log_to=" + (my_arr.length <= 8 ? "" : my_arr[8]),
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

function warehouse_in_list(wh_code, done_callback) {
    $.ajax({
        url: "/wh/in/?item_warehouse_in_item_in__warehouse__code=" + wh_code,
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

function api_get_itemmaster_by_warehouse(code, done_callback) {
    // console.log(query);
    $.ajax({
        url: "/wh/items/?warehouse_code=" + code,
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

function warehouse_out_list(id, wh_code, done_callback) {
    $.ajax({
        url: "/wh/out/?item=" + id + "&item_warehouse_in_item_in__warehouse__code=" + wh_code,
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


function warehouse_rein_search(my_arr, wh_code, done_callback) {
    $.ajax({
        url: "/wh/items/?" + //log_from=" + my_arr[0] +
            //"&log_to=" + my_arr[1] +
            "code=" + my_arr[0] +
            "&name=" + my_arr[1] +
            "&type=" + my_arr[2] +
            "&model=" + my_arr[3] +
            //        "&num=" + my_arr[6] +
            "&warehouse_keep_location__name=" + my_arr[4] +
            "&warehouse_code=" + wh_code,
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

