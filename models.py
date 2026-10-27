import sqlite3
from datetime import date


def conectar_db():
    """Establece y retorna la conexión a la base de datos SQLite."""
    conexion = sqlite3.connect("plataforma.db")
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def insertar_alumno(nombre, apellido, email, DNI, fecha_nacimiento):
    """Registra un alumno en la base de datos."""
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO alumnos
                (nombre, apellido, email, DNI, fecha_nacimiento, activo)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (nombre, apellido, email, DNI, fecha_nacimiento),
        )

        conexion.commit()

        return True, "¡Alumno registrado con éxito!"

    except sqlite3.IntegrityError:
        conexion.rollback()

        return False, "El correo electrónico o DNI ya se encuentra registrado."

    finally:
        conexion.close()


def inicializar_base_datos():
    """
    Crea las estructuras necesarias que ya pertenecen
    a los Sprints integrados.
    """
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS alumnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                email TEXT UNIQUE,
                DNI TEXT UNIQUE,
                fecha_nacimiento TEXT,
                activo INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS materias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                activo INTEGER NOT NULL DEFAULT 1
                    CHECK (activo IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_alumno INTEGER NOT NULL,
                id_materia INTEGER NOT NULL,
                nota REAL NOT NULL
                    CHECK (nota BETWEEN 1 AND 10),
                fecha TEXT NOT NULL DEFAULT CURRENT_DATE,

                FOREIGN KEY (id_alumno)
                    REFERENCES alumnos(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT,

                FOREIGN KEY (id_materia)
                    REFERENCES materias(id)
                    ON UPDATE CASCADE
                    ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS inscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_alumno INTEGER NOT NULL,
                id_materia INTEGER NOT NULL,
                fecha TEXT NOT NULL DEFAULT (date('now')),

                FOREIGN KEY (id_alumno)
                    REFERENCES alumnos(id),

                FOREIGN KEY (id_materia)
                    REFERENCES materias(id)
            );

            CREATE UNIQUE INDEX IF NOT EXISTS
                ux_inscripcion_alumno_materia
                ON inscripciones (id_alumno, id_materia);
            """)

        conexion.commit()

    finally:
        conexion.close()


def registrar_inscripcion(dni_alumno, id_materia):
    """
    Registra la inscripción de un alumno a una materia.

    Recibe el DNI del alumno, busca su ID interno
    y guarda ese ID en la tabla inscripciones.
    """
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        fila_alumno = cursor.execute(
            """
            SELECT id
            FROM alumnos
            WHERE DNI = ?
              AND activo = 1
            """,
            (str(dni_alumno).strip(),),
        ).fetchone()

        if fila_alumno is None:
            return (False, "No existe un alumno activo con el DNI indicado.")

        try:
            id_materia = int(id_materia)

        except (TypeError, ValueError):
            return False, "La materia indicada no es válida."

        fila_materia = cursor.execute(
            """
            SELECT id
            FROM materias
            WHERE id = ?
            """,
            (id_materia,),
        ).fetchone()

        if fila_materia is None:
            return False, "La materia indicada no existe."

        cursor.execute(
            """
            INSERT INTO inscripciones
                (id_alumno, id_materia, fecha)
            VALUES (?, ?, ?)
            """,
            (fila_alumno[0], id_materia, date.today().isoformat()),
        )

        conexion.commit()

        return True, "Inscripción registrada con éxito."

    except sqlite3.IntegrityError:
        conexion.rollback()

        return (False, "El alumno ya se encuentra inscripto en esa materia.")

    except sqlite3.Error as error:
        conexion.rollback()

        return (False, f"No se pudo registrar la inscripción: {error}")

    finally:
        conexion.close()


def guardar_asistencias(paquete):
    """
    Guarda una lista completa de asistencias
    en una única transacción.
    """
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.executemany(
            """
            INSERT INTO asistencias
                (id_alumno, id_materia, fecha, estado)
            VALUES (?, ?, ?, ?)
            """,
            paquete,
        )

        conexion.commit()

        return True, "Asistencias guardadas correctamente."

    except sqlite3.Error as error:
        conexion.rollback()

        return (False, f"No se pudieron guardar las asistencias: {error}")

    finally:
        conexion.close()
