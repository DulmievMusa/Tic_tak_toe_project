from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.users import User
from data.add_user_parser import parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.close()
        return jsonify({'user': user.to_dict()})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        user.name = args['name']
        user.rating = args['rating']
        user.country = args['country']
        user.email = args['email']
        user.image_name = args['image_name']
        user.set_password(args['password'])
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        session.close()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            rating=args['rating'],
            country=args['country'],
            email=args['email'],
        )
        session.add(user)
        user.image_name = user.email
        user.set_password(args['password'])
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})