from unittest import TestCase
import users
from datetime import datetime
import subprocess
import random
import string
import os

class TestUser(TestCase):

    def setUp(self):
       users.clear_users()

    def tearDown(self):
        users.clear_users()

    def test_register(self):
        # test registering user one
        registered_users = users.register("foo", "bar", "bar", "30/12/1980")

        self.assertDictEqual(registered_users,  {"username": "foo", "password": "bar", "dateOfBirth": "30/12/1980"})

        # test registering user two
        registered_users_two = users.register('auma', 'just_password', 'just_password', "30/12/1970")

        self.assertDictEqual(registered_users_two, {"username": "auma", "password": 'just_password', "dateOfBirth": "30/12/1970"})

        # test register with users name who already exist
        self.assertRaises(users.UserAlreadyExist, users.register, "foo", "password", "password", "30/12/1980")

        # test register with the same user two raises users already exist
        self.assertRaises(users.UserAlreadyExist, users.register, "auma", "just_password", "passwdDoen'tMatter", "30/12/1970")

        # test register users with password missmatch 
        self.assertRaises(users.PasswordMissmatch, users.register, "favw", "password", "passwOrd", "30/12/1980")


    def test_login(self):
        # first register users
        registered_user_1 = users.register("user1", "user1password", "user1password", "30/12/1980")
        self.assertEqual(registered_user_1, users.login("user1", "user1password"))

        registered_user_2 = users.register("user2", "user2password", "user2password", "30/12/1970")
        self.assertEqual(registered_user_2, users.login("user2", "user2password"))

        # test login with invalid password
        self.assertRaises(users.InvalidPassword, users.login, "user1", "wrongPassword")

        # test login with users who does not exist
        self.assertRaises(users.InvalidUsername, users.login, "bar",  "bar")
    
    def test_register_with_invalid_date(self):
        # test invalid date of birth 
        self.assertRaises(users.InvalidDateOfBirth, users.register, "favw", "password", "password", "invalid_date") 

class TestUserArePersisted(TestCase):

    def setUp(self):
       users.clear_users()

    def tearDown(self):
        users.clear_users()

    def test_users_registration_and_login_persists_data(self):
        # register users via command line
        random_usersname = ''.join(random.choices(string.ascii_lowercase, k = 5))
        password, dateOfBirth = "bar", "30/12/1970"
        results = subprocess.run([
            "python", 
            "manage.py",
            "user_register",
            f"--username={random_usersname}",
            f"--password={password}", 
            f"--password2={password}",
            f"--dateOfBirth={dateOfBirth}"], stdout=subprocess.PIPE)
        self.assertEqual(0, results.returncode)

        # now check the users is registered
        self.assertDictEqual(
            {
                "username": random_usersname,
                "password": password,
                "dateOfBirth": dateOfBirth
                },
                 users.login(random_usersname, password))


        # check registering the same users fails
        self.assertRaises(users.UserAlreadyExist, users.register, random_usersname, password, password, dateOfBirth)

        # test login with invalid passowrd fails
        results = subprocess.run([
                    "python",
                    "manage.py",
                    "user_login",
                    f"--username={random_usersname}",
                    f"--password={password}_invalid_password",
                    ], stdout=subprocess.PIPE)
        self.assertEqual(1, results.returncode)

        # test login with valid password
        results = subprocess.run([
                    "python",
                    "manage.py",
                    "user_login",
                    f"--username={random_usersname}",
                    f"--password={password}",
                    ], stdout=subprocess.PIPE)
        self.assertEqual(0, results.returncode)
