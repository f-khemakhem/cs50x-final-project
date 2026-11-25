# Title : 
        MedNet
#### Video demo : https://youtu.be/6nSGgwcQ758?si=tdip_3YHzeL-E-Uj

#### Description :
    MedNet is a web application that connects doctors and patients .
    It's made to help patients essentially the elderly people , and people who find it hard to understand or remember their medical history .
    Also to help doctors understand their patients cases more and make stronger , more efficient diagnosis and conclusions .
#### How it works :
    * Register : a first time user should register entering their name, email , password and confirm their password . If the password and the confirmation don't match an error is generated. 
    They also need to specify their role whether a doctor or a patient.

    *Log in : after registering the user can log in by just writing their name , email and password and the website will lead them to their dashboard whether they're a doctor or a patient

    *Patient's Dashboard : After registering, a patient should complete their profile entering their informations  , after logging in a patient will have a generated code so they can give access to doctors to see their informations and have access to them.
    In their dashboard a patient can see their informations , their up coming appointments , their prescriptions and their doctors .
    A patient can change their own informations

    *Doctor dashboard : A doctor can register and log in ; in their dashboard they have links to different pages :
        *view patients : they can see a list of names of all their patients and a searching box for searching a patient's name

        **patient_info : contains all the selected patient's informations . A doctor can edit, see/add consultations, see other doctors notes about the patient, see/add prescriptions

        ***edit patient : the doctor can change some/all of  the patient's informations

        ***consultations : the doctor can see the patient's previous consultations and can add new ones 

        ***other doctors : a doctor can write some notes about the patient for other doctors to see : THIS FEATURE MAKES IT EASIER FOR ONE PATIENT'S DOCTORS TO COMMUNICATE AND UNDERSTAND THE PATIENT'S CASE

        ***prescriptions : a doctor can see all the patient's medications , doses and descriptions that whether they or other doctors gave to them
        And they can add new ones by adding the medication, the doses needed and a description of how to use it

        *my notes : A doctor has a private space where they can write their own notes.
        they also can delete a note.
        The notes are saved by the date and time they were added at.

        *add patient : they can add a patient ,that doesn't have an account , entering their informations , after adding them a code will be generated for the patient so other doctors can have access to the patient's informations : THIS FEATURE HELPS ESPECIALLY THE ELDERLY PATIENTS AND PATIENTS THAT FIND IT HARD TO MAKE AN ACCOUNT

        *enter code : if a patient already have a code whether they created their own account or other doctor added them , the current doctor can just write their code and they'll be added to the doctor's list of patients : THIS FEATURE MAKES SURE A PATIENT WON'T BE ADDED MULTIPLE TIMES

        *agenda : contains the up-coming appointments :date , patient name and notes(optional)

#### Code :
    ===schema.sql=== : Contains the creation of all the tables needed to save the data needed for the website :
        users : table that contains all the users (doctors and patients) registring informations
        patients : table that contains all the patients registred or added in the web and their medical / personal informations
        patient_doctor : a table that connects each patient to their doctor using their id's
        appointments : a table that contains the appointments informations
        consultations : table that contains the consultations informations
        prescriptions : table that contains the prescriptions informations
        messages : table that contains the messages written from a doctor to other doctors that have the same patient
        private_notes : table that contains the doctors'private-notes and their dates
    ===init_db.py=== :  creates the database from schema.sql
    ===helper.py=== : a python file that contains the functions/classes we needed :
        *class database : a class that helps connect the SQL with PYTHON easily
        *login required : cheks if the user is logged in or not
        *doctor_can_access : checks if the doctor can access to the patient's informations or not (if they're already connected in the patient_doctor table than the doctor can access)
        *role required : checks the user's role (must be doctor or patient) and returns it
        *generate_share_code : generates a code for the patients so the doctors can use it to access to their informations
    ===auth.py=== : contains the login / register / log out routes
    ===doctor.py=== : contains the code that generates the doctor's side
    ===patient.py=== : contains the code that generates the patient's side
    ===app.py=== : main file that runs the web app ; it import the other files
    ===/templates=== : contains all the html files
    ===/static=== : contains the css file
#### Design choices :
    --FLASK AND SQLITE: Flask is lightweight and I learned it in CS50. SQLite needs no separate server, which keeps the project simple to run
    --THREE VISIBILTY CHOICES : patient-only (patient's dashboard); doctor-only(doctor's dashboard) ; doctors-only-shared-notes (messages between patient's doctors)
    --SEPERATE PATIENT-DOCTOR TABLE : a patient can have multiple doctors so a patient-doctor table is a better design than adding a doctor_id column in the patients table to avoid redundancy
    --SHARE CODE OVER PATIENT_ID : IDs are guessable and easy to find so a generated code is much more secure 
    --DOCTOR CREATES PATIENTS ACCOUNT BEFORE THEY DO : some patients can't create their own accounts or don't know about the web , so a doctor can add a patient even though the patient doesn't have an account yet. If that's done a code will be generated for that patient so later when they create their account they just enter the code . THIS FEATURE STOPS THE REDUNDANCY 
    --ACCESS CHECK ON EVERY ROUTE : for security 
    --HASHED PASSWORDS : more secure
    --LOGGING WITH EMAILS (SHOULD BE UNIQUE) : names can't be unique ;  two users can have the same name and the same password . Unique emails are the solution for this problem
    --BLUEPRINT : only one python file would be so long and complicated and more difficult to understand; I used multiple files for each role and then the app.py to create the app, configure the session and register the three blueprints (auth, doctor, patient).

#### Limitations :
The share code never expires, and anyone who has it can link to the patient.
No way for a patient to revoke a doctor yet.
Doctors aren't verified.
There is no email verification or password reset.
No photos or analysis files, and no date of birth.
Test data only, no real medical data.

#### AI :
    I used AI to understand some functions and syntax I didn't understand or know . It also helped writing some code and give me some tips to improve my code . BUT the ideas , the design and the way how the web app works were all mine .







