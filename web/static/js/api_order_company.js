// 그룹코드에서 검색 버튼 누를시에 나타나는 데이터 테이블
function api_get_order_company_list(param, done_callback) {
    let query = "?";

    if (param != null) {
        if (param[0] !== null && !isNaN(param[0])) query += "id=" + param[0] + "&";
    }

    $.ajax({
        url: "/order/company/" + query,
        type: "GET",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

function api_post_order_company_content(Data, done_callback) {
    $.ajax({
        url: "/order/company/",
        data: Data,
        type: "POST",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function () {
            // add cookie
            done_callback();
        })
        .fail(handle_error);
}

function api_patch_order_company_content(id, Data, done_callback){
    $.ajax({
        url: "/order/company/"+id+"/",
        data: Data,
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

function api_delete_order_company_content(id, done_callback){
    $.ajax({
        url: "/order/company/"+id+"/",
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