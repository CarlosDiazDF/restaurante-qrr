const socket = io();
const listaPendientes = document.getElementById('lista-pedidos');
const listaProcesados = document.getElementById('lista-procesados');
const toast = document.getElementById('toast');

// Escucha pedidos nuevos en tiempo real
socket.on('nuevo_pedido', (data) => {
  mostrarToast(`🆕 Nuevo pedido de ${data.nombre}`);
  agregarPedidoPendiente(data);
});

function agregarPedidoPendiente(pedido) {
  const div = document.createElement('div');
  div.classList.add('pedido', 'fade-in');
  div.dataset.id = pedido.id;
  div.innerHTML = `
    <div class="pedido-header">
      <h3>${pedido.nombre}</h3>
      <span class="tag-pendiente">Pendiente</span>
    </div>
    <p>${pedido.detalles}</p>
    <textarea class="observacion" placeholder="Observación (opcional)"></textarea>
    <div class="acciones">
      <button class="btn btn-entregado">Entregado</button>
      <button class="btn btn-rechazado">Rechazado</button>
    </div>
  `;

  div.querySelector('.btn-entregado').addEventListener('click', () => actualizarEstado(div, 1));
  div.querySelector('.btn-rechazado').addEventListener('click', () => actualizarEstado(div, 2));

  listaPendientes.prepend(div);
}

function actualizarEstado(elemento, estado) {
  const pedidoId = parseInt(elemento.dataset.id);
  const nombre = elemento.querySelector('h3').textContent;
  const detalles = elemento.querySelector('p').textContent;
  const observacion = elemento.querySelector('.observacion').value;

  fetch('/actualizar_estado', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: pedidoId, estado })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "ok") {
      elemento.classList.add('fade-out');
      setTimeout(() => {
        elemento.remove();
        agregarHistorial(nombre, detalles, estado, observacion);
        mostrarToast(
          estado === 1 ? `✅ Pedido de ${nombre} entregado` : `❌ Pedido de ${nombre} rechazado`
        );
      }, 400);
    }
  });
}

function agregarHistorial(nombre, detalles, estado, observacion) {
  const div = document.createElement('div');
  div.classList.add('pedido', 'historial', 'fade-in');
  div.innerHTML = `
    <div class="pedido-header">
      <h3>${nombre}</h3>
      ${
        estado === 1
          ? '<span class="tag-entregado">Entregado</span>'
          : '<span class="tag-rechazado">Rechazado</span>'
      }
    </div>
    <p>${detalles}</p>
    ${observacion ? `<p class="obs"><strong>Nota:</strong> ${observacion}</p>` : ""}
  `;
  listaProcesados.prepend(div);
}

function mostrarToast(mensaje) {
  toast.textContent = mensaje;
  toast.classList.add('mostrar');
  setTimeout(() => toast.classList.remove('mostrar'), 3000);
}
