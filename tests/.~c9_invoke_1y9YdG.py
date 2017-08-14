import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser
from selenium import webdriver

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("phantomjs")

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        self.entry = Entry(title="test entry", 
                            content="test content",
                            author=self.user)          
                            
        session.add(self.user, self.entry)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(1)
    
    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        
    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")
        
    def test_add_edit_view_entry(self):
        #simulate a login
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        # #simulate adding entry
        # self.browser.visit("http://127.0.0.1:8080/entry/add")
        # self.browser.fill("title", "test entry")
        # self.browser.fill("content", "test content")
        # button = self.browser.find_by_css("button[type=submit]")
        # button.click()
        # self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        #attempt to edit entry
        self.browser.visit("http://127.0.0.1:8080/entry/1/edit")
        self.browser.fill("title", "test content")
        self.browser.fill("content", "test entry")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        time.sleep(5)
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/1")
    
    def test_view_entry(self):
        self.browser.visit("http://127.0.0.1:8080/")
        time.sleep(10)
        link = self.browser.find_element_by_link_text("test entry")
        link.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/1")
        
    def test_signup(self):
         self.browser.visit("http://127.0.0.1:8080/signup")
         self.browser.fill("username", "betty")
         self.browser.fill("email", "betty@example.com")
         self.browser.fill("password", "test")
         self.browser.fill("confirm", "test")
         button = self.browser.find_by_css("button[type=submit]")
         button.click()
         time.sleep(5)
         self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
         
    def test_signup_username_already_exists(self):
         self.browser.visit("http://127.0.0.1:8080/signup")
         self.browser.fill("username", "Alice")
         self.browser.fill("email", "b@example.com")
         self.browser.fill("password", "test")
         self.browser.fill("confirm", "test")
         button = self.browser.find_by_css("button[type=submit]")
         button.click()
         self.assertEqual(self.browser.url, "http://127.0.0.1:8080/signup")
    
    def test_signup_email_already_exists(self):
         self.browser.visit("http://127.0.0.1:8080/signup")
         self.browser.fill("username", "charlie")
         self.browser.fill("email", "alice@example.com")
         self.browser.fill("password", "test")
         self.browser.fill("confirm", "test")
         button = self.browser.find_by_css("button[type=submit]")
         button.click()
         self.assertEqual(self.browser.url, "http://127.0.0.1:8080/signup")
         
    def test_signup_password_mismatch(self):
         self.browser.visit("http://127.0.0.1:8080/signup")
         self.browser.fill("username", "quentin")
         self.browser.fill("email", "abc@example.com")
         self.browser.fill("password", "test")
         self.browser.fill("confirm", "testy")
         button = self.browser.find_by_css("button[type=submit]")
         button.click()
         self.assertEqual(self.browser.url, "http://127.0.0.1:8080/signup")
         
    def test_logout(self):
         self.browser.visit("http://127.0.0.1:8080/logout")
         self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login?next=%2Flogout")

    def tearDown(self):
        """ Test teardown """
        time.sleep(1)
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

if __name__ == "__main__":
    unittest.main()