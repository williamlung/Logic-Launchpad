import requests
from io import StringIO
import traceback

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
        
class ManageTools:
    def __init__(self, url, week) -> None:
        self.url = url
        self.week = week
    
    def login(self, username, password):
        try:
            url = "http://"+self.url+"/api/token/"
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(url, data=data).json()
            if "access" in response:
                self.access_token = response['access']
                return True, "Login successful."
            else:
                return False, "Invalid username or password."
        except:
            return False, "Unable to connect to server."
        
    def create_test_case(self, question_id: int, input: str, output: str, hidden: bool):
        try:
            url = "http://"+self.url+"/api/create/testcase/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            files = {
                'input': StringIO(input),
                'output': StringIO(output)
            }
            data = {
                'question_id': question_id,
                'hidden': hidden
            }
            response = requests.post(url, headers=headers, data=data, files=files).json()
            return response
        except:
            traceback.print_exc()
            return None
    
    def create_question(self, title: str, description: str, start_code_template: str):
        try:
            url = "http://"+self.url+"/api/create/question/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            files = {
                'start_code_template_file': StringIO(start_code_template)
            }
            data = {
                'title': title,
                'description': description,
                'week': self.week
            }
            response = requests.post(url, headers=headers, data=data, files=files).json()
            return response
        except:
            traceback.print_exc()
            return None

    def get_questions(self):
        try:
            url = "http://"+self.url+f"/api/get/questions/{self.week}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.get(url, headers=headers).json()
            return response
        except:
            traceback.print_exc()
            return None

    def get_question_info(self, question_id):
        try:
            url = "http://"+self.url+"/api/get/question/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            params = {
                'id': question_id
            }
            response = requests.get(url, headers=headers, params=params).json()
            return response
        except:
            traceback.print_exc()
            return None
    
    def delete_question(self, question_id):
        try:
            url = "http://"+self.url+"/api/delete/question/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            data = {
                'id': question_id
            }
            response = requests.post(url, headers=headers, data=data).json()
            return response
        except:
            traceback.print_exc()
            return None

    def update_question(self, question_id, title, description, start_code_template):
        try:
            url = "http://"+self.url+"/api/update/question/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            files = {
                'start_code_template_file': StringIO(start_code_template)
            }
            data = {
                'id': question_id,
                'title': title,
                'description': description
            }
            response = requests.post(url, headers=headers, data=data, files=files).json()
            return response
        except:
            traceback.print_exc()
            return None
    
    def get_test_cases(self, qid):
        try:
            url = "http://"+self.url+"/api/get/testcases/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            params = {
                'question_id': qid
            }
            response = requests.get(url, headers=headers, params=params).json()
            return response
        except:
            traceback.print_exc()
            return None
    
    def delete_test_case(self, tid):
        try:
            url = "http://"+self.url+"/api/delete/testcase/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            params = {
                'test_case_id': tid
            }
            response = requests.delete(url, headers=headers, params=params).json()
            return response
        except:
            traceback.print_exc()
            return None

    def validate_test_cases(self, qid, code):
        try:
            url = "http://"+self.url+"/api/validate/testcases/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            data = {
                'question_id': qid,
            }
            files = {
                'code': StringIO(code)
            }
            response = requests.post(url, headers=headers, data=data, files=files).json()
            return response
        except:
            traceback.print_exc()
            return None
    
    def get_user_list(self, qid):
        try:
            url = "http://"+self.url+"/api/get/userlist/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            params = {
                'question_id': qid
            }
            response = requests.get(url, headers=headers, params=params).json()
            return response
        except:
            traceback.print_exc()
            return None

    def create_user(self, username, password):
        try:
            url = "http://"+self.url+"/api/create/user/"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(url, headers=headers, data=data).json()
            return response
        except:
            traceback.print_exc()
            return None
        
if __name__ == "__main__":
    manager = ManageTools("localhost:8000", 1)
    manager.login("abc", "abc")
    print(manager.create_test_case(1, "", "", False))