import sqlite3
from functools import wraps
from flask import Blueprint, Blueprint, Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required, role_required, doctor_can_access , db, generate_share_code

doctor_bp = Blueprint("doctor", __name__)

@doctor_bp.route("/doctor")
@login_required
def doctor():
    return render_template("doctor.html")

@doctor_bp.route("/consultations/<int:patient_id>")
@login_required
@role_required("doctor")
def consultations(patient_id):
    if not doctor_can_access(patient_id):
        flash("Access denied", "danger")
        return redirect("/view_patients")

    patient = db.execute("SELECT * FROM patients WHERE id = ?", patient_id)
    if not patient:
        flash("Patient not found", "danger")
        return redirect("/view_patients")

    history = db.execute(
        """
        SELECT consultations.id, consultations.consultation_date,
               consultations.notes, consultations.diagnosis,
               consultations.analyses, users.username AS doctor_name
        FROM consultations
        JOIN users ON users.id = consultations.doctor_id
        WHERE consultations.patient_id = ? AND consultations.doctor_id = ?
        ORDER BY consultations.consultation_date DESC
        """,
        patient_id, session["user_id"]
    )
    return render_template("consultations.html", patient=patient[0], history=history)

@doctor_bp.route("/add_patient", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def add_patient():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        chronic_illnesses = request.form.get("chronic_illnesses")
        habits = request.form.get("habits")
        medical_history = request.form.get("medical_history")

        if not name or not age or not gender:
            flash("Please fill in all required fields", "warning")
            return render_template("add_patient.html")

        try:
            share_code = generate_share_code()

            patient_id = db.execute(
                "INSERT INTO patients (name, age, gender, chronic_illnesses, habits, medical_history, share_code) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                name, age, gender, chronic_illnesses, habits, medical_history, share_code,
            )
            db.execute(
                "INSERT INTO doctor_patient (doctor_id, patient_id) VALUES (?, ?)",
                session["user_id"], patient_id,
            )   
        except sqlite3.Error as e:
            print(f"Error adding patient: {e}")
            flash("Error adding patient", "danger")
            return render_template("add_patient.html")
        
        flash("Patient added successfully", "success")
        return redirect(f"/patient_info/{patient_id}")
    else:
        return render_template("add_patient.html")


@doctor_bp.route("/enter_code", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def enter_code():
    if request.method == "POST":
        code = (request.form.get("code") or "").strip().upper()
        if not code:
            flash("Please enter a code", "warning")
            return render_template("enter_code.html")

        rows = db.execute("SELECT id FROM patients WHERE share_code = ?", code)
        if not rows:
            flash("Invalid code", "danger")
            return render_template("enter_code.html")

        patient_id = rows[0]["id"]
        try:
            db.execute(
                "INSERT INTO doctor_patient (doctor_id, patient_id) VALUES (?, ?)",
                session["user_id"], patient_id,
            )
        except sqlite3.IntegrityError:
            flash("You already have access to this patient", "warning")
            return redirect("/view_patients")

        flash("Patient added to your list", "success")
        return redirect(f"/patient_info/{patient_id}")

    return render_template("enter_code.html")

@doctor_bp.route("/view_patients")
@login_required
@role_required("doctor")
def view_patients():
    search = request.args.get("search")

    query = """
        SELECT patients.* FROM patients
        JOIN doctor_patient ON patients.id = doctor_patient.patient_id
        WHERE doctor_patient.doctor_id = ?
    """
    params = [session["user_id"]]

    if search:
        query += " AND patients.name LIKE ?"
        params.append(f"%{search}%")

    patients = db.execute(query, *params)
    return render_template("view_patient.html", patients=patients)

@doctor_bp.route("/patient_info/<int:patient_id>")
@login_required
@role_required("doctor")
def patient_info(patient_id):
    if not doctor_can_access(patient_id):
        flash("Access denied")
        return redirect("/view_patients")

    patient = db.execute("SELECT * FROM patients WHERE id = ?", patient_id)
    if not patient:
        flash("Patient not found")
        return redirect("/view_patients")
    return render_template("patient_info.html", patient=patient[0])

@doctor_bp.route("/edit_patient/<int:patient_id>", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def edit_patient(patient_id):
    if not doctor_can_access(patient_id):
        flash("Access denied", "danger")
        return redirect("/view_patients")
    patient = db.execute("SELECT * FROM patients WHERE id = ?", patient_id)
    if not patient:
        flash("Patient not found", "danger")
        return redirect("/view_patients")

    if request.method == "POST":
        editable_fields = ("name", "age", "gender", "chronic_illnesses", "habits", "medical_history")
        updates = []
        values = []
        for field in editable_fields:
            value = request.form.get(field)
            if value is not None and value.strip():
                updates.append(f"{field} = ?")
                values.append(value.strip())                

        if not updates:
            flash("Please enter at least one field to edit", "warning")
            return render_template("edit_patient.html", patient=patient[0])

        try:
            db.execute(
                f"UPDATE patients SET {', '.join(updates)} WHERE id = ?",
                *(values + [patient_id])
            )
        except sqlite3.Error:
            flash("Error updating patient", "danger")
            return render_template("edit_patient.html", patient=patient[0])
        
        flash("Patient information updated successfully", "success")
        return redirect(f"/patient_info/{patient_id}")
    else:
        return render_template("edit_patient.html", patient=patient[0])


@doctor_bp.route("/agenda")
@login_required
@role_required("doctor")
def agenda():
    appointments = db.execute(
        """
        SELECT appointments.id, appointments.appointment_date,
               appointments.notes, patients.id AS patient_id,
               patients.name AS patient_name
        FROM appointments
        JOIN patients ON patients.id = appointments.patient_id
        WHERE appointments.doctor_id = ?
          AND appointments.appointment_date >= date('now')
          AND appointments.status = 'scheduled'
        ORDER BY appointments.appointment_date
        """,
        session["user_id"],
    )
    return render_template("agenda.html", appointments=appointments)

@doctor_bp.route("/add_appointment", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def add_appointment():
    patients = db.execute(
        """
        SELECT patients.id, patients.name FROM patients
        JOIN doctor_patient ON patients.id = doctor_patient.patient_id
        WHERE doctor_patient.doctor_id = ?
        """,
        session["user_id"],
    )

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        appointment_date = request.form.get("appointment_date")
        notes = request.form.get("notes")

        if not patient_id or not appointment_date:
            flash("Please choose a patient and a date", "warning")
            return render_template("add_appointments.html", patients=patients), 400

        if not doctor_can_access(patient_id):
            flash("Patient not found", "danger")
            return redirect("/agenda")

        db.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, notes) "
            "VALUES (?, ?, ?, ?)",
            patient_id, session["user_id"], appointment_date, notes,
        )
        flash("Appointment added successfully", "success")
        return redirect("/agenda")

    return render_template("add_appointments.html", patients=patients)

@doctor_bp.route("/delete_appointment/<int:appointment_id>", methods=["POST"])
@login_required
@role_required("doctor")
def delete_appointment(appointment_id):
    db.execute(
        "DELETE FROM appointments WHERE id = ? AND doctor_id = ?",
        appointment_id, session["user_id"],
    )
    flash("Appointment deleted successfully", "success")
    return redirect("/agenda")

@doctor_bp.route("/my_notes", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def my_notes():
    if request.method == "POST":
        content = request.form.get("content")
        if not content or not content.strip():
            flash("Please write a note", "warning")
            return redirect("/my_notes")

        db.execute(
            "INSERT INTO private_notes (doctor_id, content) VALUES (?, ?)",
            session["user_id"], content.strip(),
        )
        return redirect("/my_notes")

    notes = db.execute(
        "SELECT * FROM private_notes WHERE doctor_id = ? ORDER BY created_at DESC",
        session["user_id"],
    )
    flash("Note added successfully", "success")
    return render_template("my_notes.html", notes=notes)

@doctor_bp.route("/delete_note/<int:note_id>", methods=["POST"])
@login_required
@role_required("doctor")
def delete_note(note_id):
    db.execute(
        "DELETE FROM private_notes WHERE id = ? AND doctor_id = ?",
        note_id, session["user_id"],
    )
    flash("Note deleted successfully", "success")
    return redirect("/my_notes")

@doctor_bp.route("/add_consultation/<int:patient_id>", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def add_consultation(patient_id):
    if not doctor_can_access(patient_id):
        flash("Access denied")
        return redirect("/view_patients")

    patient = db.execute("SELECT * FROM patients WHERE id = ?", patient_id)
    if not patient:
        flash("Patient not found")
        return redirect("/view_patients")

    if request.method == "POST":
        consultation_notes = request.form.get("consultation_notes")
        diagnosis = request.form.get("diagnosis")
        analyses = request.form.get("analyses")
        if not consultation_notes:
            flash("Please enter consultation notes", "warning")
            return render_template("patient_appointments.html", patient=patient[0])
        try:
            db.execute(
                "INSERT INTO consultations (patient_id, doctor_id, notes, diagnosis, analyses) VALUES(?, ?, ?, ?, ?)",
                patient_id,
                session["user_id"],
                consultation_notes,
                diagnosis,
                analyses
            )
        except sqlite3.Error:
            flash("Error saving consultation notes", "danger")
            return render_template("add_consultation.html", patient=patient[0])

        flash("Consultation notes added successfully", "success")
        return redirect(f"/consultations/{patient_id}")
    else:
        return render_template("add_consultation.html", patient=patient[0])



@doctor_bp.route("/other_doctors/<int:patient_id>", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def other_doctors(patient_id):
    if not doctor_can_access(patient_id):
        flash("Access denied", "danger")
        return redirect("/view_patients")

    patient = db.execute("SELECT * FROM patients WHERE id = ?", patient_id)
    if not patient:
        flash("Patient not found", "danger")
        return redirect("/view_patients")

    if request.method == "POST":
        content = request.form.get("notes")
        if not content or not content.strip():
            flash("Please enter a note", "warning")
        else:
            try:
                db.execute(
                    "INSERT INTO messages (patient_id, doctor_id, content) VALUES (?, ?, ?)",
                    patient_id, session["user_id"], content.strip(),
                )
            except sqlite3.Error:
                flash("Error saving note", "danger")
        flash("Note added successfully", "success")
        return redirect(f"/other_doctors/{patient_id}")

    messages = db.execute(
        """
        SELECT messages.id, messages.content, messages.message_date, messages.doctor_id, users.username AS doctor_name
        FROM messages JOIN users ON users.id = messages.doctor_id
        WHERE messages.patient_id = ?
        ORDER BY messages.message_date DESC
        """,
        patient_id,
    )
    return render_template("other_doctors.html", patient=patient[0], messages=messages)

@doctor_bp.route("/delete_message/<int:message_id>", methods=["POST"])
@login_required
@role_required("doctor")
def delete_message(message_id):
    rows = db.execute(
        "SELECT patient_id FROM messages WHERE id = ? AND doctor_id = ?",
        message_id, session["user_id"],
    )
    if not rows:
        flash("Note not found", "danger")
        return redirect("/view_patients")

    patient_id = rows[0]["patient_id"]
    db.execute(
        "DELETE FROM messages WHERE id = ? AND doctor_id = ?",
        message_id, session["user_id"],
    )
    flash("Note deleted successfully", "success")
    return redirect(f"/other_doctors/{patient_id}")

@doctor_bp.route("/prescriptions/<int:patient_id>")
@login_required
@role_required("doctor")
def prescriptions(patient_id):
    if not doctor_can_access(patient_id):
        flash("Access denied", "danger")
        return redirect("/view_patients")
    patient = db.execute("SELECT * FROM patients WHERE id = ?", patient_id)
    if not patient:
        flash("Patient not found", "danger")
        return redirect("/view_patients")

    prescriptions = db.execute(
            """
            SELECT prescriptions.prescription_date, prescriptions.medication,
               prescriptions.dosage, prescriptions.instructions,
               users.username AS doctor_name
            FROM prescriptions
            JOIN users ON users.id = prescriptions.doctor_id
            WHERE prescriptions.patient_id = ?
            ORDER BY prescriptions.prescription_date DESC
            """,
            patient_id,
        )
    add = request.args.get("add_prescription_button")
    if add:
        return render_template("add_prescription.html", patient_id=patient_id)  

    return render_template("prescriptions.html", patient=patient[0], prescriptions=prescriptions)
    

@doctor_bp.route("/add_prescription/<int:patient_id>", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def add_prescription(patient_id):
    if not doctor_can_access(patient_id):
        flash("Access denied", "danger")
        return redirect("/view_patients")
    if request.method == "POST":
        prescription_date = request.form.get("prescription_date")
        medication = request.form.get("medication")
        dosage = request.form.get("dosage")
        instructions = request.form.get("instructions")

        if not prescription_date or not medication or not dosage:
            flash("Please fill in all required fields", "warning")
            return render_template("add_prescription.html")

        try:
            db.execute(
                "INSERT INTO prescriptions (patient_id, doctor_id, prescription_date, medication, dosage, instructions) VALUES(?, ?, ?, ?, ?, ?)",
                patient_id,
                session["user_id"],
                prescription_date,
                medication,
                dosage,
                instructions
            )
        except sqlite3.Error:
            flash("Error adding prescription", "danger")
            return render_template("add_prescription.html", patient_id=patient_id)

        flash("Prescription added successfully", "success")
        return redirect(f"/prescriptions/{patient_id}")
    else:
        return render_template("add_prescription.html", patient_id=patient_id)


