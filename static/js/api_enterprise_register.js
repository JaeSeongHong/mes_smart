function api_patch_enterprise_register_content(id, Data, done_callback){
    $.ajax({
        url: "/enterprises/"+id+"/",
        data: Data,
        type: "PATCH",
        headers: {
            "Authorization": get_token()
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (data) {
            done_callback(data);
        })
        .fail(handle_error);
}

function api_delete_enterprise_register_content(id, done_callback){
    $.ajax({
        url: "/enterprises/"+id+"/",
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