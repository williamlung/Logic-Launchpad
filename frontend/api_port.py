import requests
from io import StringIO
import traceback

class API_Loader:
    def __init__(self, url: str) -> None:
        self.url = url

    def login(self, username: str, password: str):
        try:
            url = "http://" + self.url + "/api/token/"
            data = {
                "username": username,
                "password": password
            }
            response = requests.post(url, data=data).json()
            if "access" in response:
                self.access_token = response["access"]
                self.refresh_token = response["refresh"]
                return True, "Login successful."
            else:
                return False, "Invalid username or password."
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."

    def valid_token(self, token: str):
        try:
            url = "http://" + self.url + "/api/token/verify/"
            data = {
                "token": token
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            traceback.print_exc()
            return False

    def get_access_token(self):
        if self.valid_token(self.access_token):
            return 'Bearer ' + self.access_token
        else:
            if self.valid_token(self.refresh_token):
                url = "http://" + self.url + "/api/token/refresh/"
                data = {
                    "refresh": self.refresh_token
                }
                response = requests.post(url, data=data).json()
                if "access" in response:
                    self.access_token = response["access"]
                    return 'Bearer ' + self.access_token
                else:
                    return None
            else:
                return None

    def get_questions(self):
        try:
            token = self.get_access_token()
            if token is None:
                return False, "Please login again."
            url = "http://" + self.url + "/api/get/questions/"
            headers = {'Authorization': token}
            response = requests.get(url, headers=headers).json()
            return True, response
        except:
            traceback.print_exc()
            return False, None
    
    def get_question_info(self, question_id: int):
        try:
            token = self.get_access_token()
            if token is None:
                return False, "Please login again."
            url = "http://" + self.url + "/api/get/question/"
            headers = {'Authorization': token}
            params = {
                "id": question_id
            }
            response = requests.get(url, headers=headers, params=params).json()
            return True, response
        except:
            traceback.print_exc()
            return False, None
    
    def submit_answer(self, question_id: int, answer: str):
        try:
            token = self.get_access_token()
            if token is None:
                return False, "Please login again."
            url = "http://" + self.url + "/api/submit/answer/"
            headers = {'Authorization': token}
            data = {
                "question_id": question_id,
            }
            files = {
                "answer": StringIO(answer)
            }
            response = requests.post(url, headers=headers, data=data, files=files).json()
            return True, response
        except:
            traceback.print_exc()
            return False, None
    
    def get_last_submit_answer(self, question_id: int):
        try:
            token = self.get_access_token()
            if token is None:
                return False, "Please login again."
            url = "http://" + self.url + "/api/get/question/answer/"
            headers = {'Authorization': token}
            params = {
                "question_id": question_id
            }
            response = requests.get(url, headers=headers, params=params).json()
            return True, response
        except:
            traceback.print_exc()
            return False, None
        
class ManageTools:
    def __init__(self, url, week) -> None:
        self.url = url
        self.week = week
    
    def login(self, username: str, password: str):
        try:
            url = "http://"+self.url+"/api/token/"
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(url, data=data).json()
            if "access" in response:
                self.access_token = response['access']
                self.refresh_token = response['refresh']
                return True, "Login successful."
            else:
                return False, "Invalid username or password."
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."
        
    def valid_token(self, token: str):
        try:
            url = "http://"+self.url+"/api/token/verify/"
            data = {
                'token': token
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            traceback.print_exc()
            return False
        
    def get_access_toekn(self):
        if self.valid_token(self.access_token):
            return 'Bearer ' + self.access_token
        else:
            if self.valid_token(self.refresh_token):
                url = "http://"+self.url+"/api/token/refresh/"
                data = {
                    'refresh': self.refresh_token
                }
                response = requests.post(url, data=data).json()
                if "access" in response:
                    self.access_token = response['access']
                    return 'Bearer ' + self.access_token
                else:
                    return None
            else:
                return None

    def create_test_case(self, question_id: int, input: str, output: str, hidden: bool):
        try:
            access_token = self.get_access_toekn()
            if access_token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/create/testcase/"
            headers = {
                'Authorization': access_token
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
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."
    
    def create_question(self, title: str, description: str, start_code_template: str):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/create/question/"
            headers = {
                'Authorization': token
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
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."

    def get_questions(self):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+f"/api/get/questions/{self.week}"
            headers = {
                'Authorization': token
            }
            response = requests.get(url, headers=headers).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."

    def get_question_info(self, question_id):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/get/question/"
            headers = {
                'Authorization': token
            }
            params = {
                'id': question_id
            }
            response = requests.get(url, headers=headers, params=params).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."
    
    def delete_question(self, question_id):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/delete/question/"
            headers = {
                'Authorization': token
            }
            data = {
                'id': question_id
            }
            response = requests.post(url, headers=headers, data=data).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."

    def update_question(self, question_id, title, description, start_code_template):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/update/question/"
            headers = {
                'Authorization': token
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
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."
    
    def get_test_cases(self, qid):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/get/testcases/"
            headers = {
                'Authorization': token
            }
            params = {
                'question_id': qid
            }
            response = requests.get(url, headers=headers, params=params).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."
    
    def delete_test_case(self, tid):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/delete/testcase/"
            headers = {
                'Authorization': token
            }
            params = {
                'test_case_id': tid
            }
            response = requests.delete(url, headers=headers, params=params).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."

    def validate_test_cases(self, qid, code):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/validate/testcases/"
            headers = {
                'Authorization': token
            }
            data = {
                'question_id': qid,
            }
            files = {
                'code': StringIO(code)
            }
            response = requests.post(url, headers=headers, data=data, files=files).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."
    
    def get_user_list(self, qid):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/get/userlist/"
            headers = {
                'Authorization': token
            }
            params = {
                'question_id': qid
            }
            response = requests.get(url, headers=headers, params=params).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."

    def create_user(self, username, password):
        try:
            token = self.get_access_toekn()
            if token is None:
                return False, "Please login again."
            url = "http://"+self.url+"/api/create/user/"
            headers = {
                'Authorization': token
            }
            data = {
                'username': username,
                'password': password
            }
            response = requests.post(url, headers=headers, data=data).json()
            return True, response
        except:
            traceback.print_exc()
            return False, "Unable to connect to server."
        
if __name__ == "__main__":
    manager = ManageTools("localhost:8000", 1)
    manager.login("abc", "abc")
    manager.create_question("The start of your programming journey", "You just need to enter submit button.", "int main() {\n    return 0;\n}\n")
    manager.create_test_case(1, "on99", "", True)
    manager.create_test_case(1, "", "", True)
    manager.create_test_case(1, "1222", "", False)
    manager.create_test_case(1, "555667", "", False)
    manager.create_test_case(1, "235236326", "", False)
    manager.create_test_case(1, "dfsjnigifsdgjofds", "", False)
    manager.create_test_case(1, "你好成功", "", False)

    manager.create_question("Say Hello to the World!", "Please try to print 'Hello World!'", "int main() {\n    // write your code here!\n    return 0;\n}\n")
    manager.create_test_case(2, "", "Hello World!", False)
    manager.create_test_case(2, "ggdfh", "Hello World!", True)
    manager.create_test_case(2, "dfhdfhdh", "Hello World!", True)
