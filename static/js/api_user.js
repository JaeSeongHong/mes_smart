// 그룹코드에서 검색 버튼 누를시에 나타나는 데이터 테이블
function api_get_user_list(param, done_callback) {
    let query = "?";

    if (param != null) {
        if (param[0] !== null && !isNaN(param[0])) query += "factory_classification=" + param[0] + "&";
        if (param[1] !== null && !isNaN(param[1])) query += "department_position=" + param[1] + "&";
        if (param[2] !== null && !isNaN(param[2])) query += "enable=" + param[2] + "&";
        if (param[3] !== null) query += "search=" + param[3];
        // if (param[3] !== null && !isNaN(param[3])) query += "username=" + param[3];
        // if (param[4] !== null && !isNaN(param[4])) query += "order_company=" + param[4];
        // Note:    The issue solved by isNan() maybe api_user.js specific issue.
    }
    console.log("query::",query);

    $.ajax({
        url: "/users/" + query,
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

function api_post_user_content(userData, done_callback) {
    $.ajax({
        url: "/users/",
        data: userData,
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

function api_patch_user_content(id, userData, done_callback){
    $.ajax({
        url: "/users/"+id+"/",
        data: userData,
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

function api_delete_user_content(employee_number_code, done_callback){
    $.ajax({
        url: "/users/"+employee_number_code+"/",
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