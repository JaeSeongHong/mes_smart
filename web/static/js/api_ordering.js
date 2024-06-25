

// hjlim new-module
// web.static.js 에 javascript file 생성 후, python manage.py collectstatic  실행해줘야 함
// 그러면 api.static.js 에 동일한 파일이 생성됨, 해당 파일을 가지고 서버에서 정적 리소스로 사용되는 것 같음

function api_get_ordering(customer_code, customer_name, done_callback) {
    $.ajax({
        url: "/ordering_input/",
        type: "GET",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: { withCredentials: true },
    })
        .done(function (json) {
            done_callback(json);
        })
        .fail(handle_error);
}


function api_post_ordering(mainData, detailData, done_callback) {
    $.ajax({
        url: "/ordering_input/",
        data: {
            mainData: mainData,
            detailData: detailData,
        },
        type: "POST",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (data) {
            // add cookie
            done_callback(data);
        })
        .fail(handle_error);
}

function api_patch_ordering(customer_code, allData, done_callback){
    $.ajax({
        url: "/ordering_input/"+customer_code+"/",
        data: allData,
        type: "PATCH",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}


function api_delete_ordering(customer_code, done_callback){
    $.ajax({
        url: "/ordering_input/"+customer_code+"/",
        type: "DELETE",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}


function api_items_get_ordering(customer_code, customer_name, id, done_callback) {
    $.ajax({
        url: "/ordering_items_input/",
        type: "GET",
        data: {
            id: id,
        },
        headers: {
            "Authorization": get_token()
        },
        xhrFields: { withCredentials: true },
    })
        .done(function (json) {
            done_callback(json);
        })
        .fail(handle_error);
}


function api_items_post_ordering(allData, done_callback) {
    $.ajax({
        url: "/ordering_items_input/",
        data: allData,
        type: "POST",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (data) {
            // add cookie
            done_callback(data);
        })
        .fail(handle_error);
}


function api_items_patch_ordering(customer_code, allData, done_callback){
    $.ajax({
        url: "/ordering_items_input/"+customer_code+"/",
        data: allData,
        type: "PATCH",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}


function api_items_delete_ordering(customer_code, done_callback){
    $.ajax({
        url: "/ordering_items_input/"+customer_code+"/",
        type: "DELETE",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            done_callback();
        })
        .fail(handle_error);
}