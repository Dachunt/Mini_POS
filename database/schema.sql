CREATE DATABASE IF NOT EXISTS pos_inventario;
USE pos_inventario;

-- Tabla de productos con índices
CREATE TABLE IF NOT EXISTS producto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre),
    INDEX idx_stock (stock_actual)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de ventas con índices
CREATE TABLE IF NOT EXISTS venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia') NOT NULL,
    total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_metodo_pago (metodo_pago)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de detalles de venta con índices y foreign keys
CREATE TABLE IF NOT EXISTS detalle_venta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES venta(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto(id),
    INDEX idx_venta_id (venta_id),
    INDEX idx_producto_id (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar datos de ejemplo
INSERT INTO producto (nombre, precio, stock_actual) VALUES
('Coca-Cola 355ml', 15.50, 100),
('Sabritas Original 45g', 18.00, 80),
('Galletas Oreo 90g', 22.50, 60),
('Agua Bonafont 1L', 12.00, 120),
('Pan Bimbo Blanco 680g', 45.00, 30),
('Leche Lala Entera 1L', 26.50, 50),
('Huevo San Juan 12pz', 38.00, 40),
('Arroz SOS 1kg', 28.00, 35),
('Frijoles La Sierra 420g', 25.50, 45),
('Aceite Nutrioli 946ml', 42.00, 25);

