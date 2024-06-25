// TODO: CSRF token process

function api_login(username, password, done_callback) {
    $.ajax({
        url: "/users/login/",
        data: {username: username, password: password},
        type: "POST",
        dataType: "json"
    })
        .done(function (json) {
            // add cookie

            document.cookie = "Authorization=Token " + json.token + "; path=/;";
            document.cookie = "user_id=" + json.user.id + "; path=/;";
            document.cookie = "usercode=" + json.user.code + "; path=/;";
            document.cookie = "username=" + json.user.username + "; path=/;";
            document.cookie = "is_superuser=" + json.user.is_superuser + "; path=/;";
            document.cookie = "is_master=" + json.user.is_master + "; path=/;";
            document.cookie = "permissions=" + json.user.permissions + "; path=/;";
            document.cookie = "enterprise_id=" + json.user.enterprise + "; path=/;";
            document.cookie = "enterprise_name=" + json.user.enterprise_name + "; path=/;";
            document.cookie = "enterprise_manage=" + json.user.enterprise_manage + "; path=/;";
            document.cookie = "order_company=" + json.user.order_company + "; path=/;";
            document.cookie = "snd_auth=" + json.user.snd_auth + "; path=/;";
            done_callback();
        })
        .fail(handle_error);
}


function api_gp(url, type, data, done_callback) {
    $.ajax({
        url: url, data: data, type: type, dataType: "json", headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        }
    })
        .done(function (json) {
            if (json == undefined) {
                return done_callback(null);
            }

            if (json.hasOwnProperty('error')) {
                if (json.error = true) {
                    alert(json.message);
                }
                return;
            }

            done_callback(json);
        })
        .fail(handle_error);
}

function api_gp_file(url, type, data, done_callback) {
    $.ajax({
        url: url, data: data, type: type, dataType: "json", headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        }, processData: false, contentType: false
    })
        .done(function (json) {
            if (json.hasOwnProperty('error')) {
                if (json.error = true) {
                    alert(json.message);
                }
                return;
            }

            done_callback(json);
        })
        .fail(handle_error);
}

function flush_token() {
    document.cookie = 'Authorization=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'user_id=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'usercode=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'username=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'is_superuser=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'is_master=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'permissions=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'enterprise_id=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'enterprise_name=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'enterprise_manage=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'order_company=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    document.cookie = 'snd_auth=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function get_token() {
    return get_cookie("Authorization");
}

function get_userinfo() {
    return {
        code: get_cookie("usercode"),
        name: get_cookie("username"),
        permissions: get_cookie("permissions"),
        is_superuser: get_cookie("is_superuser"),
        is_master: get_cookie("is_master"),
        enterprise_name: get_cookie("enterprise_name"),
        enterprise_manage: get_cookie("enterprise_manage"),
        order_company: get_cookie("order_company")
    }
}

// TODO:
function get_cookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function handle_error(xhr, status, errorThrown) {
    if (xhr.status === 401) {
        flush_token();
        // alert("사용자 정보가 만료되었습니다. 다시 로그인 해주세요.");
        top.location.replace('/');
        return;
    } else if (xhr.status === 500) {
        alert("서버 에러가 발생하였습니다. 관리자에게 문의 바랍니다.");
        return;
    }

    let errs = JSON.parse(xhr.responseText);
    let string_builder = "오류가 발생하였습니다. 아래 메시지를 참고하여 다시 입력 바랍니다.\n";
    for (const err in errs) {
        string_builder += "- " + errs[err] + "\n";
    }
    alert(string_builder);
}

function loading_start() {
    $('html').css("cursor", "wait");
}

function loading_finish() {
    $('html').css("cursor", "auto");
}

function setRowColor(obj, type){
     //선택 row 색상 표시
    if (type=='M'){
        $(obj).css('background-color', 'yellow');
    }else{
     $(obj).css('background-color', 'orange');
    }

     $(obj).siblings().css('background-color', '');
}


