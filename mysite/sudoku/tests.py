from django.test import TestCase
from .user import *
from .models import *

class QuestionIndexViewTests(TestCase):
    def test_user_creation(self):
        """ Check for successful creation of a user account"""
        user = get_user_by_loginname('test_user')
        self.assertIsNone(user)
        status = create_sudoku_user('test_user', 'ilovesudoku', 'John', 'Smith')
        self.assertEqual(status['success'], True)
        user = get_user_by_loginname('test_user')
        self.assertIsNotNone(user)

    def test_user_creation(self):
        """ Check if we can't create a user with the same loginname twice """
        status = create_sudoku_user('test_user', 'ilovesudoku', 'John', 'Smith')
        status = create_sudoku_user('test_user', 'iloveyou', 'John', 'Red')
        self.assertEqual(status['success'], False)
        self.assertEqual(status['error'].count('already exists') > 0, True)

        users = SudokuBlogUser.objects.filter(loginname='test_user')
        self.assertEqual(len(users), 1)

    def test_authentication(self):
        """ Check if we correctly authenticate users """
        status = check_user_password('test_user', '123')
        self.assertEqual(status['success'], False)
        self.assertEqual(status['error'].count('does not exist') > 0, True)

        create_sudoku_user('test_user', 'ilovesudoku', 'John', 'Smith')
        status = check_user_password('test_user', '123')
        self.assertEqual(status['success'], False)
        self.assertEqual(status['error'].count('does not match') > 0, True)

        status = check_user_password('test_user', 'ilovesudoku')
        self.assertEqual(status['success'], True)