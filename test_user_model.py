"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):

    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        """Remove test data"""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        db.session.rollback()


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


    # testing following functionality

    def test_user_follows(self):
        """tests that user1 is following user2"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_is_not_following(self):
        """there is no following relationship"""
        self.assertFalse(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))


    def test_is_followed_by(self):
        """verify user1 is following user2 and user2 is not following user1"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))


    # Signup tests

    def test_user_signup(self):
        """Does signup work"""

        u = User.signup(
            email="signup@test.com",
            username="testuser",
            password="password",
            image_url = None
        )
        uid = 12345
        u.id = uid
        db.session.add(u)
        db.session.commit()

        #User should exist in database
        test_user = User.query.get(uid)
        self.assertEqual(test_user.email, 'signup@test.com')
        self.assertEqual(test_user.username, 'testuser')
        self.assertNotEqual(test_user.password, 'password')
        self.assertTrue(test_user.password.startswith("$2b$"))

    # Authentication test
    # check authenticate() class method works

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
    
