// static/js/incidencias_campos.js
// Maneja la carga dinámica de "campos adicionales" en el formulario de incidencia.
// Requisitos del template:
// - Un <select name="encuesta"> presente
// - Un contenedor con id="campos-adicionales-container"
// - Un script tag json (opcional) con id pasado en data-prefill-id (ver template)
// - Atributo data-api-template en el script tag que apunta a la URL de la API con placeholder 0:
//     e.g. data-api-template="/incidencias/api/campos_encuesta/0/"
// - El script se carga con defer

(function () {
  'use strict';

  // Helper: parse JSON from a script tag created by Django json_script (si existe)
  function loadPrefill(prefillId) {
    if (!prefillId) return {};
    const el = document.getElementById(prefillId);
    if (!el) return {};
    try {
      return JSON.parse(el.textContent || '{}');
    } catch (err) {
      console.warn('incidencias_campos: error parsing prefill JSON', err);
      return {};
    }
  }

  // Render simple text inputs for campos (campos: [{id, titulo, es_obligatoria}])
  function renderCampos(container, campos, prefill) {
    container.innerHTML = '';
    if (!campos || campos.length === 0) return;
    campos.forEach(function (c) {
      const div = document.createElement('div');
      div.className = 'mb-3';
      div.dataset.campoId = c.id;

      const label = document.createElement('label');
      label.className = 'form-label';
      label.textContent = c.titulo + (c.es_obligatoria ? ' *' : '');
      label.htmlFor = 'campo_' + c.id;

      let input;
      // por ahora texto simple; si más adelante soportas tipos, varía aquí
      input = document.createElement('input');
      input.type = 'text';
      input.name = 'campo_' + c.id;
      input.id = 'campo_' + c.id;
      input.className = 'form-control';
      if (prefill && prefill[c.id] !== undefined && prefill[c.id] !== null) {
        input.value = prefill[c.id];
      } else if (c.valor) {
        input.value = c.valor;
      } else {
        input.value = '';
      }

      div.appendChild(label);
      div.appendChild(input);
      container.appendChild(div);
    });
  }

  // Fetch campos desde endpoint y renderiza
  async function fetchYRender(apiTemplate, encuestaId, container, prefill) {
    if (!encuestaId) {
      container.innerHTML = '';
      return;
    }
    const url = apiTemplate.replace('/0/', '/' + encodeURIComponent(encuestaId) + '/');
    try {
      const resp = await fetch(url, {
        headers: {
          'Accept': 'application/json'
        },
        credentials: 'same-origin'
      });
      if (!resp.ok) throw new Error('Network response not ok: ' + resp.status);
      const data = await resp.json();
      // data.campos expected: [{id, titulo, es_obligatoria}, ...]
      renderCampos(container, data.campos || [], prefill || {});
    } catch (err) {
      console.error('incidencias_campos: no se pudieron cargar los campos adicionales', err);
      // leave container as-is (server-side rendered fields remain)
    }
  }

  // Init: lee atributos del script tag que carga este fichero
  function init() {
    // document.currentScript puede ser null si bundling; fallback a querySelector por data attribute
    const current = document.currentScript || document.querySelector('script[data-api-template][data-prefill-id]');
    if (!current) {
      return;
    }
    const apiTemplate = current.dataset.apiTemplate; // e.g. "/incidencias/api/campos_encuesta/0/"
    const prefillId = current.dataset.prefillId;     // e.g. "prefill-data" (JSON script id)
    const encuestaSelector = current.dataset.encuestaSelector || 'select[name="encuesta"]';
    const containerSelector = current.dataset.containerSelector || '#campos-adicionales-container';

    const encuestaSelect = document.querySelector(encuestaSelector);
    const container = document.querySelector(containerSelector);
    const prefill = loadPrefill(prefillId);

    if (!container || !apiTemplate) {
      console.warn('incidencias_campos: container o apiTemplate no definidos');
      return;
    }

    // Si hay un valor inicial en el select y el container está vacío
    if (encuestaSelect && encuestaSelect.value && container.children.length === 0) {
      // Cargamos campos vía API para UX (si no estaban server-side)
      fetchYRender(apiTemplate, encuestaSelect.value, container, prefill);
    }

    if (encuestaSelect) {
      encuestaSelect.addEventListener('change', function (e) {
        fetchYRender(apiTemplate, this.value, container, prefill);
      });
    }
  }

  // Iniciar cuando DOM listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();