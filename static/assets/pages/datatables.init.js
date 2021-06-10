var dt_language = {
    "emptyTable":     "No data available in table",
    "info":           "Showing _START_ to _END_ of _TOTAL_ entries",
    "infoEmpty":      "Showing 0 to 0 of 0 entries",
    "infoFiltered":   "(filtered from _MAX_ total entries)",
    "infoPostFix":    "",
    "thousands":      ",",
    "lengthMenu":     "Show _MENU_ entries",
    "loadingRecords": "Loading...",
    "processing":     "Processing...",
    "search":         "Search:",
    "zeroRecords":    "No matching records found",
    "paginate": {
        "first":      "First",
        "last":       "Last",
        "next":       "Next",
        "previous":   "Previous"
    },
    "aria": {
        "sortAscending":  ": activate to sort column ascending",
        "sortDescending": ": activate to sort column descending"
    }
}

$(document).ready(function() {
    $('#datatable').DataTable();

    //Buttons examples
    var table = $('#datatable-buttons').DataTable({
        lengthChange: false,
        buttons: ['copy', 'excel','csvHtml5','pdf']
    });

    table.buttons().container()
        .appendTo('#datatable-buttons_wrapper .col-md-6:eq(0)');
} );

// $(document).ready(function() {
//     $('#datatable').DataTable();

//     //Buttons examples
//     var table = $('#datatable-buttons').DataTable({
//         lengthChange: false,
//         buttons: [
//         'colvis',
//         'copyHtml5',
//         'csvHtml5',
//         'excelHtml5',
//         'pdfHtml5',
//         'print'
//         ]
//     });

//     table.buttons().container()
//         .appendTo('#datatable-buttons_wrapper .col-md-6:eq(0)');
// } );