import pyrebase

config = {
    "apiKey": "AIzaSyA5Oj-QhZVpoSP-py4LRb-1IFGqS7EkGi0",
    "authDomain": "pythondeneme-e33e0.firebaseapp.com",
    "databaseURL": "https://pythondeneme-e33e0-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "pythondeneme-e33e0",
    "storageBucket": "pythondeneme-e33e0.appspot.com",
    "messagingSenderId": "355398550099",
    "appId": "1:355398550099:web:46d2f1f0a18c0f38663ca6",
    "serviceAccount": "C:/Users/ertu1/Desktop/blank/test/d1/service.json"
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()
for i in storage.list_files():
    i.download_to_filename("deneme.txt")
