"""Sprint 3 - Tarea 5 (Pablo): pruebas de inscripción.

Verifica el alta correcta en la BD y el bloqueo de inscripciones duplicadas.

Supuestos (acordados con el resto del equipo):
  - registrar_inscripcion(dni_alumno, id_materia) está en models.py
    (Yancel, Tarea 2) y devuelve (True/False, mensaje).
  - La tabla inscripciones sale de sql/sprint3_inscripcion.sql (Facundo, Tarea 1).
  - materias(id, nombre) es la de Sprint 2 - Tarea 1 (acá se crea mínima).

Ejecutar desde la raíz del repo:
    python -m unittest discover -s tests -v
"""
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import models  # noqa: E402

SQL_INSCRIPCION = os.path.join(RAIZ, "sql", "sprint3_inscripcion.sql")

ESQUEMA_BASE = """
CREATE TABLE alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT UNIQUE,
    DNI TEXT UNIQUE,
    fecha_nacimiento TEXT,
    activo INTEGER DEFAULT 1
);
CREATE TABLE materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
INSERT INTO alumnos (nombre, apellido, email, DNI, fecha_nacimiento)
VALUES ('Juan', 'Pérez', 'juan@email.com', '11111111', '2000-01-01'),
       ('María', 'Gómez', 'maria@email.com', '22222222', '2001-02-02');
INSERT INTO materias (nombre) VALUES ('Programación'), ('Base de Datos');
"""


class TestInscripcion(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta_db = os.path.join(self.carpeta.name, "prueba.db")

        con = sqlite3.connect(self.ruta_db)
        con.executescript(ESQUEMA_BASE)
        with open(SQL_INSCRIPCION, encoding="utf-8") as f:
            con.executescript(f.read())
        con.commit()
        con.close()

        patcher = mock.patch.object(
            models, "conectar_db", lambda: sqlite3.connect(self.ruta_db)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.carpeta.cleanup)

    def _filas(self):
        con = sqlite3.connect(self.ruta_db)
        try:
            return con.execute(
                "SELECT id_alumno, id_materia, fecha FROM inscripciones"
            ).fetchall()
        finally:
            con.close()

    def test_alta_correcta_se_guarda_en_la_bd(self):
        ok, _ = models.registrar_inscripcion("11111111", 1)
        self.assertTrue(ok)
        filas = self._filas()
        self.assertEqual(len(filas), 1)
        self.assertEqual((filas[0][0], filas[0][1]), (1, 1))
        self.assertTrue(filas[0][2])  # la fecha se registró

    def test_inscripcion_duplicada_es_bloqueada(self):
        self.assertTrue(models.registrar_inscripcion("11111111", 1)[0])
        ok, mensaje = models.registrar_inscripcion("11111111", 1)
        self.assertFalse(ok)
        self.assertTrue(mensaje)
        self.assertEqual(len(self._filas()), 1)

    def test_otro_alumno_puede_inscribirse_a_la_misma_materia(self):
        self.assertTrue(models.registrar_inscripcion("11111111", 1)[0])
        self.assertTrue(models.registrar_inscripcion("22222222", 1)[0])
        self.assertEqual(len(self._filas()), 2)

    def test_mismo_alumno_puede_inscribirse_a_otra_materia(self):
        self.assertTrue(models.registrar_inscripcion("11111111", 1)[0])
        self.assertTrue(models.registrar_inscripcion("11111111", 2)[0])
        self.assertEqual(len(self._filas()), 2)

    def test_dni_inexistente_no_inscribe(self):
        ok, _ = models.registrar_inscripcion("99999999", 1)
        self.assertFalse(ok)
        self.assertEqual(self._filas(), [])

    def test_materia_inexistente_no_inscribe(self):
        ok, _ = models.registrar_inscripcion("11111111", 999)
        self.assertFalse(ok)
        self.assertEqual(self._filas(), [])

    def test_la_bd_rechaza_duplicados_aunque_falle_la_validacion(self):
        con = sqlite3.connect(self.ruta_db)
        try:
            con.execute(
                "INSERT INTO inscripciones (id_alumno, id_materia) VALUES (1, 1)"
            )
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute(
                    "INSERT INTO inscripciones (id_alumno, id_materia) VALUES (1, 1)"
                )
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
