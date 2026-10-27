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
    return True, "¡Alumno registrado con éxito!"
  except sqlite3.IntegrityError:
    return False, "El correo electrónico ya se encuentra registrado."
  finally:
    conexion.close()


def guardar_asistencias(paquete):
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.executemany(
            """
            INSERT INTO asistencias (id_alumno, id_materia, fecha, estado)
            VALUES (?, ?, ?, ?)
            """,
            paquete,
        )

        conexion.commit()
        return True, "Asistencias guardadas correctamente."

    except sqlite3.Error as error:
        conexion.rollback()
        return False, f"No se pudieron guardar las asistencias: {error}"

    finally:
        conexion.close()