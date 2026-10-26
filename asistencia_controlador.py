"""Sprint 4 - Tarea 3 (Pablo): agrupación de datos de asistencia.

Recibe lo que manda la Vista (Yancel, Tarea 4) y arma el "paquete" que
consume el Modelo (Matías, Tarea 2: guardar_asistencias).

Contrato con la Vista (formulario HTML):
    <input type="hidden" name="alumnos"   value="<id_alumno>">   (uno por cada inscripto)
    <input type="checkbox" name="presentes" value="<id_alumno>"> (sólo los marcados)

Contrato con el Modelo - el paquete es una lista de tuplas:
    (id_alumno, id_materia, fecha, estado)    estado: "Presente" | "Ausente"
"""
from datetime import date, datetime

ESTADO_PRESENTE = "Presente"
ESTADO_AUSENTE = "Ausente"


def _a_entero(valor):
    return int(str(valor).strip())


def _fecha_valida(fecha):
    if fecha is None:
        return date.today().isoformat()
    try:
        return datetime.strptime(str(fecha).strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.")


def preparar_paquete_asistencia(id_materia, fecha, ids_inscriptos, ids_presentes):
    """Arma la lista de tuplas lista para guardar.

    Todo inscripto que no esté en ids_presentes queda como "Ausente".
    Lanza ValueError si hay datos inválidos o un presente que no está inscripto.
    """
    try:
        id_materia = _a_entero(id_materia)
        inscriptos = [_a_entero(i) for i in ids_inscriptos]
        presentes = {_a_entero(i) for i in ids_presentes}
    except (TypeError, ValueError):
        raise ValueError("Los identificadores de materia y alumnos deben ser números.")

    fecha = _fecha_valida(fecha)

    # quitar repetidos conservando el orden
    inscriptos = list(dict.fromkeys(inscriptos))
    if not inscriptos:
        raise ValueError("No hay alumnos inscriptos para tomar asistencia.")

    desconocidos = presentes - set(inscriptos)
    if desconocidos:
        raise ValueError("Hay alumnos marcados como presentes que no están inscriptos.")

    return [
        (
            id_alumno,
            id_materia,
            fecha,
            ESTADO_PRESENTE if id_alumno in presentes else ESTADO_AUSENTE,
        )
        for id_alumno in inscriptos
    ]


def procesar_formulario_asistencia(form, id_materia, fecha=None):
    """Toma request.form (o cualquier objeto con getlist) y arma el paquete.

    Devuelve (True, paquete) o (False, mensaje_de_error).
    """
    try:
        paquete = preparar_paquete_asistencia(
            id_materia,
            fecha,
            form.getlist("alumnos"),
            form.getlist("presentes"),
        )
    except ValueError as error:
        return False, str(error)
    return True, paquete
