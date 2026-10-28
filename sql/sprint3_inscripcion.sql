-- Sprint 3 - Tarea 1 (Facundo): tabla intermedia Inscripcion
-- Relación muchos a muchos entre alumnos y materias.
-- Requiere las tablas alumnos (Sprint 1) y materias (Sprint 2 - Tarea 1).

CREATE TABLE IF NOT EXISTS inscripciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    fecha TEXT NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (id_alumno) REFERENCES alumnos(id),
    FOREIGN KEY (id_materia) REFERENCES materias(id)
);

-- Red de seguridad en la BD: un alumno no puede inscribirse dos veces
-- a la misma materia (complementa la validación de la Tarea 3).
CREATE UNIQUE INDEX IF NOT EXISTS ux_inscripcion_alumno_materia
    ON inscripciones (id_alumno, id_materia);
