
function mostrarModal(elemento) {
    // Obtiene el ID
    var elementId = $(elemento).data('element-id');
    // Pasa el ID al modal
    $('#myModal').data('element-id', elementId);
    // Muestra el modal
    $('#myModal').modal('show');
    // Actualiza la URL del botón Bloquear con el ID de la encuesta
    var blockUrl = baseUrl.replace('0', elementId.toString());
    console.log('URL de bloqueo al hacer clic:', blockUrl);
    $('#blockButton').attr('href', blockUrl);
}

$(document).ready(function () {
    $('#myModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var elementId = button.data('element-id');
        var modal = $(this);

        // Verifica que elementId tenga un valor
        if (elementId !== undefined) {
            // Actualiza la URL del botón Bloquear con el ID
            var blockUrl = baseUrl.replace('0', elementId.toString());
            console.log('URL de bloqueo al hacer clic:', blockUrl);
            modal.find('#blockButton').attr('href', blockUrl);
        }
    });
});