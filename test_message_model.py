import os
from unittest import TestCase
from datetime import datetime
from flask_bcrypt import Bcrypt
from app import app, db
from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

bcrypt = Bcrypt()

class MessageModelTestCase(TestCase):
    """Test model for Message."""

    def setUp(self):
        """Create test client, add sample data."""
        self.app_context = app.app_contect()
        self.app_context.push()
        
        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User.signup("testuser", "test@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()
        db.session.close()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="Hello World!",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "Hello World!")

    def test_message_user_relationship(self):
        """Test the relationship between User and Message models."""
        
        before = datetime.utcnow()
        after = datetime.utcnow()

        m1 = Message(text="User1's message", user_id=self.uid)
        db.session.add(m1)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        # The text of the user's first message should match
        self.assertEqual(self.u.messages[0].text, "User1's message")

        # Test cascading delete - deleting a user should delete their messages
        db.session.delete(self.u)
        db.session.commit()

        # Message should also be deleted
        self.assertIsNone(Message.query.get(m1.id))


        # Check that the message's timestamp is within a reasonable range
        self.assertTrue(before <= m1.timestamp <= after)


