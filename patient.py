import sqlite3
from functools import wraps
from flask import  Blueprint, Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required, role_required, db, generate_share_code


patient_bp = Blueprint("patient", __name__)
    
@patient_bp.route("/patient")
@login_required
@role_required("patient")
def patient():
    info = db.execute("SELECT * FROM patients WHERE user_id = ?", session["user_id"])
    if not info:
        return redirect("/complete_profile")
    patient = info[0]

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
        patient["id"],
    )

    consultations = db.execute(
        """
        SELECT consultations.consultation_date, consultations.notes,
               consultations.diagnosis, consultations.analyses,
               users.username AS doctor_name
        FROM consultations
        JOIN users ON users.id = consultations.doctor_id
        WHERE consultations.patient_id = ?
        ORDER BY consultations.consultation_date DESC
        """,
        patient["id"],
    )

    appointments = db.execute(
        """
        SELECT appointments.appointment_date, appointments.notes,
               users.username AS doctor_name
        FROM appointments
        JOIN users ON users.id = appointments.doctor_id
        WHERE appointments.patient_id = ?
          AND appointments.appointment_date >= date('now')
          AND appointments.status = 'scheduled'
        ORDER BY appointments.appointment_date
        """,
        patient["id"],
    )

    doctors = db.execute(
        """
        SELECT users.id, users.username
        FROM users
        JOIN doctor_patient ON users.id = doctor_patient.doctor_id
        WHERE doctor_patient.patient_id = ?
        """,
        patient["id"],
    )

    return render_template(
        "patient.html",
        patient=patient,
        prescriptions=prescriptions,
        consultations=consultations,
        appointments=appointments,
        doctors=doctors,
    )




@patient_bp.route("/complete_profile", methods=["GET", "POST"])
@login_required
@role_required("patient")
def complete_profile():
    # Already linked to a record: nothing to complete
    if db.execute("SELECT 1 FROM patients WHERE user_id = ?", session["user_id"]):
        return redirect("/patient")

    mode = request.args.get("mode")

    if request.method == "POST":
        claim_code = (request.form.get("claim_code") or "").strip().upper()

        # Case 1: a doctor already created my record, I link it with my code
        if claim_code:
            rows = db.execute(
                "SELECT id FROM patients WHERE share_code = ? AND user_id IS NULL",
                claim_code,
            )
            if not rows:
                flash("Invalid code, or this record already has an account", "danger")
                return render_template("complete_profile.html", mode=mode)

            db.execute(
                "UPDATE patients SET user_id = ? WHERE id = ?",
                session["user_id"], rows[0]["id"],
            )
            flash("Your record is now linked to your account", "success")
            return redirect("/patient")

        # Case 2: I'm new, I fill my profile (kima 9bal)
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        chronic_illnesses = request.form.get("chronic_illnesses")
        habits = request.form.get("habits")
        medical_history = request.form.get("medical_history")

        if not name or not age or not gender:
            flash("Please fill in name, age and gender", "warning")
            return render_template("complete_profile.html", mode=mode)

        share_code = generate_share_code()
        try:
            db.execute(
                "INSERT INTO patients (user_id, name, age, gender, chronic_illnesses, habits, medical_history, share_code) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                session["user_id"], name, age, gender,
                chronic_illnesses, habits, medical_history, share_code,
            )
        except sqlite3.Error:
            flash("Error saving profile", "danger")
            return render_template("complete_profile.html", mode=mode)

        return redirect("/patient")

    return render_template("complete_profile.html", mode=mode)

@patient_bp.route("/change_info", methods=["GET", "POST"])
@login_required
@role_required("patient")
def change_info():
    patient = db.execute("SELECT * FROM patients WHERE user_id = ?", session["user_id"])
    if not patient:
        flash("Patient not found", "danger")
        return redirect("/patient")

    patient = patient[0]

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
                return render_template("change_info.html", patient=patient[0])
        try:
            db.execute(
                f"UPDATE patients SET {', '.join(updates)} WHERE id = ?",
                *(values + [session["user_id"]])
         )
        except sqlite3.Error:
            flash("Error updating profile", "danger")
            return render_template("change_info.html", patient=patient)
        
        flash("Profile updated successfully", "success")
        return redirect("/patient")

    return render_template("change_info.html", patient=patient)
