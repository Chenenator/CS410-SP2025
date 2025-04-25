import requests

res = requests.post("https://thingsboard.cloud/api/auth/login", json={
    "username": "dennis.wong002@umb.edu",
    "password": "123456"
})

print(res.json()["token"])
