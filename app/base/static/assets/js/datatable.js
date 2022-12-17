

$(document).ready(function () {
    $('#table_processes').DataTable({
      bProcessing: true,
      bServerSide: true,
      sPaginationType: "full_numbers",
      lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
      bjQueryUI: true,
      sAjaxSource: '<API_ENDPOINT>',
      columns: [
        {"data": "Column A"},
        {"data": "Column B"},
        {"data": "Column C"},
        {"data": "Column D"}
      ]
    });
  });
