let ulEl = document.getElementById("ul-el");
let searchInput = document.getElementById("searchInput");
let selectedCheck = document.getElementById("selected-check");
let preCheckedOut = [];

function renderMultiSelect(things) {
    let listItems = "";
    for (let i = 0; i < things.length; i++) {
        listItems += `<li class="names"><label class="label" for="${things[i].id}"><input class="check" type="checkbox" value="${things[i].id}" name="checkbox" id="${things[i].id}"><span>${things[i].name}</span></label></li>`;
    }
    ulEl.innerHTML = listItems;
}

renderUpdatedList = (list) => {
    const parent = document.getElementById('ul-el')

    Array.from(parent.children).forEach(item => {
        item.classList.add("active");
    })
    list.forEach(item => {
        item.classList.remove("active");
    })
}

searchInput.addEventListener("input", (event) => {
    let searchQuery = event.target.value.toLowerCase();
    searchQuery = searchQuery.replaceAll('-', ' ').split(' ').filter(s => s);

    let allNamesDOMCollection = $("#multi-select #ul-el .names")
    let result = [];
    let includes;

    for (listRecord of allNamesDOMCollection) {
        let selector = listRecord.querySelector('span')
        let currentName = selector.textContent.toLowerCase().replaceAll("-", " ").split(' ').filter(s => s).join(" ");;
        includes = true;
        listRecord.classList.remove("active");
        for (words of searchQuery) {
            if (currentName.indexOf(words) === -1 || currentName.lastIndexOf(words) === -1) {
                includes = false;
                listRecord.classList.add("active");
                break;
            }

            listRecord.classList.remove("active");
        }

        if (includes) {
            result.push(listRecord);
            renderUpdatedList(result)
        }
    }
});

jQuery.each(preCheckedOut, (index, item) => {
    $(`#multi-select input[name="checkbox"][id="${item}"]`).prop('checked', true);
});

function seeCheckedNum() {
    let checked = $('#multi-select input[type="checkbox"]:checked').length;
    selectedCheck.textContent = `Selected Items : ${checked}`
}

function countChecked(){
    let preChecked = []
    preCheckedOut = preChecked;
    $("#multi-select :checkbox").map(function () {
        if (this.checked){
            preChecked.push(this.id)
        }
    })
}

let list = $("#multi-select #ul-el"),
    origOrderList = list.children();

list.on("change", ":checkbox", function () {
    let checked = document.querySelectorAll('input[type="checkbox"]:checked').length;
    if ($(this).is(':checked')) {
        selectedCheck.textContent = `Selected Items : ${checked}`
    }else{
        selectedCheck.textContent = "Selected Items : " + checked--
    }
})

$("multi-select :checkbox").change(function () {
    countChecked()
});


var clicked = false;
$("#multi-select .checkall").on("click", function () {
    $("#mysearch #ul-el .names .check:visible").prop("checked", !clicked);
    clicked = !clicked;
    this.innerHTML = clicked ? 'Deselect All' : 'Select All';
    seeCheckedNum();
    countChecked();

});


