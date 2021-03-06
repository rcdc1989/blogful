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
        
        #handle odd situation where database somehow still contains something..
        Base.metadata.drop_all(engine)
        # Set up the tables in the database
        Base.metadata.create_all(engine)
        
        #Create an example user and entry
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
        time.sleep(1)
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
        
    def test_edit_view_entry(self):
        #simulate a login
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        self.browser.visit("http://127.0.0.1:8080/entry/1/edit")
        #time.sleep(5)
        self.browser.fill("title", "test content")
        self.browser.fill("content", "test entry")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/1")
    
    def test_view_entry(self):
        self.browser.visit("http://127.0.0.1:8080/")
        #link = self.browser.find_element_by_link_text("test entry")
        #link = self.browser.findElement(By.xpath("//tag[contains(text(),'test entry')]")
        #self.browser.findElement(By.linkText("Smoke Sequential")).click();
        #time.sleep(10)
        links = self.browser.find_link_by_text('*')
        #links = self.browser.find_link_by_partial_href('test')
        #links = self.browser.find_by_id("1")
        #link = self.browser.find_by_tag("h1")
        #links = self.browser.find_by_css("h1")
        #links = self.browser.find_*()
        print(links)
        links[0].click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/entry/1")
        
    def test_signup(self):
         self.browser.visit("http://127.0.0.1:8080/signup")
         self.browser.fill("username", "betty")
         self.browser.fill("email", "betty@example.com")
         self.browser.fill("password", "test")
         self.browser.fill("confirm", "test")
         button = self.browser.find_by_css("button[type=submit]")
         button.click()
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
         
    def test_delete_entry(self):
        #simulate a login
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        self.browser.visit("http://127.0.0.1:8080/delete/1/confirm")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        # with self.assertRaises(IndexError):
        #     self.browser.visit("http://127.0.0.1:8080/entry/1")
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        
    def test_delete_entry_not_logged_in(self):
        self.browser.visit("http://127.0.0.1:8080/")
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")
        self.browser.visit("http://127.0.0.1:8080/delete/1/confirm")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        time.sleep(1)
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")
            
    
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