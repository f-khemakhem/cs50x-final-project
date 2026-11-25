CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT  NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('doctor' ,'patient'))
);

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,
    user_id INTEGER ,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    chronic_illnesses TEXT,
    habits TEXT,
    medical_history TEXT,
    share_code TEXT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);



CREATE TABLE IF NOT EXISTS doctor_patient (
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    PRIMARY KEY (doctor_id, patient_id),
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'scheduled'
        CHECK (status IN ('scheduled', 'done', 'cancelled')),
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_id INTEGER,
    consultation_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    diagnosis TEXT,
    analyses TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    prescription_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    medication TEXT NOT NULL,
    dosage TEXT NOT NULL,
    instructions TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    message_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS private_notes (
    id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);