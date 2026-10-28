"""Sprint 2 - Tarea 2 (Pablo): consultas Back-End de notas.

Esquema esperado (definido en Sprint 2 - Tarea 1, Matías):
    materias(id, nombre)
    notas(id, id_alumno, id_materia, nota, fecha)
Si Matías nombra distinto alguna tabla o columna, ajustar sólo los SQL de abajo.

Estas funciones NO validan el rango de la nota: eso lo hace
validaciones_notas.py (Tarea 3). El controlador debe llamar primero a la
validación y luego a insertar_nota().
"""
import sqlite3
from datetime import date

from models import conectar_db


def insertar_nota(id_alumno, id_materia, nota, fecha=None):
    """Inserta una nota. Devuelve (True, mensaje) o (False, mensaje)."""
    if fecha is None:
        fecha = date.today().isoformat()

    conexion = conectar_db()
    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute(
            """
            INSERT INTO notas (id_alumno, id_materia, nota, fecha)
            VALUES (?, ?, ?, ?)
            """,
            (id_alumno, id_materia, nota, fecha),
        )
        conexion.commit()
        return True, "Nota registrada con éxito."
    except sqlite3.IntegrityError:
        conexion.rollback()
        return False, "El alumno o la materia indicados no existen."
    finally:
        conexion.close()


def obtener_notas_alumno(id_alumno):
    """Devuelve el historial de notas del alumno, de la más reciente a la más antigua.

    Cada elemento es un dict: {"id", "materia", "nota", "fecha"}.
    Si el alumno no tiene notas devuelve una lista vacía.
    """
    conexion = conectar_db()
    try:
        cursor = conexion.execute(
            """
            SELECT n.id, m.nombre, n.nota, n.fecha
            FROM notas n
            JOIN materias m ON m.id = n.id_materia
            WHERE n.id_alumno = ?
            ORDER BY n.fecha DESC, n.id DESC
            """,
            (id_alumno,),
        )
        return [
            {"id": fila[0], "materia": fila[1], "nota": fila[2], "fecha": fila[3]}
            for fila in cursor.fetchall()
        ]
    finally:
        conexion.close()
