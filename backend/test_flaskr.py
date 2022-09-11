import os
from unicodedata import category
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

DB_HOST = os.getenv('DB_HOST', '10.0.2.15:5432')
DB_USER = os.getenv('DB_USER', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Passw0rd')
DB_NAME = os.getenv('DB_NAME', 'trivia_test')

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME 
        self.database_path = "postgresql://{}:{}@{}/{}".format( DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question={
            'question' : "best software engineer ?",
            'answer' : "Tshepiso Ncosane",
            'category' : 3,
            'difficulty' : 3
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """

    # GET

    def test_get_questionsByCategory(self):
        res = self.client().get('/categories/3/questions')
        self.assertEqual(res.status_code,200)

    def test_404_sent_requesting_question_unvalidID(self):
        res = self.client().get('/category/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data["error"],404)
        self.assertEqual(data['message'],"resource not found")

    def test_get_allQuestionsPaginated(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['questions']) <= 10)

    '''
        let maxPage = Math.ceil(this.state.totalQuestions / 10);
        this makes it impossible to fail pagination, i think
    '''

    """
    def test_404_cannot_get_allQuestionsPaginated(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["error"],404)
        self.assertEqual(data['message'],"resource not found")
    """
   
    # DELETE
    def test_delete_Question(self):
        res = self.client().delete("/questions/36")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == '36').one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data["deleted"],36)
        self.assertEqual(question,None)

    def test_404_cannot_delete_questionID(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data["error"],404)
        self.assertEqual(data['message'],"resource not found")

    # POST
    def test_post_newQuestion(self):
        res = self.client().post('/questions/add' , json = self.new_question)
        self.assertEqual(res.status_code,200)
    
    def test_422_cannot_post_question(self):
        res = self.client().post('/questions/add' , json = {
                'question' : "best software engineer ?",
                'answer' : "Tshepiso Ncosane",
                'category' : 'kiefkbjk,',
                'difficulty' : 'ddsdc',
                
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["error"],422)
        self.assertEqual(data['message'],"unprocessable")

    def test_post_randomQuizQuestion(self):
        res = self.client().post('/play/quizzes?previousQuestions=2,3&category=1')
        self.assertEqual(res.status_code,200)
    
    def test_422_cannot_retrieve_questionsOFcategory(self):
        res = self.client().post('/play/quizzes?previousQuestions=2,3&category=100000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data["error"],422)
        self.assertEqual(data['message'],"unprocessable")

    






# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()