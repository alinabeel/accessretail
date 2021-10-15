(function ($) {

    // convert a multiple select in a multiple checkbox

    $.fn.mselectTOmcheckbox = function () {

        var elements = $(this);

        elements.each(function (index, item) {
            var id = $(item).attr('id'),
                name = $(item).attr('name'),
                options = $(item).children();

            var mcheckbox_table = $('<ul class="ul-el" />', {
                id: 'mcheckbox-' + id,
                className: 'table table-striped table-bordered dt-responsive nowrap mcheckbox-table'
            }).appendTo(
                mcheckbox_container = $('<div/>', {
                    className: 'mcheckbox-container'
                })
            );



            var outerhtml = `
            <div class="multiselect-search">
                <input type="text" class="form-control" id="searchInput" aria-describedby="Search"
                placeholder="Search Names">

                <div class="btn-li-items">
                <p><span id="selected-check">Selected Items : 0</span> of <span id="visibleNum">0</span></p>
                <button type="button" class="btn btn-info checkall">Toggle Select</button>
                </div>
                ${mcheckbox_table}
            </div>`;

            options.each(function (index, option) {
                var value = $(option).attr('value'),
                    label = $(option).text(),
                    selected = $(option).attr('selected');


                var checkbox_row = $(
                    `<li class="list-items">
                  <label for="${name}_${value}" class="mcheckbox-label">
                    <input type="checkbox" id="${name}_${value}" class="check" name="${name}" value="${value}"  ${(selected ? 'checked="checked"' : '')}/><span>${label}</span>
                  </label>
                 </li>`
                ).appendTo(mcheckbox_table);


            })

            mcheckbox_container.insertAfter(item);

            try {
                mcheckbox_container.resizable({ handles: "se" });
            }
            catch (e) {
                // resizing not supported
                // console.log('resizing not supported');
            }

            $(item).nextAll('.help').hide();
            $(item).remove();

        })

        let ulEl = document.getElementsByClassName("ul-el");
        let searchInput = document.getElementById("searchInput");
        let selectedCheck = document.getElementById("selected-check");
        let visibleNum = document.getElementById("visibleNum")
        let preCheckedOut = [];


        renderUpdatedList = (list) => {
            const parent = ulEl[0]

            Array.from(parent.children).forEach(item => {
                item.classList.add("active");
            })
            list.forEach(item => {
                item.classList.remove("active");
            });

        }

        let checkedOnInputChange = $('.ul-el .list-items input[type="checkbox"]:checked:visible').length;
        selectedCheck.textContent = `Selected Items : ${checkedOnInputChange}`

        jQuery('#searchInput').on('input keyup', function (event) {
            let searchQuery = event.target.value.toLowerCase();
            searchQuery = searchQuery.replaceAll('-', ' ').split(' ').filter(s => s);

            countVisible();

            let checkedOnInputChange = $('.ul-el .list-items input[type="checkbox"]:checked:visible').length;
            selectedCheck.textContent = `Selected Items : ${checkedOnInputChange}`

            let allNamesDOMCollection = $(".ul-el .list-items");
            let result = [];
            let includes;

            for (listRecord of allNamesDOMCollection) {
                let selector = listRecord.querySelector('span')
                let currentName = selector.textContent.toLowerCase().replaceAll("-", " ").split(' ').filter(s => s).join(" ");
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
                    renderUpdatedList(result);
                }

            }

        });


        jQuery.each(preCheckedOut, (arrIndex, arrItem) => {
            $(`.ul-el .list-items input[class="check"][id="${arrItem}"]`).prop('checked', true);
        });

        function countChecked() {
            let preChecked = []
            preCheckedOut = preChecked;
            $(".ul-el .list-items :checkbox").map(function () {
                if (this.checked) {
                    preChecked.push(this.id)
                }
            })
        }

        function countVisible(){
            let visibleItemNumber = $(".ul-el .list-items:visible").length;
            visibleNum.textContent = visibleItemNumber;
        }

        let list = $(".ul-el"),
            origOrderList = list.children();

        list.on("change", ":checkbox", function () {
            let checked = $('.ul-el .list-items input[type="checkbox"]:checked:visible').length;
            if ($(this).is(':checked')) {
                selectedCheck.textContent = `Selected Items : ${checked}`
                // console.log(preCheckedOut)
            } else {
                selectedCheck.textContent = `Selected Items :  ${checked--}`
                // console.log(preCheckedOut)
            }
        })


        function seeCheckedNum() {
            let checked = $('.ul-el .list-items input[type="checkbox"]:checked:visible').length;
            selectedCheck.textContent = `Selected Items : ${checked}`

        }


        $(".ul-el .list-items :checkbox").change(function () {
            countChecked()
        });


        var clicked = false;
        $(".btn-li-items .checkall").on("click", function () {
            $(".ul-el .list-items .check:visible").prop("checked", !clicked);
            clicked = !clicked;
            // this.innerHTML = clicked ? 'Toggle Select' : 'Toggle Select';
            seeCheckedNum();
            countChecked();


        });
        countVisible();
        // setTimeout(function(){ },100);

    };

    // apply the conversion to the desired elements (change the selector)




})(jQuery)
