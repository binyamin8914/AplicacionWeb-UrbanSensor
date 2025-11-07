document.addEventListener('DOMContentLoaded', () => {
    const botonToggle = document.getElementById('toggle_btn')
    const sidebar = document.getElementById('sidebar')
    console.log(localStorage.getItem('sbEstaContraido'))

    if (!localStorage.getItem('sbEstaContraido')) {
        localStorage.setItem('sbEstaContraido', 'true')
    }

    if (localStorage.getItem('sbEstaContraido') == 'false') {
        sidebar.classList.remove('contraido')
    }

    botonToggle.addEventListener('click', () => {
        localStorage.setItem('sbEstaContraido', !(localStorage.getItem('sbEstaContraido') == 'true')) // toggle
        sidebar.classList.toggle('contraido')
    })
})