// import DataTable from './datatables.net-dt';
// import './datatables.net-responsive-dt';

let table = new DataTable('#sortableTable', {
    responsive: true
});

$(document).ready( function () {
    $('#sortableTable').DataTable();
} );
