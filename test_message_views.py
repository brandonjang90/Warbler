"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
# app.app_context().push()

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_follow_pages_logged_in(self):
        """When you're logged in, can you see the follower/following pages for any user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.testuser_id

            # Test for following page
            response = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(response.status_code, 200)

            # Test for followers page
            response = c.get(f"/users/{self.testuser_id}/followers")
            self.assertEqual(response.status_code, 200)


    def test_add_message_logged_in(self):
        """When you're logged in, can you add a message as yourself?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.testuser_id

            response = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Hello", response.get_data(as_text=True))
            
    def test_delete_message(self):
        """Test deletion of a message."""
        m = Message(text="This message will be deleted", user_id=self.uid)
        db.session.add(m)
        db.session.commit()

        # Ensure the message is in the database
        self.assertIsNotNone(Message.query.get(m.id))

        # Delete the message
        db.session.delete(m)
        db.session.commit()

        # Ensure the message is no longer in the database
        self.assertIsNone(Message.query.get(m.id))