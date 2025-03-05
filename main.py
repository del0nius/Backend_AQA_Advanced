"""
curl -X 'POST' \
  'http://5.63.153.31:5051/v1/account' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "login": "d.gaponenko_test",
  "email": "d.gaponenko_test@mail.ru",
  "password": "123456789"
}'

curl -X 'PUT' \
  'http://5.63.153.31:5051/v1/account/79a2f11c-d0b4-49bf-9ebc-694612b310a8' \
  -H 'accept: text/plain'
"""
import pprint
import requests

# url = 'http://5.63.153.31:5051/v1/account'
# headers = {
#     'accept': '*/*',
#     'Content-Type': 'application/json'
# }
# json = {
#     "login": "d.gaponenko_test2",
#     "email": "d.gaponenko_test2@mail.ru",
#     "password": "123456789"
# }
#
# response = requests.post(
#     url = url,
#     headers = headers,
#     json = json
# )

url = 'http://5.63.153.31:5051/v1/account/79a2f11c-d0b4-49bf-9ebc-694612b310a8'
headers = {
    'accept': 'text/plain'
}

response = requests.put(
    url = url,
    headers = headers
)

print(response.status_code)
pprint.pprint(response.json())
response_json = response.json()
print(response_json["resource"]["rating"]["quantity"])