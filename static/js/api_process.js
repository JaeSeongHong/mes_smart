// 공정관리 - 생산공정 조회
function process_list(filter_arr, done_callback) {
    let query = "?";
    if (filter_arr !== null) query += "code=" + filter_arr[0] +
        "&customer__id=" + filter_arr[1] +
        "&bom_master__product_name=" + filter_arr[2] +
        "&bom_master__model_name=" + filter_arr[3] +
        "&bom_master__version=" + filter_arr[4] +
        "&factory_classification=" + filter_arr[5] +
        "&amount=" + filter_arr[6] +
        "&name=" + filter_arr[7];
    $.ajax({
        url: "/process/" + query,
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

function process_search(filter_arr, done_callback) {
    let query = "?";
    if (filter_arr !== null) query += "&created_at_after=" + filter_arr[0] +
        "&created_at_before=" + filter_arr[1] +
        "&customer__id=" + filter_arr[2] +
        "&bom_master__product_name=" + filter_arr[3] +
        "&bom_master__model_name=" + filter_arr[4] +
        "&bom_master__version=" + filter_arr[5] +
        "&factory_classification=" + filter_arr[6] +
        "&name=" + filter_arr[7] +
        // "&charge=" + filter_arr[8] +
        "&s=" + filter_arr[8];
    $.ajax({
         url: "/process/" + query,
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

// 공정진행현황 조회
function process_status_list(done_callback) {
    $.ajax({
        url: "/process/status/",
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

// 공정진행현황 조회
function process_status_search(filter_arr, done_callback) {
     let query = "?";
    if (filter_arr !== null) query += "&created_at_after=" + filter_arr[0] +
        "&created_at_before=" + filter_arr[1] +
        "&customer__id=" + filter_arr[2] +
        "&bom_master__product_name=" + filter_arr[3] +
        "&bom_master__model_name=" + filter_arr[4] +
        "&bom_master__version=" + filter_arr[5] +
        "&factory_classification=" + filter_arr[6] +
        "&name=" + filter_arr[7];
        // "&charge=" + filter_arr[8];
    $.ajax({
         url: "/process/status/" + query,
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

// 공정진행현황 (개별)
function process_status_read(code, done_callback) {
    $.ajax({
        url: "/process/status/" + code + "/",
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


// 세부공정관리 - 세부공정 조회
function process_sub_templet_search(done_callback) {
    $.ajax({
        url: "/process/subtemplet/",
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

// 세부공정관리 - 세부공정 조회
function process_sub_list(done_callback) {
    $.ajax({
        url: "/process/sub/",
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

// 세부공정관리 - 세부공정 조회
function process_sub_search(my_arr, done_callback) {
    $.ajax({
        url: "/process/sub/?created_at_after=" + my_arr[0] +
        "&=created_at_before" + my_arr[1] +
        "&=customer" + my_arr[2] +
        "&=bom_master__product_name" + my_arr[3] +
        "&=bom_master__model_name" + my_arr[4] +
        "&=bom_master__version" + my_arr[5] +
        "&=factory_classification" + my_arr[6] +
        "&=name" + my_arr[7],
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

// 작업진행현황 - 공정과정 조회
function process_sub_progress_list(done_callback) {
    $.ajax({
        url: "/process/sub/progress/",
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

// 작업진행현황 - 공정과정 조회 (개별)
function process_sub_progress_read(id, done_callback) {
    $.ajax({
        url: "/process/sub/progress/" + id + "/",
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

// 세부공정관리 - 세부공정 조회 (개별)
function process_sub_read(id, done_callback) {
    $.ajax({
        url: "/process/sub/" + id + "/",
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

// 공정관리 - 생산공정 조회 (개별)
function process_read(code, done_callback) {
    $.ajax({
        url: "/process/" + code + "/",
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