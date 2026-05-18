const API = 'http://localhost:5000';
let state = { productos: [], carrito: {} };

// ===== CARGAR PRODUCTOS =====
async function cargarProductos() {
  try {
    const res = await fetch(`${API}/api/productos`);
    state.productos = await res.json();
    mostrarProductos();
  } catch (err) {
    mostrarAlerta('Error al cargar productos: ' + err.message, 'error');
  }
}

// ===== MOSTRAR PRODUCTOS =====
function mostrarProductos() {
  const input = document.getElementById('buscar').value.toLowerCase();
  const filtrados = state.productos.filter(p => 
    p.nombre.toLowerCase().includes(input)
  );
  
  const div = document.getElementById('lista-productos');
  div.innerHTML = '';
  
  filtrados.forEach(p => {
    const card = document.createElement('div');
    card.className = 'producto';
    card.innerHTML = `
      <div class="producto-nombre">${p.nombre}</div>
      <div class="producto-precio">$${p.precio}</div>
      <div class="producto-stock">Stock: ${p.stock_actual}</div>
      <button class="btn-agregar" ${p.stock_actual === 0 ? 'disabled' : ''}>Agregar</button>
    `;
    
    const btn = card.querySelector('.btn-agregar');
    btn.addEventListener('click', () => agregarCarrito(p.id, p.nombre));
    
    div.appendChild(card);
  });
}

// ===== AGREGAR AL CARRITO =====
function agregarCarrito(id, nombre) {
  state.carrito[id] = (state.carrito[id] || 0) + 1;
  mostrarCarrito();
  mostrarAlerta(`✓ ${nombre} agregado`, 'success');
}

// ===== MOSTRAR CARRITO =====
function mostrarCarrito() {
  const div = document.getElementById('items-carrito');
  const ids = Object.keys(state.carrito);
  
  if (ids.length === 0) {
    div.innerHTML = '<div class="carrito-vacio">Carrito vacío</div>';
    document.getElementById('totales').style.display = 'none';
    document.getElementById('finalizar').disabled = true;
    return;
  }
  
  document.getElementById('totales').style.display = 'block';
  document.getElementById('finalizar').disabled = false;
  
  div.innerHTML = '';
  let total = 0;
  
  ids.forEach(id => {
    const p = state.productos.find(x => x.id === parseInt(id));
    const qty = state.carrito[id];
    const subtotal = p.precio * qty;
    total += subtotal;
    
    const item = document.createElement('div');
    item.className = 'carrito-item';
    item.innerHTML = `
      <div class="carrito-item-info">
        <div class="carrito-item-nombre">${p.nombre}</div>
        <div class="carrito-item-qty">
          Cant: <input type="number" min="1" max="${p.stock_actual}" value="${qty}" />
          × $${p.precio}
        </div>
      </div>
      <div class="carrito-item-subtotal">$${subtotal.toFixed(2)}</div>
      <button class="btn-remove">✕</button>
    `;
    
    item.querySelector('input').addEventListener('change', (e) => {
      const val = parseInt(e.target.value);
      if (val > 0 && val <= p.stock_actual) {
        state.carrito[id] = val;
        mostrarCarrito();
      } else {
        e.target.value = qty;
      }
    });
    
    item.querySelector('.btn-remove').addEventListener('click', () => {
      delete state.carrito[id];
      mostrarCarrito();
    });
    
    div.appendChild(item);
  });
  
  document.getElementById('subtotal').textContent = `$${total.toFixed(2)}`;
  document.getElementById('total').textContent = `$${total.toFixed(2)}`;
}

// ===== FINALIZAR VENTA =====
async function finalizarVenta() {
  const ids = Object.keys(state.carrito);
  if (ids.length === 0) {
    mostrarAlerta('Carrito vacío', 'error');
    return;
  }
  
  const items = ids.map(id => ({
    producto_id: parseInt(id),
    cantidad: state.carrito[id]
  }));
  
  const metodo = document.getElementById('metodo_pago').value;
  
  try {
    const res = await fetch(`${API}/api/ventas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metodo_pago: metodo, items })
    });
    
    const data = await res.json();
    
    if (res.ok) {
      mostrarAlerta(`✓ Venta #${data.id} registrada`, 'success');
      state.carrito = {};
      await cargarProductos();
      mostrarCarrito();
    } else {
      mostrarAlerta(`Error: ${data.error}`, 'error');
    }
  } catch (err) {
    mostrarAlerta(`Error: ${err.message}`, 'error');
  }
}

// ===== LIMPIAR CARRITO =====
function limpiarCarrito() {
  if (Object.keys(state.carrito).length === 0) {
    mostrarAlerta('Carrito ya está vacío', 'error');
    return;
  }
  state.carrito = {};
  mostrarCarrito();
  mostrarAlerta('✓ Carrito limpiado', 'success');
}

// ===== MOSTRAR ALERTA =====
function mostrarAlerta(texto, tipo) {
  const div = document.getElementById('mensaje');
  div.textContent = texto;
  div.className = `alerta show ${tipo}`;
  setTimeout(() => {
    div.className = 'alerta';
  }, 3000);
}

// ===== INICIALIZAR =====
document.addEventListener('DOMContentLoaded', () => {
  cargarProductos();
  
  document.getElementById('buscar').addEventListener('input', mostrarProductos);
  document.getElementById('finalizar').addEventListener('click', finalizarVenta);
  document.getElementById('limpiar').addEventListener('click', limpiarCarrito);
});
