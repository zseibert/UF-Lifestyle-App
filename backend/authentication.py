import re
import datetime

import pyrebase
import firebase_admin
from firebase_admin import auth

email_regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

config = {
    "apiKey": "AIzaSyC4_b2Kf-65XVZ6vqCyn_B0hbNLrTDXgZc",
    "authDomain": "uf-lifestyle.firebaseapp.com",
    "databaseURL": "https://uf-lifestyle.firebaseio.com",
    "projectId": "uf-lifestyle",
    "storageBucket": "uf-lifestyle.appspot.com",
    "messagingSenderId": "540721409323",
    "appId": "1:540721409323:web:d7a16aef5c536f0f02696e",
    "measurementId": "G-BZYLF7CKJB",
    "serviceAccount" : "uf-lifestyle-firebase-adminsdk.json"
}

def isEmailValid(email):
    if not isinstance(email, str):
            raise TypeError('ERROR email must be of type str')
    else:
        return re.search(email_regex, email)

class AuthDatabase:

    def __init__(self):
        self._firebase = pyrebase.initialize_app(config)
        self._auth = self._firebase.auth()
        self._db = self._firebase.database()

    def authenticate_user(self, email, password):
        if not isinstance(email, str):
                raise TypeError('ERROR email must be of type str')

        if not isinstance(password, str):
            raise TypeError('ERROR password must be of type str')

        if not (isEmailValid(email)):
            raise SyntaxError('ERROR a valid email must be provided')

        return self._auth.sign_in_with_email_and_password(email,password)['idToken']

    def _get_userID_from_authID(self, auth_id):
        return self._auth.get_account_info(auth_id)["users"][0]['localId']

    def get_account_info(self,auth_id,account_name):
        user_id = self._get_userID_from_authID(auth_id)
        return self._db.child('users').child(user_id).child(account_name).get(auth_id).val()

    # Creates new user in database based on their email and password
    def create_new_user(self, email, password):
        if not isinstance(email, str):
            raise TypeError('ERROR email must be of type str')

        if not isinstance(password, str):
            raise TypeError('ERROR password must be of type str')

        if not (isEmailValid(email)):
            raise SyntaxError('ERROR a valid email must be provided')

        if len(password) < 8:
            raise ValueError('ERROR passwords must be at least 8 characters in length')

        auth_id = self._auth.create_user_with_email_and_password(email,password)['idToken']
        user_id = self._get_userID_from_authID(auth_id)

        # data = {"/users/" + user_id : {"default" : "json"}}
        # self._db.update(data)
        return auth_id

    def add_daily_entry(self, auth_id, date, timespent):
        date = date.replace(r'/', ":")
        date = date[:-2]
        user_id = self._get_userID_from_authID(auth_id)
        self._db.child("users").child(user_id).child(date).update(timespent)

    def update_weekly_goal(self, auth_id, goal):
        date = "" + str(datetime.datetime.now().strftime("%x"))
        date = date.replace(r'/', ":")
        user_id = self._get_userID_from_authID(auth_id)
        self._db.child("users").child(user_id).child("weeklygoal").update(goal)
        self._db.child("users").child(user_id).update({"weeklygoalstart" : date})

    def get_daily_entry(self, auth_id, date):
        # date needs to be in format month:day:year eg 01:01:20
        user_id = self._get_userID_from_authID(auth_id)
        return  self._db.child('users').child(user_id).child(date).get().val()

    def get_weekly_goal(self, auth_id):
        user_id = self._get_userID_from_authID(auth_id)
        ret = self._db.child('users').child(user_id).child('weeklygoal').get().val()
        start = self._db.child('users').child(user_id).child('weeklygoalstart').get().val()
        ret.update({'weeklygoalstart' : start})
        return ret

    def get_report_data(self, auth_id, start, end):
        data = {}
        startDate = datetime.date(int(start[6:10]), int(start[0:2]), int(start[3:5]))
        endDate = datetime.date(int(end[6:10]), int(end[0:2]), int(end[3:5]))
        for n in range(int((endDate - startDate).days) + 1):
            date = (startDate + datetime.timedelta(n)).strftime("%x")
            date = date.replace(r'/', ":")
            dailyData = self.get_daily_entry(auth_id, date)
            if dailyData is not None:
                temp = {date :
                        {'Class' : int(dailyData['class']),
                        'Study' : int(dailyData['study']),
                        'Social' : int(dailyData['social']),
                        'Exercise' : int(dailyData['exercise']),
                        'Leisure' : int(dailyData['leisure']),
                        'Sleep' : int(dailyData['sleep']),
                        'Other' : int(dailyData['other']),
                        'Stress' : int(dailyData['stress'])}
                        }
                data.update(temp)
            else:
                temp = {date :
                        {'Class' :0,
                        'Study' : 0,
                        'Social' : 0,
                        'Exercise' : 0,
                        'Leisure' : 0,
                        'Sleep' : 0,
                        'Other' : 0,
                        'Stress' : 0}
                        }
                data.update(temp)
        return data

# if __name__ == '__main__':
#     db = AuthDatabase()
#     auth_id = db.authenticate_user("test144f2@test.com", "password")
#     data = {"something" : "one", 1 : "two", "3" : "five"}
#     db.add_daily_entry(auth_id, data)
#     # print(db.get_weekly_goal(auth_id))