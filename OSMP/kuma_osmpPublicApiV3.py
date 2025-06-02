import requests
import json
from typing import Any, Optional, Dict

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Kuma:

    def __init__(self, xdrdomain, token):
        self.session = requests.Session()
        self.session.verify = False
        self.xdrdomain = xdrdomain
        self.token = token
        self.headers = {'Authorization': 'Bearer ' + token}
        self.session.headers.update(self.headers)

    def _make_request(self, method, route, params=None, data=None, files=None, resp_status_code_expected=200, response_type='json'):
        url = 'https://api.{}/xdr/api/v3/kuma/{}'.format(self.xdrdomain, route)

        response = self.session.request(
            method, url,
            params=params,
            json=data,
            files=files
        )
#        print(f"[DEBUG] Route: {route}, Status: {response.status_code}")
        if response.status_code == 204:
            return "[Status 204: OK] Resource is valid!"
        if response.status_code != resp_status_code_expected:
            raise Exception("Wrong result status code " + str(response.status_code) + str(response.text))
        if response.status_code == 200 and '/create' in route:
            return "[Status 200: OK] Created resource!"
        if response.status_code == 200 and method == 'put':
            return "[Status 200: OK] Changed resource!"
        if response_type == 'json':
            return response.json()
        if response_type == 'text':
            return response.text
        if response_type == 'content':
            return response.content

    def make_post_request(self, *args, **kwargs):
        return self._make_request('post', *args, **kwargs)

    def make_get_request(self, *args, **kwargs):
        return self._make_request('get', *args, **kwargs)

    def make_put_request(self, *args, **kwargs):
        return self._make_request('put', *args, **kwargs) 

    def whoami(self):
        return self.make_get_request('users/whoami')

    def get_tenants(self, *args, **kwargs):
        return self.make_get_request('tenants', *args, **kwargs)

    def resources_export(self, ids, password, tenantID):
        data = {
            "ids": ids,
            "password": password,
            "tenantID": tenantID
        }
        return self.make_post_request('resources/export', data = data)

    def resources_download(self, fileID):
        return self.make_get_request('download/' + fileID, response_type='content')

    def resources_search(self, page: int = 1, id: Optional[str] = None, tenantID: Optional[str] = None, name: Optional[str] = None, kind: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "page": page,
            "id": id,
            "tenantID": tenantID,
            "name": name,
            "kind": kind,
        }
        clean_params = {k: v for k, v in params.items() if v is not None}
        # Добавляем логирование для отладки
        print(f"[INFO] Sending request with params: {clean_params}\n")
        return self.make_get_request('resources', params=clean_params)

    def get_kind_resources(self, kind, resource_id):
        return self.make_get_request(route = f'resources/{kind}/{resource_id}')

    def put_kind_resources(self, kind, resource_id, content):
        return self.make_put_request(route = f'resources/{kind}/{resource_id}', data = content)

    def resources_validate(self, kind, content):
        return self.make_post_request(route = f'resources/{kind}/validate', data = content)
    
    def resources_create(self, kind, content):
        return self.make_post_request(route = f'resources/{kind}/create', data = content)
