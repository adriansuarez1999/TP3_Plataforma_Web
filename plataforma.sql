-- SQLite
PRAGMA foreign_keys = ON;

-- Creamos la tabla alumnos
CREATE TABLE IF NOT EXISTS alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT UNIQUE,
    DNI TEXT UNIQUE,
    fecha_nacimiento TEXT,
    activo INTEGER DEFAULT 1
);

-- Creamos la tabla materias
CREATE TABLE IF NOT EXISTS materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    activo INTEGER NOT NULL DEFAULT 1
        CHECK (activo IN (0, 1))
);

-- Creamos la tabla notas
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    nota REAL NOT NULL
        CHECK (nota BETWEEN 1 AND 10),
    fecha TEXT NOT NULL DEFAULT CURRENT_DATE,

    FOREIGN KEY (id_alumno) REFERENCES alumnos(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (id_materia) REFERENCES materias(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Insertamos algunos datos de prueba
INSERT INTO alumnos (nombre, apellido, email, DNI, fecha_nacimiento, activo) VALUES 
('Juan', 'Pérez', 'juan.perez@email.com', '12345678A', '2000-05-15', 1),
('María', 'Gómez', 'maria.gomez@email.com', '87654321B', '2001-08-22', 1),
('Carlos', 'López', 'carlos.lopez@email.com', '11223344C', '1999-12-10', 0);




/* -- 1. Verificá que los datos se insertaron bien
SELECT * FROM alumnos;

-- 2. Probá filtrar por un campo (ej: buscar los alumnos activos)
SELECT nombre, apellido FROM alumnos WHERE activo = 1;

-- 3. Probá insertar un alumno nuevo para ver si el autoincremental (id) y el email único funcionan
INSERT INTO alumnos (nombre, apellido, email, DNI, fecha_nacimiento, activo) 
VALUES ('Sofía', 'Martínez', 'sofia.martinez@email.com', '55667788D', '2002-03-11', 1);

-- 4. Volvé a consultar todos para confirmar que se agregó el nuevo
SELECT * FROM alumnos; */
