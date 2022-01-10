import json
import os
from re import search
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    items = [item.format() for item in selection]

    return items[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  """
    CORS(app)

    """
  Use the after_request decorator to set Access-Control-Allow
  """

    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    """
  Create an endpoint to handle GET requests 
  for all available categories.
  """

    @app.route("/categories")
    def get_categories():

        try:
            # get all categories
            categories = Category.query.all()

            # if none abort
            if len(categories) == 0:
                abort(404)

            return jsonify(
                {
                    "success": True,
                    "categories": {cat.id: cat.type for cat in categories},
                    "total_categories": len(categories),
                }
            )
        except:
            abort(500)

    """
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
    def get_questions():

        try:
            selection = Question.query.order_by(Question.id).all()
            current_page = paginate(request, selection)

            categories = {
                cat.id: cat.type
                for cat in Category.query.filter(
                    Category.id.in_(set([cat.category for cat in selection]))
                ).all()
            }

        except:
            abort(422)

        if len(current_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_page,
                "page": request.args.get("page", 1, type=int),
                "total_questions": len(selection),
                "current_category": None,
                "categories": categories,
            }
        )

    """
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  """

    @app.route("/questions/<question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        try:
            question.delete()
            selection = Question.query.all()
            current_page = paginate(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_page,
                    "total_books": len(selection),
                }
            )
        except:
            abort(500)

    """
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  """

    """
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        question_text = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)
        search_term = body.get("searchTerm", None)

        # prevent user from entering already existing question or empty string question/answer
        if (
            (
                question_text == ""
                or answer == ""
                or question_text in [q.question for q in Question.query.all()]
            )
            and (search_term is None)
            and (question_text is not None)
        ):
            abort(400)

        try:
            # if search term is present run search else add question
            if search_term:
                search_results = (
                    Question.query.order_by(Question.id)
                    .filter(Question.question.ilike(f"%{search_term}%"))
                    .all()
                )

                current_page = paginate(request, search_results)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_page,
                        "current_page": request.args.get("page", 1, type=int),
                        "total_questions": len(search_results),
                    }
                )
            # otherwise create new question
            elif question_text:
                new_question = Question(
                    question=question_text,
                    answer=answer,
                    difficulty=difficulty,
                    category=category,
                )

                new_question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_page = paginate(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": new_question.id,
                        "questions": current_page,
                        "current_page": request.args.get("page", 1, type=int),
                        "total_questions": len(Question.query.all()),
                    }
                )
            else:
                abort(400)
        except:
            abort(422)

    """
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  """

    @app.route("/categories/<category_id>/questions")
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter(Question.category == category_id).all()
        except:
            abort(422)

        if len(questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in questions],
                "total_questions": len(questions),
                "current_category": category_id,
            }
        )

    """
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  """

    @app.route("/quizzes", methods=["POST"])
    def generate_quiz():
        try:
            body = request.get_json()

            previous_questions = body.get("previous_questions", None)
            quiz_category = body.get("quiz_category", None)

            # all categories
            if quiz_category["id"] == 0:
                # get random question that has not been used previously
                random_question = (
                    Question.query.filter(Question.id.notin_(previous_questions))
                    .order_by(func.random())
                    .first()
                )
            # specific categories
            else:
                random_question = (
                    Question.query.filter(Question.category == quiz_category["id"])
                    .filter(Question.id.notin_(previous_questions))
                    .order_by(func.random())
                    .first()
                )
            # if no more questions just return true
            if random_question is None:
                return jsonify({"success": True})

            return jsonify({"success": True, "question": random_question.format()})
        except:
            abort(500)

    @app.route("/categories", methods=["POST"])
    def create_category():
        body = request.get_json()

        category_name = body.get("categoryName", None)

        # prevent user from adding empty string category or category that already exists
        if (
            category_name == ""
            or category_name is None
            or category_name in [cat.type for cat in Category.query.all()]
        ):
            abort(400)

        else:
            try:
                new_category = Category(type=category_name)
                new_category.insert()

                all_categories = Category.query.all()

                return jsonify(
                    {
                        "success": True,
                        "new_category_id": new_category.id,
                        "categories": [cat.format() for cat in all_categories],
                        "total_categories": len(all_categories),
                    }
                )

            except:
                abort(500)

    @app.route("/categories/<category_id>", methods=["DELETE"])
    def delete_category(category_id):
        category = Category.query.get(category_id)

        if category is None:
            abort(404)

        else:

            try:
                category.delete()

                all_categories = [cat.format() for cat in Category.query.all()]

                return jsonify(
                    {
                        "success": True,
                        "deleted": category_id,
                        "categories": all_categories,
                        "total_categories": len(all_categories),
                    }
                )
            except:
                abort(500)

    """
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  """

    @app.errorhandler(400)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "bad request: possible duplicate or empty question",
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "internal service error"}
            ),
            500,
        )

    return app
