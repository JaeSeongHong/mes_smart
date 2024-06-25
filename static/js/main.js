console.log("Hello World!");

function addrPostCodeFinder(postcodeField, addressField) {
    new daum.Postcode({
        oncomplete: function(data) {
            // 팝업에서 검색결과 항목을 클릭했을때 실행할 코드를 작성하는 부분.
            var finalAddr = '';

            // 각 주소의 노출 규칙에 따라 주소를 조합한다.
            // 내려오는 변수가 값이 없는 경우엔 공백('')값을 가지므로, 이를 참고하여 분기 한다.
            var addr = ''; // 주소 변수
            var extraAddr = ''; // 참고항목 변수

            //사용자가 선택한 주소 타입에 따라 해당 주소 값을 가져온다.
            if (data.userSelectedType === 'R') { // 사용자가 도로명 주소를 선택했을 경우
                addr = data.roadAddress;
            } else { // 사용자가 지번 주소를 선택했을 경우(J)
                addr = data.jibunAddress;
            }

            // 사용자가 선택한 주소가 도로명 타입일때 참고항목을 조합한다.
            if(data.userSelectedType === 'R'){
                // 법정동명이 있을 경우 추가한다. (법정리는 제외)
                // 법정동의 경우 마지막 문자가 "동/로/가"로 끝난다.
                if(data.bname !== '' && /[동|로|가]$/g.test(data.bname)){
                    extraAddr += data.bname;
                }
                // 건물명이 있고, 공동주택일 경우 추가한다.
                if(data.buildingName !== '' && data.apartment === 'Y'){
                    extraAddr += (extraAddr !== '' ? ', ' + data.buildingName : data.buildingName);
                }
                // 표시할 참고항목이 있을 경우, 괄호까지 추가한 최종 문자열을 만든다.
                if(extraAddr !== ''){
                    extraAddr = ' (' + extraAddr + ')';
                }
                // 조합된 참고항목을 해당 필드에 넣는다.
                finalAddr = addr + extraAddr;

            } else {
                finalAddr = addr;
            }

            // 우편번호를 해당 필드에 넣는다.
            postcodeField.value = data.zonecode;

            // 주소를 해당 필드에 넣는다.
            addressField.value = finalAddr;

        }
    }).open();
}

var getParameters = function (paramName) {
    var returnValue;
    var url = location.href;
    if (url.includes('?')) {
        var parameters = (url.slice(url.indexOf('?') + 1, url.length)).split('&');
        for (var i = 0; i < parameters.length; i++) {
            var varName = parameters[i].split('=')[0];
            if (varName.toUpperCase() == paramName.toUpperCase()) {
                returnValue = parameters[i].split('=')[1];
                return decodeURIComponent(returnValue);
            }
        }
    } else
        return "";
}

function nullapply(value) {
    return ((value === 0 || value) ? value : "");
}

function numberWithCommas(num) {
    var parts = num.toString().split(".");
    return parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (parts[1] ? "." + parts[1] : "");
}

// 숫자 체크(숫자 이외 값 모두 제거)
function chkNumber(obj){
    var tmpValue = $(obj).val().replace(/[^0-9,]/g,'');
    tmpValue = tmpValue.replace(/[,]/g,'');
    // 천단위 콤마 처리 후 값 강제변경
    obj.value = numberWithCommas(tmpValue);
}

function _numberWithCommas(num, cnt) {
    let point = false;

    if (String(num).includes(".")){
        point = true;
    }

    if (String(num).indexOf('.') == 0 ){
        return '0.';
    }

    if (String(num).indexOf('-.') == 0){
        return '-0.';
    }

    let parts = num.toString().split(".");
    // console.log('parts[0]', parts[0]);
    // console.log('parts[1]', parts[1]);

    let bf = '';  // 소수점 앞
    let af = '';  // 소수점 뒤
    bf = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",")

    if (point == true){
        af = "." + parts[1];

        if ( (cnt*1) <= 2){
            af = af.match(/.{1,3}/);  // 소수점 2자리
        } else if (( (cnt*1) == 3)){
            af = af.match(/.{1,4}/);  // 소수점 3자리
        }
        return bf + af;
    }else{
        return bf;
    }
}

// 숫자 체크(숫자 이외 값 모두 제거)
function _chkNumber(obj, cnt){
    let regexedValue = $(obj).val().replace(/[\{\}\[\]\/?,;:|\)*~`!^a-zA-Z가-힣ㅏ-ㅣㄱ-ㅎ\+_<>@\#$%&\\\=\(\'\"]/g,'');
    let tmpValue = '-';

    // - 중복 삭제
    if (regexedValue[0] !== "-" || regexedValue === '') {
        tmpValue = regexedValue;
    }
    else if (regexedValue[0] === "-") {
        for (let i = 1; i < regexedValue.length; i++){
            if(regexedValue[i] !== '-') tmpValue += regexedValue[i];
        }
    }


    // 천단위 콤마 처리 후 값 강제변경
    obj.value = _numberWithCommas(tmpValue, cnt);
}

// 반올림 함수
function round2(num){
    let ret = 0;
    let f_num = 0.0;
    let i_num = 0;

    try{
        f_num = parseFloat(num);
        i_num = parseInt(num)
    } catch (e){
        return 0;
    }

    let minus = (f_num < 0 ? true : false)
    if (minus == true){
        f_num = f_num * -1;
        i_num = i_num * -1;
    }

    ret = i_num + (f_num - i_num >= 0.5 ? 1.0 : 0.0);

    if (minus == true) {
        ret = ret * -1;
    }

    return ret
}


// 실수형 변환 함수 ( _x : 변환할 값, _y : 허용 소수점 )
function tof(_x, _y) {
    let x = 0.0;

    // _x 가 이상한 기호일 경우
    if (_x == '' || _x == undefined || _x == null) {
        return x;
    }

    if (isNaN(_x) == false) {
        // _x 가 숫자인 경우
        x = _x * 1.0;
    } else {
        try {
            // 콤마가 들어간 문자인 경우
            _x = _x.replace(/,/g, "");

            if (isNaN(_x) == false) {
                x = _x * 1.0;
            } else {
                // 숫자가 아닌 경우
            }
        } catch (e) {
            // 문자인데 다른 문자가 들어간 경우
            console.table('예외', e);
        }
    }
    // console.log('1', x);

    // _y 가 이상한 기호일 경우
    if (_y == '' || _y == undefined || _y == null) {
        _y = 0
    }

    if (isNaN(_y) == false) {
        // _y 가 숫자인 경우
    } else {
        // 숫자가 아닌 경우
        _y = 0
    }

    // 소수점 반올림
    let mul = 1;
    for (let i = 0; i < _y; i++) {
        mul *= 10;
    }

    x = x * mul * 10;
    x = round2(x)  // 소수점 한번 더 에서 반올림
    x = x / 10

    x = round2(x)
    x = x / mul

    return x;
}


$(function() {

});