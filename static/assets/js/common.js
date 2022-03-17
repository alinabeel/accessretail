function getCookie(name) {
    var cookieValue = null;
    var value = '; ' + document.cookie,
        parts = value.split('; ' + name + '=');
    if (parts.length == 2) cookieValue = parts.pop().split(';').shift();
    return cookieValue;
}

function getCSRFToken() {
    var csrftoken = getCookie('csrftoken');
    if (csrftoken == null) {
        csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    }
    return csrftoken;
}

function newexportaction(e, dt, button, config) {
    console.log(dt);
    var self = this;
    var oldStart = dt.settings()[0]._iDisplayStart;
    dt.one('preXhr', function (e, s, data) {
        // Just this once, load all data from the server...
        data.start = 0;
        data.length = 2147483647;
        dt.one('preDraw', function (e, settings) {
            // Call the original action function
            if (button[0].className.indexOf('buttons-copy') >= 0) {
                $.fn.dataTable.ext.buttons.copyHtml5.action.call(self, e, dt, button, config);
            } else if (button[0].className.indexOf('buttons-excel') >= 0) {
                $.fn.dataTable.ext.buttons.excelHtml5.available(dt, config) ?
                    $.fn.dataTable.ext.buttons.excelHtml5.action.call(self, e, dt, button, config) :
                    $.fn.dataTable.ext.buttons.excelFlash.action.call(self, e, dt, button, config);
            } else if (button[0].className.indexOf('buttons-csv') >= 0) {
                $.fn.dataTable.ext.buttons.csvHtml5.available(dt, config) ?
                    $.fn.dataTable.ext.buttons.csvHtml5.action.call(self, e, dt, button, config) :
                    $.fn.dataTable.ext.buttons.csvFlash.action.call(self, e, dt, button, config);
            } else if (button[0].className.indexOf('buttons-pdf') >= 0) {
                $.fn.dataTable.ext.buttons.pdfHtml5.available(dt, config) ?
                    $.fn.dataTable.ext.buttons.pdfHtml5.action.call(self, e, dt, button, config) :
                    $.fn.dataTable.ext.buttons.pdfFlash.action.call(self, e, dt, button, config);
            } else if (button[0].className.indexOf('buttons-print') >= 0) {
                $.fn.dataTable.ext.buttons.print.action(e, dt, button, config);
            }
            dt.one('preXhr', function (e, s, data) {
                // DataTables thinks the first item displayed is index 0, but we're not drawing that.
                // Set the property to what it was before exporting.
                settings._iDisplayStart = oldStart;
                data.start = oldStart;
            });
            // Reload the grid with the original page. Otherwise, API functions like table.cell(this) don't work properly.
            setTimeout(dt.ajax.reload, 0);
            // Prevent rendering of the full data to the DOM
            return false;
        });
    });
    // Requery the server with the new one-time export settings
    dt.ajax.reload();
}


var common_dt_options = {
    processing: true,
    autoWidth: true,
    full_row_select: false,
    scrollX: true,
    dom: 'Bfr<t>lip',
    buttons: [
        {
            "extend": 'csv',
            "text": 'CSV Export',
            "titleAttr": 'CSV Export',
            "action": newexportaction
        },
    ],

};

function ucword(words) {
    var separateWord = words.toLowerCase().split('_');
    for (var i = 0; i < separateWord.length; i++) {
        separateWord[i] = separateWord[i].charAt(0).toUpperCase() +
        separateWord[i].substring(1);
    }
    return separateWord.join(' ');
}

function isObject(obj) {
    return obj !== null && typeof obj === 'object';
}


function stripSlashes(str){
    return str.toString().replace(/\\(.)/mg, "$1");
}


function jQFormSerializeArrToJson(formSerializeArr){
    var jsonObj = {};
    jQuery.map( formSerializeArr, function( n, i ) {
        jsonObj[n.name] = n.value;
    });

    return JSON.stringify(jsonObj);
   }

