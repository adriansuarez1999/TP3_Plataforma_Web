import re
from flask import Flask, flash, redirect, render_template, request, url_for
from models import insertar_alumno, inicializar_base_datos, registrar_inscripcion

app = Flask(__name__)
app.secret_key = "clave_secreta_para_flash"

# Inicializar la base de datos y tablas al arrancar la aplicación
inicializar_base_datos()


@app.route("/", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        # Capturamos y limpiamos espacios
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        email = request.form.get("email", "").strip()
        DNI = request.form.get("DNI", "").strip()
        fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()

        # --- TAREA 3: VALIDACIONES ---
        # 1. Validar campos vacíos
        if not nombre or not apellido or not email or not DNI or not fecha_nacimiento:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("registrar"))

        # 2. Validar formato de correo electrónico
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            flash("El formato del correo electrónico no es válido.", "error")
            return redirect(url_for("registrar"))

        # --- TAREA 2: IMPLEMENTACIÓN CON LA BD ---
        exito, mensaje = insertar_alumno(nombre, apellido, email, DNI, fecha_nacimiento)

        if exito:
            flash(mensaje, "exito")
        else:
            flash(mensaje, "error")

        return redirect(url_for("registrar"))

    return render_template("registro.html")


# ==========================================
# SPRINT 3 - Tarea 2: Registrar Inscripción (Yancel)
# ==========================================
@app.route('/inscribir', methods=['POST'])
def inscribir():
    dni_alumno = request.form.get('dni_alumno')
    id_materia = request.form.get('id_materia')
    
    # Llamada a la función de inscripción desarrollada en models.py
    exito, mensaje = registrar_inscripcion(dni_alumno, id_materia)
    
    if exito:
        flash(mensaje, "exito")
    else:
        flash(mensaje, "error")
        
    return redirect(url_for('registrar'))


# ==========================================
# SPRINT 4 - Tarea 4: Vista de Toma de Asistencia (Yancel)
# ==========================================
@app.route('/asistencia/<int:id_materia>')
def vista_asistencia(id_materia):
    # Datos de ejemplo para renderizar la grilla y los checkboxes de asistencia
    materia = {"id": id_materia, "nombre": "Programación II"}
    alumnos = [
        {"dni": "40111222", "nombre": "Juan", "apellido": "Pérez"},
        {"dni": "41222333", "nombre": "María", "apellido": "Gómez"},
        {"dni": "42333444", "nombre": "Carlos", "apellido": "Rodríguez"}
    ]
    
    return render_template('asistencia.html', alumnos=alumnos, materia=materia)


if __name__ == "__main__":
    app.run(debug=True)