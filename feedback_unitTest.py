import unittest
from app import app
from flask import session

class APPTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_feedback_html(self):
        with app.test_client() as client:
            response = client.get('/feedback')
            data = response.get_data(as_text=True)
            self.assertIn('ShoesStore - Feedback', data)

    def test_post_comment(self):
        # with app.test_request_context():
        client=app.test_client()
        with client.session_transaction() as session:
            session['uid'] = 17
            session['user'] ="aaa"
        comment="nice shoes"
        response = client.post('/feedback', data=dict(
            content=comment,
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn(comment, data)

        
if __name__ == '__main__':
    unittest.main()
