from flask_testing import TestCase
import unittest
from flaskcard import *

class FlaskcardTests(TestCase):
    def create_app(self):
        app = flaskcard.app
        app.config['TESTING'] = True
        return app

    def test_user_creation(self):
        user = User(username='test',password='pass')
        db.session.add(user)
        db.session.commit()

        assert user in db.session
        assert user in User.query.all()
