$(".BOM-list th").each(function (index) {
    if (index != 0)
        this.setAttribute('data-index', index);
});

function allowDrop(ev) {
    ev.preventDefault();
}

function drag_to_list(ev) {
    ev.dataTransfer.setData("item", ev.target.id);
}

function drag_to_item(ev) {
    ev.dataTransfer.setData("list", ev.target.id);
}

function drop(ev) { //list로 drop할 때
    ev.preventDefault();
    var data = ev.dataTransfer.getData("item");
    var item = document.getElementById(data);
    if (item != null && ev.target.id === "") {
        item.removeAttribute('draggable');
        item.style.backgroundColor = "#eee"
        ev.target.innerText = item.innerText.replace("*", "");
        // ev.target.removeAttribute('ondrop');
        // ev.target.removeAttribute('ondragover');

        //item으로 다시 돌려놓기위한 drag&drop attribute 생성
        // item.setAttribute('ondrop', "drop2(event)");
        // item.setAttribute('ondragover', "allowDrop(event)");
        ev.target.setAttribute('id', item.getAttribute('id') + "i");
        ev.target.setAttribute('draggable', "true");
        ev.target.setAttribute('ondragstart', "drag_to_item(event)");
    }
}

function drop2(ev) { // item으로 drop할 때
    ev.preventDefault();
    var data = ev.dataTransfer.getData("list");
    var list = document.getElementById(data);

    let target = $('#' + data.substring(0, data.length - 1))[0]

    // if (ev.target.getAttribute('id') + "i" == data) {
    if (target.tagName.toLowerCase() == "label") {
        var parent = target.parentNode;
        parent.style.backgroundColor = "#E7F9FF";
        parent.setAttribute('draggable', "true");
        parent.setAttribute('ondragstart', "drag_to_list(event)");
    } else {
        target.style.backgroundColor = "#E7F9FF";
        target.setAttribute('draggable', "true");
        target.setAttribute('ondragstart', "drag_to_list(event)");
    }

    //list에서 제거할 때 모든 attribute를 초기화.
    list.removeAttribute('id');
    list.removeAttribute('draggable');
    list.removeAttribute('ondragstart');
    list.setAttribute('ondrop', "drop(event)");
    list.setAttribute('ondragover', "allowDrop(event)");
    list.innerText = "\u00a0";
    // }
}

function add_list() {
    var th = document.createElement('th');
    var td = document.createElement('td');
    var index_num = $(".BOM-list th").length;

    th.setAttribute('ondrop', "drop(event)");
    th.setAttribute('ondragover', "allowDrop(event)");
    th.setAttribute('class', 'new_th');
    th.setAttribute('data-index', index_num);
    th.innerText = "\u00a0";

    td.setAttribute('class', 'new_td');

    $(".BOM-list").append(th);
    $(".BOM-data").append(td);
}