from app import create_app
from app.extensions import db
import click
from flask_migrate import stamp

app = create_app()

@app.cli.command("reinit-db")
def reinit_db_command():
    """Drops and re-creates the database."""
    db.drop_all()
    db.create_all()
    stamp()
    click.echo('Re-initialized the database.')

if __name__ == '__main__':
    app.run(debug=True)