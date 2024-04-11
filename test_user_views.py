import os
from unittest import TestCase
from models import db, User, Message
from app import app, CURR_USER_KEY

# Setup test database
os.environ['_DATABASE_URI'] = 'postgresql:///warbler-test'

db.create_all()

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client and sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 94566
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        db.session.close()

    def test_signup(self):
        """Can user sign up?"""
        
        with self.client as c:
            resp = c.post('/signup', data=dict(username="newuser", email="new@test.com",
                                               password="password", image_url=None), follow_redirects=True)
            # Make sure it redirects to the home page
            self.assertEqual(resp.status_code, 200)
            self.assertIn("newuser", str(resp.data))

            # Make sure the user was added to the database
            user = User.query.filter_by(username="newuser").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, "new@test.com")

    def test_login(self):
        """Can user log in?"""

        with self.client as c:
            resp = c.post('/login', data=dict(username="testuser", password="testuser"), follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", str(resp.data))

    def test_logout(self):
        """Can user log out?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.testuser_id

            resp = c.get('/logout', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("testuser", str(resp.data))

    def test_view_following_logged_in(self):
        """When logged in can you view the following page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user'] = self.testuser_id

            resp = c.get(f'/users/{self.testuser_id}/following')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Following', str(resp.data))

    def test_view_following_logged_out(self):
        """When logged out are you disallowed from viewing the following page?"""

        resp = self.client.get(f'/users/{self.testuser_id}/following', follow_redirects=True)
        self.assertNotIn('Following', str(resp.data))
        self.assertIn('Access unauthorized', str(resp.data))
