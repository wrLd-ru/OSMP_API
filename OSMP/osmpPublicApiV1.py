import requests
import json
from typing import Any, Optional, Dict
from time import strftime

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Osmp:

    def __init__(self, xdrdomain, token):
        self.session = requests.Session()
        self.session.verify = False
        self.xdrdomain = xdrdomain
        self.token = token
        self.headers = {'Authorization': 'Bearer ' + token}
        self.session.headers.update(self.headers)

    def _make_request(self, method, route, params=None, data=None, files=None, resp_status_code_expected=200, response_type='json'):
        url = 'https://api.{}/xdr/api/v1/{}'.format(self.xdrdomain, route)

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

    def get_tenants(self, *args, **kwargs):
        return self.make_get_request('tenants', *args, **kwargs)
    
    def get_alerts(self, *, id: Optional[str] = None, tenantID: Optional[str] = None, timestamp: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        
        #timestamp = 'lastSeen'
        page = 1 
        params = {
        "page": page,
        "id": id,
        "tenantID": tenantID,
        "timestampField" : timestamp,
        "from": start,
        "to": end,
        "status": status
        }
        clean_params = {k: v for k, v in params.items() if v is not None}
        # Добавляем логирование для отладки
        print(f"[INFO] Sending request with params: {clean_params}\n")
        return self.make_get_request('alerts', params=clean_params)
