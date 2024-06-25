function api_search_itemmaster_adjust(param, done_callback) {
    let query = "?";
    if (param != null) {
        if (param[0] !== null) query += "purchase_from__id=" + param[0] + "&";
        if (param[1] !== null) query += "item_division__name=" + param[1] + "&";
        if (param[2] !== null) query += "code=" + param[2] + "&";
        if (param[3] !== null) query += "name=" + param[3] + "&";
        if (param[5] !== null) query += "model__name=" + param[5];
    }

    console.log(query);
    $.ajax({
        url: "/items/adjust/status/" + query,
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

// 자재현황 - 자재 현황 조회
function items_calculate_list(done_callback) {
    $.ajax({
        url: "/items/calculate/",
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

// 자재현황 - 자재 현황 조회
function items_calculate_search(my_arr, done_callback) {
    $.ajax({
        url: "/items/calculate/?purchase_from=" + my_arr[0] +
        "&item_division=" + my_arr[1] +
        "&code=" + my_arr[2] +
        "&name=" + my_arr[3] +
        "&type=" + my_arr[4] +
        "&model=" + my_arr[5]+
        //"&log_from=" + my_arr[6]+
        //"&log_to=" + my_arr[7],
        "&warehouse_keep_location__name=" + my_arr[6],
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

// 자재입고 - 입고 자재 조회
function items_in_list(done_callback) {
    $.ajax({
        url: "/items/in/",
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

// 자재출고 - 출고 자재 조회
function items_out_list(id, done_callback) {
    $.ajax({
        url: "/items/out/?item=" + id,
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


// 자재반입 - 반입 자재 조회
function items_rein_search(my_arr, done_callback) {
    $.ajax({
        url: "/items/?" + //log_from=" + my_arr[0] +
        //"&log_to=" + my_arr[1] +
        "code=" + my_arr[0] +
        "&name=" + my_arr[1] +
        "&type=" + my_arr[2] +
        "&model=" + my_arr[3] +
//        "&num=" + my_arr[6] +
        "&warehouse_keep_location__name=" + my_arr[4],
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

function validation_material_itemcode_check(type, formdata){
        let valid = true;

        let item_code_id

        if (formdata.some(item => item.name === "item")) {
              item_code_id = formdata.find(item => item.name === "item").value;
            } else {
              item_code_id = null;
            }

        if (type === "A"){
            if(item_code_id == null){
                alert("품목을 선택해주세요");
                valid = false;
            }/*else if(customer_id == null){
                alert("거래처를 선택해주세요");
                valid = false;
            }*/
        }else{

        }


        return valid;
    }

