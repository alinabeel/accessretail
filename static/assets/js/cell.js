// var dt_ajax_url = '{% url "master-setups:code-frame-list-ajax" country_code=global.country_code %}';
$(document).ready(function() {
    let dt_ajax_url = $('#ajax_datatable').attr("url");
    AjaxDatatableViewUtils.initialize_table(
        $('#ajax_datatable'),
        dt_ajax_url,
        common_dt_options,
        {
            data: function() { return $("#frm1").serialize(); },
        }
    );
    renameFilters();
});

function getAPIData() {
    $('#ajax_datatable').DataTable().ajax.reload(null, false);

    var jsonObj = jQFormSerializeArrToJson($("#accordion :input").serializeArray());
    console.log(jsonObj);
    $("#condition_json").val(jsonObj);
}


function renameFilters(){
    $(".or_group").each( function(key,value) {
        //
        var or_group_id = $(this).attr('id').split('_');
        $(this).find("[data-name=cols]").each( function(key,value) {
            $(this).attr("name","field_group[group]["+or_group_id[2]+"][row]["+key+"][cols]")
        });
        $(this).find("[data-name=operator]").each( function(key,value) {
            $(this).attr("name","field_group[group]["+or_group_id[2]+"][row]["+key+"][operator]")
        });
        $(this).find("[data-name=value]").each( function(key,value) {
            $(this).attr("name","field_group[group]["+or_group_id[2]+"][row]["+key+"][value]")
        });
    });
}



$(".or-add, .and-add").click(function(){
    renameFilters();
});

$("#btn_filter").click(function(){
    getAPIData();
});

$( "#frm1 select" ).change(function( event ) {
    $(this).find('option').removeAttr("selected");
});

$( "#frm1" ).submit(function( event ) {
    $(this).find("input").each( function(key,value) {
        $(this).attr("value", $(this).val());
    });

    $(this).find("select").each(function(){
        var value = $(this).val();
        $(this).find('option[value="' + value + '"]').attr("selected", "selected");

    });


    var jsonObj = jQFormSerializeArrToJson($("#accordion :input").serializeArray());
    console.log(jsonObj);
    $("#condition_json").val(jsonObj);


    $("#serialize_str").val($("#frm1").serialize());
    $("#condition_html").val($("#accordion").html());

});

