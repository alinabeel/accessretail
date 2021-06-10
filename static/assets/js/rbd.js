
    var send_data = {}
    $(document).ready(function() {
        getAPIData();
        renameFilters();
        if($('#id_rbd').length){
            $('#id_rbd').change(function(){
                getAPIData();
            });
        }
    });

    function putTableData(result) {
        // creating table row for each result and
        // pushing to the html cntent of table body of listing table
        let row;
        if(result["results"].length > 0){
            $("#no_results").hide();
            $("#list_data").show();
            $("#listing").html("");
            let tr_index = 0;
            $.each(result["results"], function (a, b) {
                row = '<tr>';

                if(tr_index==0){
                    row +=  '<tr>';
                    $.each(b, function (aa, bb) {
                        row += '<th data-field="'+ aa +'"">' + ucword(aa) + '</th>';
                    });
                    row +=  '</tr>';
                }


                $.each(b, function (aa, bb) {
                    if(isObject(bb)){
                        value = (bb.code)?bb.code:bb;
                    }else{
                        value = bb
                    }
                    row += "<td title=\"" + value + "\">" + value + "</td>";

                });

                row += '</tr>';
                tr_index++;
                $("#listing").append(row);
            });
        }
        else{
            // if no result found for the given filter, then display no result
            $("#no_results h5").html("No results found");
            $("#list_data").hide();
            $("#no_results").show();
        }
        // setting previous and next page url for the given result
        let prev_url = result["previous"];
        let next_url = result["next"];
        // disabling-enabling button depending on existence of next/prev page.
        if (prev_url === null) {
            $("#previous").addClass("disabled");
            $("#previous").prop('disabled', true);
        } else {
            $("#previous").removeClass("disabled");
            $("#previous").prop('disabled', false);
        }
        if (next_url === null) {
            $("#next").addClass("disabled");
            $("#next").prop('disabled', true);
        } else {
            $("#next").removeClass("disabled");
            $("#next").prop('disabled', false);
        }
        // setting the url
        $("#previous").attr("url", result["previous"]);
        $("#next").attr("url", result["next"]);
        // displaying result count
        $("#result-count span").html(result["count"]);
    }

    function getAPIData() {
        let url = $('#list_data').attr("url")
        var datastring = $("#frm1").serialize();

        $.ajax({
            method: 'GET',
            url: url,
            data: datastring,
            beforeSend: function(){
                $("#no_results h5").html("Loading data...");
            },
            success: function (result) {
                putTableData(result);
            },
            error: function (response) {
                $("#no_results h5").html("Something went wrong");
                $("#list_data").hide();
            }
        });
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

    $("#next").click(function () {
        let url = $(this).attr("url");
        if (!url)
            $(this).prop('all', true);

        $(this).prop('all', false);
        $.ajax({
            method: 'GET',
            url: url,
            success: function (result) {
                putTableData(result);
            },
            error: function(response){
                console.log(response)
            }
        });
    });

    $("#previous").click(function () {
        let url = $(this).attr("url");
        if (!url)
            $(this).prop('all', true);

        $(this).prop('all', false);
        $.ajax({
            method: 'GET',
            url: url,
            success: function (result) {
                putTableData(result);
            },
            error: function(response){
                console.log(response)
            }
        });
    });


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
        $("#serialize_str").val($("#frm1").serialize());
        $("#condition_html").val($("#accordion").html());

    });
