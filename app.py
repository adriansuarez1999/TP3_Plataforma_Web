import re
from flask import Flask, flash, redirect, render_template, request, url_for
from models import insertar_alumno

app = Flask(__name__)
app.secret_key = "clave_secreta_para_flash"


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


if __name__ == "__main__":
    app.run(debug=True)
