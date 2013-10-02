# -*- coding: utf-8 -*-


import ujson
import requests
import urllib
import urlparse

from uritemplate import expand


def append_query_params(url, params):
    parts = list(urlparse.urlsplit(url))
    query = urlparse.parse_qs(parts[3])
    query.update(params)
    parts[3] = urllib.urlencode(query, doseq=True)
    return urlparse.urlunsplit(parts)


class Request(object):

    def __init__(self, method, href, auth, resource):
        self.method = method
        self.href = href
        self.auth = auth
        self.resource = resource

    def _get(self, **kwargs):
        # TODO: Refactor to resolve circular dependency.
        from pluct import resource

        data = self.resource.data
        data.update(kwargs)
        url = expand(self.href, data)
        for var in kwargs.keys():
            if "{{{}}}".format(var) in self.href:
                kwargs.pop(var)
        url = append_query_params(url, kwargs)

        response = requests.get(url=url,
                                headers=self.get_headers(),
                                timeout=self.resource.timeout)
        return resource.from_response(response)

    def _post(self, **kwargs):
        # TODO: Refactor to resolve circular dependency.
        from pluct import resource

        self.href = expand(self.href, self.resource.data)
        data = kwargs.pop('data')
        response = requests.post(url=self.href,
                                 data=ujson.dumps(data),
                                 headers=self.get_headers(),
                                 timeout=self.resource.timeout)
        return resource.from_response(response)

    def _patch(self, **kwargs):
        # TODO: Refactor to resolve circular dependency.
        from pluct import resource

        self.href = expand(self.href, self.resource.data)
        data = kwargs.pop('data')
        response = requests.patch(url=self.href,
                                  data=ujson.dumps(data),
                                  headers=self.get_headers(),
                                  timeout=self.resource.timeout)
        return resource.from_response(response)

    def _put(self, **kwargs):
        # TODO: Refactor to resolve circular dependency.
        from pluct import resource

        self.href = expand(self.href, self.resource.data)
        data = kwargs.pop('data')
        response = requests.put(url=self.href,
                                data=ujson.dumps(data),
                                headers=self.get_headers(),
                                timeout=self.resource.timeout)
        return resource.from_response(response)

    def _delete(self, **kwargs):
        # TODO: Refactor to resolve circular dependency.
        from pluct import resource

        self.href = expand(self.href, self.resource.data)
        response = requests.delete(url=self.href,
                                   headers=self.get_headers(),
                                   timeout=self.resource.timeout)
        return resource.from_response(response)

    def get_headers(self):
        header = {
            'content-type': 'application/json'
        }
        if self.auth:
            header['Authorization'] = '{0} {1}'.format(
                self.auth['type'], self.auth['credentials'])

        return header

    @property
    def process(self):
        request_type_by_method = {
            'GET': self._get,
            'POST': self._post,
            'PATCH': self._patch,
            'PUT': self._put,
            'DELETE': self._delete,
        }
        return request_type_by_method[self.method]
