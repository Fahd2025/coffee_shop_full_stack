import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import sys

app = Flask(__name__)
setup_db(app)
CORS(app)


# The after_request decorator to set Access-Control-Allow
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, PATCH, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/')
def index():
    return jsonify({'Project': 'Coffee Shop Full Stack'})


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@cross_origin()
@app.route("/drinks")
def get_drinks():
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception:
        # exception details
        print('\n * Error:\n', sys.exc_info(), '\n')
        # Server error
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@cross_origin()
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception:
        # exception details
        print('\n * Error:\n', sys.exc_info(), '\n')
        # Server error
        abort(500)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@cross_origin()
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(token):

    request_json = request.get_json()

    title = request_json.get('title', None)
    if title is None:
        # Unprocessable error
        abort(422)

    recipe = request_json.get('recipe', None)

    new_drink = Drink(title=title)
    if recipe is not None:
        new_drink.recipe = json.dumps(recipe)

    try:

        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })
    except Exception:
        # exception details
        print('\n * Error:\n', sys.exc_info(), '\n')
        # Server error
        abort(500)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@cross_origin()
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(token, drink_id):
    request_json = request.get_json()

    title = request_json.get('title', None)
    if title is None:
        # Unprocessable error
        abort(422)

    recipe = request_json.get('recipe', None)

    edit_drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if edit_drink is None:
        # Not found
        abort(404)

    edit_drink.title = title
    if recipe is not None:
        edit_drink.recipe = json.dumps(recipe)

    try:
        edit_drink.update()

        return jsonify({
            'success': True,
            'drinks': [edit_drink.long()]
        })
    except Exception:
        # exception details
        print('\n * Error:\n', sys.exc_info(), '\n')
        # Server error
        abort(500)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@cross_origin()
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, drink_id):
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except Exception:
        # exception details
        print('\n * Error:\n', sys.exc_info(), '\n')
        # Server error
        abort(500)


'''
Error handlers for expected errors
'''


# catch auth error
@app.errorhandler(AuthError)
def catch_auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


# catch bad request 400
@app.errorhandler(400)
def catch_bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request error'
    }), 400


# catch unauthorized 401
@app.errorhandler(401)
def catch_unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized error'
    }), 401


# catch not found error 404
@app.errorhandler(404)
def catch_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found'
    }), 404


# catch Method not allowed 405
@app.errorhandler(405)
def catch_method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
    }), 405


# catch unprocessable error 422
@app.errorhandler(422)
def catch_unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable error'
    }), 422


# catch server error 500
@app.errorhandler(500)
def catch_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error has been occured'
    }), 500


# Launch
if __name__ == '__main__':
    app.run()
