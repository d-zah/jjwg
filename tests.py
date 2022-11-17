import unittest
import requests

class FlaskTest(unittest.TestCase):

    def test_index(self):
        response = requests.get("http://127.0.0.1:5000/")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual('<h2>Use this site to maintain and organize your tasks.</h2>' in response.text, True)

    def test_tasks(self):
        response = requests.get("http://127.0.0.1:5000/tasks")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual('Title' and 'Date' in response.text, True)

    def test_task(self):
        response = requests.get("http://127.0.0.1:5000/tasks/1")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual('First task' in response.text, True)

    def test_new(self):
        response = requests.get("http://127.0.0.1:5000/tasks/new")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
        self.assertEqual('<form action="new" method="post">' in response.text, True)

    def test_delete(self):
        response = requests.get('http://127.0.0.1:5000/tasks/delete')
        statuscode = response.status_code
        self.assertEqual(statuscode, 500)

if __name__ == " __main__":
    unittest.main()