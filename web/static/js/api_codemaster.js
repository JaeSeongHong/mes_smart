// codemaster.html에 db에 저장된 모든 정보를 띄워줍니다.
function api_get_codemaster(code_group, done_callback) {
  let query = "?";
  if (code_group !== null) query += "group=" + code_group;
  console.log(query);
  $.ajax({
    url: "/codes/" + query,
    type: "GET",
    headers: {
      Authorization: get_token(), // TODO: improve when replace it with something other one
    },
    xhrFields: { withCredentials: true },
  })
    .done(function (json) {
      // add cookie
      done_callback(json);
    })
    .fail(handle_error);
}

// 특정 Codemaster
function api_get_specific_code_list(code, done_callback) {
  $.ajax({
    url: "/codes/?group=" + code,
    type: "GET",
    headers: {
      Authorization: get_token(), // TODO: improve when replace it with something other one
    },
    xhrFields: { withCredentials: true },
  })
    .done(function (json) {
      // add cookie
      done_callback(json);
    })
    .fail(handle_error);
}

//codemaster.html의 그룹코드 선택창에 해당 정보를 띄워줍니다.
function api_get_codegroup_list(done_callback) {
  $.ajax({
    url: "/group_codes/",
    type: "GET",
    headers: {
      Authorization: get_token(), // TODO: improve when replace it with something other one
    },
    xhrFields: { withCredentials: true },
  })
    .done(function (json) {
      // add cookie
      done_callback(json);
    })
    .fail(handle_error);
}

function api_post_detail_codemaster(allData, done_callback) {
  $.ajax({
    url: "/codes/",
    data: allData,
    type: "POST",
    headers: {
      Authorization: get_token(), // TODO: improve when replace it with something other one
    },
    xhrFields: { withCredentials: true },
  })
    .done(function () {
      // add cookie
      done_callback();
    })
    .fail(handle_error);
}

function api_patch_detail_codemaster(code_group_id, allData, done_callback) {
  $.ajax({
    url: "/codes/" + code_group_id + "/",
    data: allData,
    type: "PATCH",
    headers: {
      Authorization: get_token(), // TODO: improve when replace it with something other one
    },
    xhrFields: { withCredentials: true },
  })
    .done(function () {
      done_callback();
    })
    .fail(handle_error);
}

// API 코드마스터에서 사용중
function api_delete_detail_codemaster(code_group_id, done_callback) {
  $.ajax({
    url: "/codes/" + code_group_id + "/",
    type: "DELETE",
    headers: {
      Authorization: get_token(), // TODO: improve when replace it with something other one
    },
    xhrFields: { withCredentials: true },
  })
    .done(function () {
      done_callback();
    })
    .fail(handle_error);
}
