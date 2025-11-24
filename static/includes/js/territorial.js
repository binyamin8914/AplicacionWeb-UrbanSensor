document.addEventListener("DOMContentLoaded", function () {
    const perfilSelect = document.getElementById("id_group");
    const direccionContainer = document.getElementById("direccion-container");

    function toggleDireccion() {
        direccionContainer.style.display = (perfilSelect.value === "Territorial")
            ? "block"
            : "none";
    }

    toggleDireccion();
    perfilSelect.addEventListener("change", toggleDireccion);
});
