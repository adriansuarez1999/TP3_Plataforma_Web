"""Sprint 4 - Tarea 5 (Facundo): pruebas de persistencia de asistencia.

Cargar asistencia -> cerrar -> reabrir -> verificar que SQLite conserve los datos.

Supuestos (acordados con el resto del equipo):
  - models.guardar_asistencias(paquete) (Matías, Tarea 2) guarda toda la lista
    en una sola transacción. paquete = [(id_alumno, id_materia, fecha, estado), ...]
  - Tabla asistencias(id, id_alumno, id_materia, fecha, estado) (Adrián, Tarea 1).
    Acá se crea una versión mínima equivalente; ajustar si el esquema real difiere.
  - asistencia_controlador.py es el de Pablo (Tarea 3).

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
from asistencia_controlador import preparar_paquete_asistencia  # noqa: E402

ESQUEMA = """
CREATE TABLE asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('Presente', 'Ausente'))
);
"""

PAQUETE = [
    (1, 10, "2026-10-24", "Presente"),
    (2, 10, "2026-10-24", "Ausente"),
    (3, 10, "2026-10-24", "Presente"),
]


class TestPersistenciaAsistencia(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta_db = os.path.join(self.carpeta.name, "prueba.db")
        con = sqlite3.connect(self.ruta_db)
        con.executescript(ESQUEMA)
        con.close()

        patcher = mock.patch.object(
            models, "conectar_db", lambda: sqlite3.connect(self.ruta_db)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.carpeta.cleanup)

    def _leer(self):
        """Abre una conexión NUEVA (simula cerrar y reabrir la aplicación)."""
        con = sqlite3.connect(self.ruta_db)
        try:
            return con.execute(
                "SELECT id_alumno, id_materia, fecha, estado "
                "FROM asistencias ORDER BY id_alumno"
            ).fetchall()
        finally:
            con.close()

    def test_los_datos_se_conservan_al_reabrir(self):
        models.guardar_asistencias(PAQUETE)
        self.assertEqual(self._leer(), PAQUETE)

    def test_el_archivo_db_conserva_los_datos_en_otro_proceso(self):
        import subprocess

        models.guardar_asistencias(PAQUETE)
        codigo = (
            "import sqlite3,sys;"
            "c=sqlite3.connect(sys.argv[1]);"
            "print(c.execute('SELECT COUNT(*) FROM asistencias').fetchone()[0])"
        )
        salida = subprocess.run(
            [sys.executable, "-c", codigo, self.ruta_db],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(salida.stdout.strip(), str(len(PAQUETE)))

    def test_guardado_en_una_sola_transaccion(self):
        paquete_roto = PAQUETE + [(None, 10, "2026-10-24", "Presente")]
        try:
            models.guardar_asistencias(paquete_roto)
        except Exception:
            pass  # puede devolver (False, msg) o lanzar: lo importante es no dejar datos parciales
        self.assertEqual(self._leer(), [])

    def test_guardar_dos_veces_acumula_registros(self):
        models.guardar_asistencias(PAQUETE)
        models.guardar_asistencias(
            [(1, 10, "2026-10-25", "Ausente"), (2, 10, "2026-10-25", "Presente")]
        )
        self.assertEqual(len(self._leer()), 5)

    def test_flujo_completo_controlador_modelo_bd(self):
        paquete = preparar_paquete_asistencia(10, "2026-10-24", [1, 2, 3], [1, 3])
        models.guardar_asistencias(paquete)
        self.assertEqual(self._leer(), PAQUETE)


if __name__ == "__main__":
    unittest.main()
