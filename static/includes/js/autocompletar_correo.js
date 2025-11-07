// Este script autocompleta el correo del encargado en cualquier formulario que tenga:
// - Un select con id "encargado" y opciones con data-correo
// - Un input con name "correo_encargado"

document.addEventListener("DOMContentLoaded", function() {
    var encargadoSelect = document.getElementById('encargado');
    var correoInput = document.querySelector('input[name="correo_encargado"]');
    if (encargadoSelect && correoInput) {
        encargadoSelect.addEventListener('change', function() {
            var correo = this.options[this.selectedIndex].getAttribute('data-correo');
            correoInput.value = correo || '';
        });
        // Si hay encargado seleccionado al cargar la página (edición)
        if(encargadoSelect.value) {
            var selectedOption = encargadoSelect.options[encargadoSelect.selectedIndex];
            var correo = selectedOption.getAttribute('data-correo');
            if(correo) correoInput.value = correo;
        }
    }
});