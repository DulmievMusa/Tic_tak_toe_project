from requests import get, post, delete, put
print(put('http://127.0.0.1:5000/api/user/2',
           json={
               'name': 'first',
               'rating': 100,
               'country': 'Russia',
               'email': 'h@h',
               'password': 'sdfghj'
           }
           ))