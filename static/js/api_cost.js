
// 제품별원가 - 제품별 원가조회
function cost_by_product_search(done_callback) {
    $.ajax({
        url: "/cost/product/search/",
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