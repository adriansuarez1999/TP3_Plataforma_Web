import sqlite3

def conectar_db():
    """Establece y retorna la conexión a la base de datos SQLite."""
    return sqlite3.connect("plataforma.db")

def inicializar_base_datos():
    """Crea las tablas iniciales y la tabla de inscripciones si no existen."""
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Tabla Inscripcion (Sprint 3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Inscripcion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_Alumno TEXT NOT NULL,
            ID_Materia INTEGER NOT NULL,
            Fecha TEXT NOT NULL,
            UNIQUE(ID_Alumno, ID_Materia)
        )
    """)
    
    conexion.commit()
    conexion.close()

def registrar_inscripcion(dni_alumno, id_materia):
    """
    Desarrolla la lógica de base de datos para registrar la inscripción.
    Sprint 3 - Tarea 2 (Yancel).
    """
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO Inscripcion (ID_Alumno, ID_Materia, Fecha) VALUES (?, ?, datetime('now'))",
            (dni_alumno, id_materia)
        )
        conexion.commit()
        return True, "Inscripción registrada con éxito."
    except sqlite3.IntegrityError as e:
        conexion.rollback()
        return False, f"Error de integridad (posible duplicado o datos inválidos): {e}"
    except Exception as e:
        conexion.rollback()
        return False, f"Error al registrar inscripción: {e}"
    finally:
        conexion.close()