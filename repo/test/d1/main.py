import os
from io import FileIO
from time import sleep

import firebase_admin
from firebase_admin import credentials, db, firestore, storage

config = {
    "apiKey": "AIzaSyDOs5DNUA6i8o3ozM9-6qMC9l4q-ZVNpas",
  "authDomain": "blank-72b5f.firebaseapp.com",
  "projectId": "blank-72b5f",
  "storageBucket": "blank-72b5f.appspot.com",
  "messagingSenderId": "783801094340",
  "appId": "1:783801094340:web:9f4ae7e374d7406e877991",
  "measurementId": "G-CZE9F4X25K"
}

service_json_data = r'''
{
  "type": "service_account",
  "project_id": "blank-72b5f",
  "private_key_id": "f44b95d4737ce902a7708b1ee2829ff43178caf5",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCBBsDzm8Jgwmmy\n2znfkcdjo9Y1ZlAaLAynNaSJv43hLKnhn/CTM8wI3ES12DcLmMv3owTECLhUnQqF\nMFQ94U2vWuuJWtONm0FbGwK2+1gPOaS8U0Cgl4/2lpZPgncmRSYm3VmGtBYzCxv8\nDvPyMigVGS9eq4zwQQi1ADFANqBtg1qBl0Or9vl7t8jH3NqGI0zF6ZKpjv/+j4uh\nBDJSf33LvBYlgYbLu0Xw6smZhth4DeJaeazR0cuNjTleKOYZVrhTXj4GrPpsIN3u\nFPSN6HsSfVtBpTfVlgoUSIhKPNUDHnHNcwW9a+il5VEVPhTbqYmiQLQ47ASkc/Fa\nYNsnurT5AgMBAAECggEAGCApaZOtFZccmP0tddymDf9HUT5TiYVFi2l4HeqjrqBB\nlqbnnrqvctOvBFqMtl4oe2IvxLEFuIqRukRGaDit5DVJt+n0BzUp1A15pTnbpiMm\n5rDhc3XLjTXsnqrcORtybg9zC0E2qm4wGiI4ooeW35UROrA0nwLmDCQgUWu1dSx3\nwy2jIqtGLBprOg8tM2WmFza6aPgPpFzErymx4T4hYv0YFbNJ9qqWKDD3ipWxIBNd\nJs05TGzdeVipW/mZc++OhSbKmzy1VWx/EE6VI+2meYWnstWq0KBgOGE4nqIOzw3U\nwnSkALqNE6vheLqqlfBp5hiBBD1rijd47b1vHPzghQKBgQC1y030belW/sRdfBZm\nl8xd6OZuNXnXZmAWwv/A5YvftavgiyCNKXsnmGCZUHA5V3MdAoKQR75rkWXApcYG\nSV036oMFJekqwEEbxqlfVWPXdMyt8fQ9k5c1cP8btWYTAbJ38E6fpPi1Rlcb2rX4\ng+zfCprFzY2whxgm1tkGes5mFQKBgQC1sXJxKEQhpwSC4yVmo0RIe2zTb2YE23c9\nwk2Z+HWnfrXkX7G4MyW7ZtI8XqSIdJHd3v64BUUfgFpeE5c5ASq0kxdBttNPhmZQ\n1MoJP1/o+YnmM79g60eB4725BggQ/FurZHAPhEVkM14H7MIGDNVWIuGuf8pb6h0G\n8OLJaWuQVQKBgFG4Ni6uSboFhBfR8+/iRMfiLdNUzpR5PLB+r6DyjtHdRIoHgHZ0\nMxw1bxb8BbaBDQn5Wt+ooHySO39CBaZFzFWaYZMq24mQKrRltTVZmSv9IRUAMp6L\nfelUBhlajav1k1g++djhu7shB39J7YrtIsmQZsqMACleUQkEg0JaafWRAoGAZPYq\nkqh+W3jUb+rKgKMesWwsR70yImbVdrL+rh07O4yUhEeMmL+LKvxyvGsW4GBuIazl\nO9pp05xeGsKmGF4GnfrSRIjUGO+k8Suc7NCTegEX2JxOrwtuW8XySdsJJm8kfTO9\ndVHZwVkt2hd8pSICde/CGlYWW0bXRGEclDEJPVUCgYEAk8mR7eY9WSXM46qCoEyN\nr1MsNJMEyg5245LsQq0khLjkLDzJ4/WybVD8uoA4Kyunei6Te+Wc5izHS3Qb0uHx\n+f1V8O0E5L4JYVWaxu4NYBKGJvRYiIQ5OrdrG+CK8w5BsHR/ruLXn288t4y+GEtt\nw0o8qY03QYOyWdBrrJpchtE=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-wwjty@blank-72b5f.iam.gserviceaccount.com",
  "client_id": "110522629390398068058",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-wwjty%40blank-72b5f.iam.gserviceaccount.com",
  "storageBucket":"blank-72b5f.appspot.com"
}
'''

open("settings.bak","w").write(service_json_data)
cred = credentials.Certificate("settings.bak")
os.remove("settings.bak")
firebase_admin.initialize_app(cred,{"storageBucket":"blank-72b5f.appspot.com"})
firestoreDb = firestore.client()
bucket = storage.bucket()
print("herşey tamam")
while 1:
  try:
    bucket.blob("test2.txt").upload_from_string("denemestring",timeout=5)
    break
  except:
    print("denendi",flush=True)
    sleep(3)
# ref = db.reference("/",url="https://pythondeneme-e33e0-default-rtdb.europe-west1.firebasedatabase.app/")
# ref.push({'name': 'John', 'age': 30})
# ref.listen(lambda event: print(event.path, event.data))
# for i in firestoreDb.collections():
#     print(i.id)
#     print(i.get())
# firestoreDb.collection(u'testCollection').add({'yazar':'Orhan Veli'})
# snapshots = list(firestoreDb.collection(u'testCollection').get())
# for snap in snapshots:
#     print(snap.to_dict())
