# Documentation

## Database Migration

The application now uses SQLite as the database. The database file is `app.db`.

To create the database and apply the schema, run the following commands:

1.  Initialize the migrations directory (only needs to be done once):
    ```bash
    python -m flask db init
    ```
2.  Generate the migration script:
    ```bash
    python -m flask db migrate -m "Initial migration"
    ```
3.  Apply the migration to the database:
    ```bash
    python -m flask db upgrade
    ```

## Usage Guide

### Class Management

The "View Students" module has been replaced with a "Class" module.

*   **View Classes:** Navigate to the "Classes" page to see a list of all classes.
*   **Add a Class:** From the "Classes" page, click the "Add Class" button to create a new class. You will need to provide the department, section, year, and advisor.
*   **View Class Details:** Click the "View Class" button on a class card to see the list of students in that class.

### Student Management

Student management is now done within a class.

*   **Add a Student:** From the class detail page, click the "Add Student" button. You will need to provide the student's name and capture their face.
*   **Edit a Student:** From the class detail page, click the "Edit" button next to a student's name. You can change the student's name and class.
*   **Delete a Student:** From the class detail page, click the "Delete" button next to a student's name.
*   **Add a Face:** From the class detail page, click the "Add Face" button to add another face image for a student.

### PDF Reports

You can download attendance reports in PDF format.

*   **Class Reports:** From the class detail page, you can download daily and monthly attendance reports for the entire class.
*   **Student Reports:** From the class detail page, you can download monthly and yearly attendance reports for individual students using the dropdown menu next to their name.

### Excel Import

You can import a list of students from an Excel file. The Excel file should have two columns: `name` and `class_id`. The `class_id` should correspond to the ID of a class that already exists in the database.
