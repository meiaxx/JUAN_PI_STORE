-- Crea la DB juan_pi;
CREATE database IF NOT EXISTS juan_pi;

-- Entra en ella
USE juan_pi;

-- Crea la tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phonenumber VARCHAR(15) NOT NULL,
    address VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Crea la tabla productos
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    imagen VARCHAR(255) NOT NULL
);


-- crea la table de el detalle de la compra
CREATE TABLE IF NOT EXISTS detalle_compra (
    usuario_id INT,
    producto_id INT,
    nombre_producto VARCHAR(255),
    cantidad INT,
    precio DECIMAL(10, 2),
    PRIMARY KEY (usuario_id, producto_id)
);

-- Crea la table de pedidos
CREATE TABLE IF NOT EXISTS order_buy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    correo VARCHAR(255) NOT NULL,
    ubicacion VARCHAR(255) NOT NULL,
    codigo_postal VARCHAR(10) NOT NULL,
    numero_telefono VARCHAR(20) NOT NULL,
    se_envia BOOLEAN NOT NULL DEFAULT FALSE,
    cantidad_total DECIMAL(10, 2) NOT NULL
);

-- crea una table para el Usuario Administrador
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL
);
