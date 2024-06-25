
function api_get_itemmaster(done_callback) {
    // console.log(query);
    $.ajax({
        url: "/items/",
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

// codemaster.html에 db에 저장된 모든 정보를 띄워줍니다.
function api_search_itemmaster(param, page, done_callback) {
    let query = "?";
    if (param != null) {
        // if (param[0] !== null) query += "factory_division=" + param[0] + "&";
        if (param[1] !== null) query += "type=" + param[1] + "&";
        if (param[2] !== null) query += "name=" + param[2] + "&";
        if (param[3] !== null) query += "item_division=" + param[3] + "&";
        // if (param[4] !== null) query += "enable=" + param[4] + "&";
        // if (param[5] !== null) query += "search=" + param[5];
    }

    if (page == undefined || page == null) {
        page = 1;
    }
    query += "&page=" + page;

    console.log(query);
    $.ajax({
        url: "/items/" + query,
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

function api_post_detail_itemmaster_form(allData, done_callback) {
    $.ajax({
        url: "/items/",
        data: allData,
        type: "POST",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        processData: false,
        contentType: false,
    })
        .done(function () {
            // add cookie
            done_callback();
        })
        .fail(handle_error);
}

function api_post_detail_itemmaster(allData, done_callback) {
    $.ajax({
        url: "/items/",
        data: allData,
        type: "POST",
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

function api_patch_detail_itemmaster_form(code_group_id, allData, done_callback) {
    $.ajax({
        url: "/items/" + code_group_id + "/",
        data: allData,
        type: "PATCH",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        processData: false,
        contentType: false,
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}

function api_patch_detail_itemmaster(code_group_id, allData, done_callback) {
    $.ajax({
        url: "/items/" + code_group_id + "/",
        data: allData,
        type: "PATCH",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}

function api_delete_detail_itemmaster(code_group_id, done_callback) {
    $.ajax({
        url: "/items/" + code_group_id + "/",
        type: "DELETE",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}



