from array import array
from ast import FormattedValue
from cgitb import text
from contextlib import nullcontext
from curses import flash
import os
from tkinter import N
from tokenize import String
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):

    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    print(page)
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response


    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            formatted_categories = [category.format() for category in categories]
            categories_dict = {item['id']:item['type'] for item in formatted_categories}
        except:
            abort(500)
        return jsonify({
            'success': True,
            'categories':categories_dict,
            'total_categories':len(formatted_categories)
            })


    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def retrieve_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            categories = [category.format() for category in Category.query.all()]
            categories_dict = {item['id']:item['type'] for item in categories}
        except:
            abort(500)
        
        return jsonify(
            {
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "current_category":"all",
                "categories" : categories_dict
            }
        )
    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions')
    def get_byCategory(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()
        if category is None:
            abort(404)
        else:
            selection = Question.query.filter_by(category = category.id).all()
            current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)
        
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "current_category":category.type
               
            }
        )

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question != None:
            question.delete()
        else:
            abort(404)
        
        return jsonify(
            {
                "success": True,
                "deleted": question_id,
            }
        )
            

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions/add", methods=["POST"])
    def add_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        try:
            question = Question(question=new_question, answer =new_answer, category=category, difficulty=difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions" , methods=['POST'])
    def search_question():
        body = request.get_json()
        searchTerm = body.get("searchTerm", None)

        """
            selection = all questions which have the "searchTerm" substring
        """
        selection = Question.query.filter(Question.question.ilike("%"+ searchTerm +"%")).all()
        result_questions = paginate_questions(request, selection)
        
        return jsonify(
            {
                "questions": result_questions,
                "total_questions": len(selection),
                "current_category": "all"    
            }
        )

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/play/quizzes' , methods=['POST'])
    def post_quiz():
        category = request.args.get('category',1,type=int)
        prev_questions = request.args.get('previousQuestions')
    
        if prev_questions != "":
            prevQuestions_array  = prev_questions.split(',')
        else:
            prevQuestions_array = ['']

        """
            get questions of a certain CATEGORY if category argument is not 0, 
            else get all questions
        """
        if category != 0:
                all_questionsInCategory = Question.query.filter_by(category = category).all()
                if len(all_questionsInCategory) == 0:
                    abort(422)
        else:
            all_questionsInCategory = Question.query.all()
        
        """
            format() all the questions to Dict.
            Then delete question from quizzes(array of Dict questions) if questions ID is in previous questions.
        """

        quizzes = [question.format() for question in all_questionsInCategory]
        for i in prevQuestions_array:
            for q in quizzes:  
                if str(q['id']) == i:
                    quizzes.remove(q)

        random.shuffle(quizzes) #randomize final question list to be used
       
        question_ = quizzes[0] if len(quizzes) != 0 else {}

        return jsonify({
            "question" : question_,
        })
        

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error":404,
            "message" : "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error":400,
            "message" : "bad request"
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "error":422,
            "message" : "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "error":500,
            "message" : "server error"
        }), 500

    return app

