//db에 저장된 모든 정보를 codemaster_managepopup.html에 띄워줍니다.
function api_get_groupcodemaster(done_callback) {
    $.ajax({
        url: "/group_codes/",
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: { withCredentials: true },
    })
    .done(function (json) {
        // add cookie
        done_callback(json);
    })
    .fail(handle_error);
}
function api_post_generate_codemaster(done_callback){
    $.ajax({
        url: "/generate_codes/",
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
//codemaster_managepopup.html에서 그룹코드를 생성합니다.
function api_post_group_codemaster(code_group, code_group_name, done_callback){
    $.ajax({
        url: "/group_codes/",
        data: {
            code: code_group,
            name: code_group_name,
        },
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

//codemaster_managepopup.html에서 그룹코드를 수정합니다.
function api_patch_group_codemaster(group_code_num, code_group, code_group_name, done_callback){
    $.ajax({
        url: "/group_codes/"+group_code_num+"/",
        data: {
            code: code_group,
            name: code_group_name,
        },
        type: "PATCH",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (data) {
            console.log(data);
            done_callback();
        })
        .fail(handle_error);
}