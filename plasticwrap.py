
import json
import requests
import subprocess
import sys
import time

class PlasticWrap:
    def __init__(self, api_url="http://localhost:9090/api/v1"):
        self.api_url = api_url
        self.api_process = None
        # try a simple request, invoke cm api if it fails
        try:
            requests.get(api_url)
        except requests.ConnectionError:
            print("Starting Plastic API")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            self.api_process = subprocess.Popen(r"cm api", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            time.sleep(2.5)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.api_process is not None:
            self.api_process.terminate()
    
    def get_repos(self):
        url = self.api_url + "/repos"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_workspaces(self):
        url = self.api_url + "/wkspaces"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_switch_status(self, workspace):
        url = self.api_url + "/wkspaces/" + workspace + "/switch"
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.content)["status"]
        return None
    
    def switch_workspace(self, workspace, objectType, object):
        url = self.api_url + "/wkspaces/" + workspace + "/switch"
        params = {"objectType": objectType, "object": object}
        response = requests.post(url, json=params)
        if response.status_code == 200:
            return True
        return None
    
    def get_changes(self, workspace, types=None):
        url = self.api_url + "/wkspaces/" + workspace + "/changes"
        if types is None: types = "changed"
        params = {"types": types}
        response = requests.get(url, json=params)
        if response.status_code == 200:
            return json.loads(response.content)
        return None
    
    def undo_changes(self, workspace, paths):
        url = self.api_url + "/wkspaces/" + workspace + "/changes"
        params = {"paths": paths}
        response = requests.delete(url, json=params)
        if response.status_code == 200:
            return json.loads(response.content)
        return None
    
    def checkout(self, workspace, path):
        url = self.api_url + "/wkspaces/" + workspace + "/content/" + path
        response = requests.put(url)
        if response.status_code == 200:
            return json.loads(response.content)
        return None
    
    def move(self, workspace, path, destination):
        url = self.api_url + "/wkspaces/" + workspace + "/content/" + path
        params = {"destination": destination}
        response = requests.patch(url, json=params)
        if response.status_code == 200:
            return json.loads(response.content)
        return None
