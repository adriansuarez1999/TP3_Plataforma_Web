import sqlite3


def conectar_db():
  return sqlite3.connect("plataforma.db")


def insertar_alumno(nombre, apellido, email, DNI, fecha_nacimiento):
  conexion = conectar_db()
  cursor = conexion.cursor()
  try:
    cursor.execute(
        """
            INSERT INTO alumnos (nombre, apellido, email, DNI, fecha_nacimiento, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        """,
        (nombre, apellido, email, DNI, fecha_nacimiento),
    )
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