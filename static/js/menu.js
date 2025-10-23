document.addEventListener('DOMContentLoaded', () => {
  const pedido = [];
  const detallesEl = document.querySelector('textarea[name="detalles"]');

  function actualizarPedido() {
    detallesEl.value = pedido.join(' | ');
  }

  document.querySelectorAll('.item button').forEach(boton => {
    boton.addEventListener('click', () => {
      const item = boton.closest('.item');
      const nombre = item.querySelector('h3')?.textContent || '';
      const termino = item.querySelector('select')?.value || '';
      const extra = item.querySelector('input[type="text"]')?.value || '';

      if (item.querySelector('select') && (!termino || termino === 'Seleccionar término')) {
        alert(`⚠️ Debes seleccionar un término de cocción para ${nombre}`);
        return;
      }

      let texto = nombre;
      if (termino) texto += ` (${termino})`;
      if (extra) texto += ` - ${extra}`;

      pedido.push(texto);
      actualizarPedido();

      // Resetear campos después de agregar
      if (item.querySelector('select')) item.querySelector('select').selectedIndex = 0;
      if (item.querySelector('input[type="text"]')) item.querySelector('input[type="text"]').value = '';
    });
  });

  // Enviar pedido al backend
  document.getElementById('pedidoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (pedido.length === 0) {
      alert('Agrega al menos un producto antes de enviar el pedido.');
      return;
    }

    const formData = new FormData(e.target);
    formData.set('detalles', pedido.join(' | '));

    await fetch('/pedido', {
      method: 'POST',
      body: formData
    });

    alert('✅ Pedido enviado a cocina');
    e.target.reset();
    pedido.length = 0;
    actualizarPedido();
  });
});
