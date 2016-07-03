from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from bucketlist_api import models, create_app, db
from bucketlist_api.config import DevConfig
import nose

app = create_app(DevConfig)

manager = Manager(app)
migrate = Migrate(app, db)


@manager.command
def drop():
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def create(default_data=True, sample_data=False):
    "Creates database tables from sqlalchemy models"
    db.create_all()


@manager.command
def test():
    """Run test for the application."""
    test_response = nose.run(argv=['--with-coverage'])
    return test_response


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, models=models)

manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server())


if __name__ == '__main__':
    manager.run()
