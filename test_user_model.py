"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import Bcrypt
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app
# app.app_context().push()

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
bcrypt = Bcrypt()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        # Initialize app context
        self.app_context = app.app_context()
        self.app_context.push()

        # Create all tables in the database
        db.create_all()

    def tearDown(self):
        # Remove the app context after the test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""

        u2 = User.signup("testuser2", "test2@test.com", "password", None)
        u2.id = 99999
        db.session.add(u2)
        u2.following.append(self.u)
        db.session.commit()

        self.assertTrue(self.u.is_followed_by(u2))
        self.assertFalse(u2.is_followed_by(self.u))
    
    def test_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        u = User.authenticate(self.u.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid)