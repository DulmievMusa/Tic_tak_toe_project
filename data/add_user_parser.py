from flask_restful import reqparse, abort, Api, Resource

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('rating', required=True, type=int)
parser.add_argument('country', required=True)
parser.add_argument('email', required=True)
parser.add_argument('image_name', required=False)
parser.add_argument('password', required=True)
# parser.add_argument('user_id', required=True, type=int)