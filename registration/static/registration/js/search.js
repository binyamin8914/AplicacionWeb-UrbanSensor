$(document).ready(function () {
    // Función para manejar la búsqueda
    function handleSearch() {
        var searchText = $('#searchInput').val().toLowerCase();

        // Oculta todas las filas de la tabla
        $('table tbody tr').hide();

        // Muestra solo las filas que coinciden con la búsqueda
        $('table tbody tr').each(function () {
            var rowText = $(this).text().toLowerCase();
            if (rowText.includes(searchText)) {
                $(this).show();
            }
        });
    }

    // Agrega un evento al cambio del contenido del input de búsqueda
    $('#searchInput').on('input', function () {
        handleSearch();
    });

    // Agrega un evento al hacer clic en el ícono de búsqueda
    $('#searchIcon').on('click', function () {
        handleSearch();
    });
});