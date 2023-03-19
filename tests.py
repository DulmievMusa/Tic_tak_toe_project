from requests import get, post, delete, put
print(post('http://127.0.0.1:5000/api/users',
           json={
               'name': 'first',
               'rating': 100,
               'country': 'Russia',
               'email': 'h@h',
               'password': 'abcd'
           }
           ))