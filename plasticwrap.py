
import json
import re
import requests
import subprocess
import sys
import time

class PlasticWrap:
    def __init__(self, api_url="http://localhost:9090/api/v1"):
        self.api_url = api_url
        self.api_process = None
        method_definitions = [ { "method_name": "get_repos", "url_endpoint": "/repos" } ]
        method_factory = PlasticWrapMethodFactory(self, method_definitions)
        method_factory.generate_functions()
    
    def __enter__(self):
        self._connect()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.api_process is not None:
            self.api_process.terminate()
    
    def _connect(self):
        # try a simple request, invoke cm api if it fails
        try:
            requests.get(self.api_url)
        except requests.ConnectionError:
            print("Starting Plastic API")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESTDHANDLES | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            self.api_process = subprocess.Popen(r"cm api", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            time.sleep(2.5)
    
    def _req(self, method, url, params, data):
        url = self.api_url + url
        response = requests.request(method=method, url=url, params=params, json=data)
        return response
    
    def _delete(self, url, params, data):
        return _req(method="DELETE", url=url, params=params, data=data)
    
    def _get(self, url, params, data):
        return _req(method="GET", url=url, params=params, data=data)
    
    def _patch(self, url, params, data):
        return _req(method="PATCH", url=url, params=params, data=data)
    
    def _post(self, url, params, data):
        return _req(method="POST", url=url, params=params, data=data)
    
    def _put(self, url, params, data):
        return _req(method="PUT", url=url, params=params, data=data)
    
    def _append_url(func):
        def wrapper(self, *args, **kwargs):
            url = func.__kwdefaults__["url"]
            if ':' in url:
                matches = re.findall('/:\w{1,}', url)
                for match in matches:
                    key = match[2:]
                    val = kwargs.get(key)
                    url = url.replace(match[1:], val)
            url = self.api_url + url
            return url
        return wrapper

    @_append_url
    def test_append_url(self, *, url="/repos/:repname/branches/:branchname/changesets"):
        return url
    
    """
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
    """

class PlasticWrapMethod():
    def __init__(self, parent, url_endpoint, url_params=[]):
        self.parent = parent
        self.url_endpoint = url_endpoint
        self.url_params = url_params
    
    def __call__(self, *args, **kwargs):
        url = self.parent.api_url + self.url_endpoint
        if self.url_params:
            for url_param in self.url_params:
                url_value = kwargs.get(url_param)
                url = url.replace(":" + url_param, url_value)
        return url


class PlasticWrapMethodFactory():
    def __init__(self, parent, definitions):
        self.parent = parent
        self.definitions = definitions
    
    def generate_functions(self):
        for definition in self.definitions:
            method_name = definition["method_name"]
            url_endpoint = definition["url_endpoint"]
            try:
                url_params = definition["url_params"]
            except KeyError:
                url_params = []
            method = PlasticWrapMethod(self.parent, url_endpoint, url_params)
            setattr(self.parent, method_name, method)