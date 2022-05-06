import unittest
from app import create_app, db
from app.models import User, Test, Location, TestingCenter
from app.config import Config
from datetime import datetime

class TestConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI='sqlite://'
    # sqlite:// was passed as the database URI to cause SQLAlchemy to use an in-memory database...
    # ...for the tests

class UserAndTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    def test_password_hashing(self):
        u = User(username='john_doe')
        u.hash_password('Thi$is@$tr0ngPassworD')
        self.assertFalse(u.verify_password('Thi$is@$tr0ngPassword'))
        self.assertTrue(u.verify_password('Thi$is@$tr0ngPassworD'))


    def test_user_ownership_testingcenter(self):
        u = User(id=1, username='jane_doe')
        u2 = User(id=2, username='john_doe')
        center1 = TestingCenter(id=1, name='Noguchi')
        center2 = TestingCenter(id=2, name='Ridge')
        results_of_test = Test(date=datetime.utcnow(), user_id=1, testing_center_id=2)

        db.session.add_all([u, results_of_test, center1, center2])
        db.session.commit()

        self.assertEqual(results_of_test.location, center2)
        self.assertNotEqual(results_of_test.location, center1)
        self.assertEqual(results_of_test.owner, u)
        self.assertNotEqual(results_of_test.owner, u2)


    def test_user_location_relationship(self):
        user1 = User(username='john')
        user2 = User(username='jane')
        user3 = User(username='spector')
        location1 = Location(location_name='church')
        location2 = Location(location_name='school')
        
        db.session.add_all([user1, user2, user3, location1, location2])
        db.session.commit()

        self.assertEqual(user1.visits.count(), 0)
        self.assertEqual(user2.visits.count(), 0)
        self.assertEqual(user3.visits.count(), 0)
        self.assertEqual(location1.wasvisitedby.count(), 0)
        self.assertEqual(location2.wasvisitedby.count(), 0)

        user1.visits.append(location1)
        user1.visits.append(location2)
        user3.visits.append(location2)

        self.assertEqual(user1.visits.count(), 2)
        self.assertEqual(user2.visits.count(), 0)
        self.assertEqual(user3.visits.count(), 1)
        self.assertEqual(location1.wasvisitedby.count(), 1)
        self.assertEqual(location2.wasvisitedby.count(), 2)

        user1.visits.remove(location2)
        user2.visits.append(location2)

        self.assertEqual(user1.visits.count(), 1)
        self.assertEqual(user2.visits.count(), 1)
        self.assertEqual(user3.visits.count(), 1)
        self.assertEqual(location1.wasvisitedby.count(), 1)
        self.assertEqual(location2.wasvisitedby.count(), 2)


    def test_user_to_user_relationship(self):
        user1 = User(username='john')
        user2 = User(username='jane')
        user3 = User(username='spector')
        user4 = User(username='steve')

        self.assertEqual(user1.knows.count(), 0)
        self.assertEqual(user2.knows.count(), 0)
        self.assertEqual(user3.knows.count(), 0)
        self.assertEqual(user4.knows.count(), 0)
        self.assertEqual(user1.known_by.count(), 0)
        self.assertEqual(user2.known_by.count(), 0)
        self.assertEqual(user3.known_by.count(), 0)
        self.assertEqual(user4.known_by.count(), 0)

        user1.add_contact(user2)
        user1.add_contact(user2)
        user1.add_contact(user3)
        user2.add_contact(user4)

        self.assertEqual(user1.knows.count(), 2)
        self.assertEqual(user2.knows.count(), 1)
        self.assertEqual(user3.knows.count(), 0)
        self.assertEqual(user4.knows.count(), 0)
        self.assertEqual(user1.known_by.count(), 0)
        self.assertEqual(user2.known_by.count(), 1)
        self.assertEqual(user3.known_by.count(), 1)
        self.assertEqual(user4.known_by.count(), 1)
    

if __name__ == '__main__':
    unittest.main(verbosity=2)