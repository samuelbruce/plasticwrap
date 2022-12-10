
import json
import os
import re
import requests
import subprocess
import time

class PlasticWrap:
    def __init__(self, api_url="http://localhost:9090/api/v1"):
        self.api_url = api_url
        self.api_process = None
        method_definitions = json.load(open(os.path.join(os.path.dirname(__file__), "method_definitions.json"), "r"))
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
    
    def request(self, http_method, url, json_params):
        print(http_method)
        print(url)
        print(json_params)
        if json_params:
            response = requests.request(http_method, url, json=json_params)
        else:
            response = requests.request(http_method, url, json=[])
        print(response.status_code)
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        return None
     
    """
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
    def __init__(self, parent, http_method, url_endpoint, query=False, json_params=[]):
        self.parent = parent
        self.http_method = http_method
        self.url_endpoint = url_endpoint
        self.url_params = [x[2:] for x in re.findall('/:\w{1,}', url_endpoint)]
        self.query = query
        self.json_params = json_params
    
    def __call__(self, *args, **kwargs):
        url = self.parent.api_url + self.url_endpoint
        if self.url_params:
            for url_param in self.url_params:
                url_value = kwargs.get(url_param)
                try:
                    url = url.replace(":" + url_param, url_value)
                except TypeError:
                    # raise an exception?
                    pass
        if self.query:
            q = kwargs.get("q")
            if q:
                url = url + "?q=" + q
        json_params = {}
        if self.json_params:
            for json_param in self.json_params:
                p = kwargs.get(json_param)
                if p:
                    json_params.update({json_param: p})
                else:
                    # raise an exception?
                    pass
        # TODO: parse the response json
        # TODO: handle response 204 No Content
        return self.parent.request(self.http_method, url, json_params)


class PlasticWrapMethodFactory():
    def __init__(self, parent, definitions):
        self.parent = parent
        self.definitions = definitions
    
    def generate_functions(self):
        for definition in self.definitions:
            method_name = definition["method_name"]
            http_method = definition["http_method"]
            url_endpoint = definition["url_endpoint"]
            try:
                url_params = definition["url_params"]
            except KeyError:
                url_params = []
            try:
                query = definition["query"]
            except KeyError:
                query = False
            try:
                json_params = definition["json_params"]
            except KeyError:
                json_params = []
            method = PlasticWrapMethod(self.parent, http_method, url_endpoint, query, json_params)
            setattr(self.parent, method_name, method)