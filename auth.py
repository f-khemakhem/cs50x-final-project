import sqlite3

from functools import wraps
from helper import db 
from flask import Blueprint, Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return render_template("login.html")
        if not request.form.get("email"):
                flash("must provide email")
                return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE email = ?", 
            request.form.get("email")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["role"] = rows[0]["role"]

        # Redirect user to home page
        if rows[0]["role"] == "doctor":
            return redirect("/doctor")  
        elif rows[0]["role"] == "patient":
            return redirect("/patient")
        else:
            flash("invalid role")
            return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        role = request.form.get("role")
        if not name:
            flash("please enter name")
            return render_template("register.html")
        if not email:
            flash("please enter email")
            return render_template("register.html")
        if not password:
            flash("please enter password")
            return render_template("register.html")
        if not confirmation:
            flash("please confirm password")
            return render_template("register.html")
        if confirmation != password:
            flash("passwords do not match")
            return render_template("register.html")
        if role not in ["doctor", "patient"]:
            flash("please choose a valid role")
            return render_template("register.html")
        try:
            db.execute(
                "INSERT INTO users (username, email, hash, role) VALUES(?, ?, ?, ?)", name,email, generate_password_hash(password), role)
        except sqlite3.Error:
            flash("user already exists")
            return render_template("register.html")

        return redirect("/")
    else:
        return render_template("register.html")
