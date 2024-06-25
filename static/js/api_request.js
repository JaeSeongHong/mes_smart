

// hjlim new-module
// web.static.js 에 javascript file 생성 후, python manage.py collectstatic  실행해줘야 함
// 그러면 api.static.js 에 동일한 파일이 생성됨, 해당 파일을 가지고 서버에서 정적 리소스로 사용되는 것 같음

// function api_get_request(customer_code, customer_name, is_detail, done_callback) {
function api_get_request(customer_code, customer_name, done_callback) {
    $.ajax({
        url: "/request_input/",
        type: "GET",
        // dataType: 'text',
        // data:{
        //     is_detail: is_detail,
        // },
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


function api_post_request(mainData, detailData, done_callback) {
    $.ajax({
        url: "/request_input/",
        data: {
            mainData: mainData,
            detailData: detailData,
        },
        type: "POST",
        success: function(data){
          alert(data);
        },
        error: function (request,status,error) {
          alert("failed");
          alert(request, status, error);
        },
        complete: function(data) {
          alert("failed but finished");
          alert(data);
        },
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


function api_patch_request(customer_code, allData, done_callback){
    $.ajax({
        url: "/request_input/"+customer_code+"/",
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


function api_delete_request(customer_code, done_callback){
    $.ajax({
        url: "/request_input/"+customer_code+"/",
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


function api_items_get_request(customer_code, customer_name, id, done_callback) {
    $.ajax({
        url: "/request_items_input/",
        type: "GET",
        // dataType: 'text',
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


function api_items_post_request(allData, done_callback) {
    $.ajax({
        url: "/request_items_input/",
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


function api_items_patch_request(customer_code, allData, done_callback){
    $.ajax({
        url: "/request_items_input/"+customer_code+"/",
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


function api_items_delete_request(customer_code, done_callback){
    $.ajax({
        url: "/request_items_input/"+customer_code+"/",
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