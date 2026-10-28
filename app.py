import re

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from models import (
    conectar_db,
    guardar_asistencias,
    insertar_alumno,
    inicializar_base_datos,
    registrar_inscripcion,
)

from asistencia_controlador import (
    procesar_formulario_asistencia,
)

from notas_consultas import insertar_nota

from validaciones_notas import (
    evaluar_nota,
)

app = Flask(__name__)

app.secret_key = "clave_secreta_para_flash"


# =========================================================
# INICIALIZACIÓN
# =========================================================

inicializar_base_datos()


# =========================================================
# SPRINT 1 - REGISTRO DE ALUMNOS
# =========================================================


@app.route("/", methods=["GET", "POST"])
def registrar():

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()

        apellido = request.form.get("apellido", "").strip()

        email = request.form.get("email", "").strip()

        DNI = request.form.get("DNI", "").strip()

        fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()

        # =================================================
        # VALIDACIONES
        # =================================================

        if not nombre or not apellido or not email or not DNI or not fecha_nacimiento:

            flash("Todos los campos son obligatorios.", "error")

            return redirect(url_for("registrar"))

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(email_regex, email):

            flash("El formato del correo electrónico no es válido.", "error")

            return redirect(url_for("registrar"))

        # =================================================
        # REGISTRO EN BD
        # =================================================

        exito, mensaje = insertar_alumno(nombre, apellido, email, DNI, fecha_nacimiento)

        if exito:

            flash(mensaje, "exito")

        else:

            flash(mensaje, "error")

        return redirect(url_for("registrar"))

    return render_template("registro.html")


# =========================================================
# SPRINT 3 - INSCRIPCIÓN DE ALUMNOS
# =========================================================


@app.route("/inscribir", methods=["POST"])
def inscribir():

    dni_alumno = request.form.get("dni_alumno")

    id_materia = request.form.get("id_materia")

    exito, mensaje = registrar_inscripcion(dni_alumno, id_materia)

    if exito:

        flash(mensaje, "exito")

    else:

        flash(mensaje, "error")

    return redirect(url_for("registrar"))


# =========================================================
# SPRINT 4 - VISTA DE ASISTENCIA
# =========================================================


@app.route("/asistencia/<int:id_materia>")
def vista_asistencia(id_materia):

    conexion = conectar_db()

    conexion.row_factory = __import__("sqlite3").Row

    cursor = conexion.cursor()

    try:

        # -------------------------------------------------
        # Obtener materia
        # -------------------------------------------------

        materia_db = cursor.execute(
            """
            SELECT
                id,
                nombre
            FROM materias
            WHERE id = ?
            """,
            (id_materia,),
        ).fetchone()

        if materia_db is None:

            flash("La materia seleccionada no existe.", "error")

            return redirect(url_for("registrar"))

        materia = {
            "id": materia_db["id"],
            "nombre": materia_db["nombre"],
        }

        # -------------------------------------------------
        # Obtener alumnos realmente inscriptos
        # -------------------------------------------------

        filas = cursor.execute(
            """
            SELECT
                a.id,
                a.DNI,
                a.nombre,
                a.apellido
            FROM alumnos AS a

            INNER JOIN inscripciones AS i
                ON i.id_alumno = a.id

            WHERE i.id_materia = ?
              AND a.activo = 1

            ORDER BY
                a.apellido,
                a.nombre
            """,
            (id_materia,),
        ).fetchall()

        alumnos = []

        for fila in filas:

            alumnos.append(
                {
                    "id": fila["id"],
                    "dni": fila["DNI"],
                    "nombre": fila["nombre"],
                    "apellido": fila["apellido"],
                }
            )

        return render_template("asistencia.html", alumnos=alumnos, materia=materia)

    finally:

        conexion.close()


# =========================================================
# SPRINT 4 - GUARDAR ASISTENCIA
# =========================================================


@app.route("/guardar_asistencia", methods=["POST"])
def guardar_asistencia():

    id_materia = request.form.get("id_materia")

    exito, resultado = procesar_formulario_asistencia(request.form, id_materia)

    # -----------------------------------------------------
    # Error al preparar datos
    # -----------------------------------------------------

    if not exito:

        flash(resultado, "error")

        return redirect(url_for("vista_asistencia", id_materia=id_materia))

    paquete = resultado

    # -----------------------------------------------------
    # Guardar mediante el Modelo
    # -----------------------------------------------------

    exito_guardado, mensaje = guardar_asistencias(paquete)

    if exito_guardado:

        flash(mensaje, "exito")

    else:

        flash(mensaje, "error")

    return redirect(url_for("vista_asistencia", id_materia=id_materia))


# =========================================================
# SPRINT 2 - PANEL DOCENTE / CARGA DE NOTAS
# =========================================================


@app.route("/notas", methods=["GET", "POST"])
def panel_notas():

    # -----------------------------------------------------
    # GUARDAR NOTA
    # -----------------------------------------------------

    if request.method == "POST":

        id_alumno = request.form.get("id_alumno")

        id_materia = request.form.get("id_materia")

        nota_ingresada = request.form.get("nota")

        # Validar alumno y materia
        if not id_alumno or not id_materia:

            flash("Debe seleccionar un alumno y una materia.", "error")

            return redirect(url_for("panel_notas"))

        # Validar nota y calcular regularidad
        valida, nota, resultado = evaluar_nota(nota_ingresada)

        if not valida:

            flash(resultado, "error")

            return redirect(url_for("panel_notas"))

        # Guardar nota mediante la lógica existente
        exito, mensaje = insertar_nota(int(id_alumno), int(id_materia), nota)

        if exito:

            flash(f"{mensaje} Regularidad: {resultado}.", "exito")

        else:

            flash(mensaje, "error")

        return redirect(url_for("panel_notas"))

    # -----------------------------------------------------
    # CARGAR ALUMNOS Y MATERIAS
    # -----------------------------------------------------

    conexion = conectar_db()

    conexion.row_factory = __import__("sqlite3").Row

    cursor = conexion.cursor()

    try:

        filas_alumnos = cursor.execute("""
            SELECT
                id,
                nombre,
                apellido,
                DNI
            FROM alumnos
            WHERE activo = 1
            ORDER BY apellido, nombre
            """).fetchall()

        alumnos = []

        for fila in filas_alumnos:

            alumnos.append(
                {
                    "id": fila["id"],
                    "nombre": fila["nombre"],
                    "apellido": fila["apellido"],
                    "dni": fila["DNI"],
                }
            )

        filas_materias = cursor.execute("""
            SELECT
                id,
                nombre
            FROM materias
            WHERE activo = 1
            ORDER BY nombre
            """).fetchall()

        materias = []

        for fila in filas_materias:

            materias.append(
                {
                    "id": fila["id"],
                    "nombre": fila["nombre"],
                }
            )

        return render_template("notas.html", alumnos=alumnos, materias=materias)

    finally:

        conexion.close()


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)
