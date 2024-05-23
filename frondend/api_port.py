import requests

class API_Loader:
    def __init__(self, url) -> None:
        self.url = url

    def login(self, username, password):
        try:
            url = "http://" + self.url + "/api/token/"
            data = {
                "username": username,
                "password": password
            }
            response = requests.post(url, data=data).json()
            if "access" in response:
                self.access_token = response["access"]
                return True, "Login successful."
            else:
                return False, "Invalid username or password."
        except:
            return False, "Unable to connect to server."

    def get_questions(self):
        try:
            url = "http://" + self.url + "/api/get/questions/"
            headers = {'Authorization': 'Bearer ' + self.access_token}
            response = requests.get(url, headers=headers).json()
            return response
        except:
            return None
    
    def get_question_info(self, question_id):
        try:
            url = "http://" + self.url + "/api/get/question/"
            headers = {'Authorization': 'Bearer ' + self.access_token}
            params = {
                "id": question_id
            }
            response = requests.get(url, headers=headers, params=params).json()
            return response
        except:
            return None