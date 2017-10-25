# -*- coding: utf-8 -*-

"""
This module contains an asynchronous method to send get and post http requests.

Use 'AsRequests' to send them.

Simple and effective.
:)

"""
import asyncio

import requests

import aiohttp

# from concurrent.futures import ThreadPoolExecutor
# import threading

__all__ = (
    'AsRequests'
)


class RequestsBase(object):
    session = requests.session()

    def __del__(self):
        self.session.close()

    def get(self, url, **kwargs):

        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):

        return self.session.post(url, **kwargs)


class AsRequests(RequestsBase):
    """
    An async http requests.

    Accept parameters:

    :param callback: response callback. 
    :param callback default: lambda response: self.result.append(response.result()) 

    :param exceptionHandler: exception handling function. 
    :param exceptionHandler default: lambda exception: print(exception)
    
    Method:
    get.
    post.

    Usage::
    # normal.
    with AsRequests() as ar:
        for i in ['https://github.com']*5:
            ar.get(i)

    print(ar.result)
    
    # print error.
    with ar:
        for i in ['https://github.com']*5:
            ar.get(i, timeout=0.001)   

    print(ar.result)

    # with params.
    def showResponse(result):
        print(result)
        ....

    with AsRequests(callback=showResponse) as ar:
        for i in ['https://github.com']*5:
            ar.get(i)

    >>>
    # normal.
    [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>]
    # error
    error information...
    [False, False, False, False, False]
    # print result.
    <Response [200]>
    <Response [200]>
    <Response [200]>
    <Response [200]>
    <Response [200]>
    """
    def __init__(self, callback=None, exceptionHandler=None):
        super().__init__()
        
        # default callback result.
        self.result = []
        
        self.tasks = []
        
        self.callback = callback if callback else lambda response: self.result.append(response)

        self.exceptionHandler = exceptionHandler if exceptionHandler else lambda exception: print(exception)

    def __enter__(self):

        # Initialize the tasks and result.
        self.tasks = []
        self.result = []
        
        return self

    def __exit__(self, except_type, value, tb):
        """
            without manual setting.
        """
        eventLoop = asyncio.get_event_loop()
        eventLoop.run_until_complete(asyncio.wait(self.tasks))

        return True

    def __del__(self):
        pass

    def _httpRequest(self, method, url, kwargs):
        method = method.upper()
        if method == 'GET':
            data = super().get(url, **kwargs)
        elif method == 'POST':
            data = super().post(url, **kwargs)

        return data

    @asyncio.coroutine
    def _get(self, url, **kwargs):
        eventLoop = asyncio.get_event_loop()
        future = eventLoop.run_in_executor(None, self._httpRequest, 'GET', url, kwargs)

        try:
            data = yield from future
            eventLoop.call_soon_threadsafe(self.callback, data)

        except Exception as e:
            self.exceptionHandler(e)
            eventLoop.call_soon_threadsafe(self.callback, False)
            return False

        return data

    @asyncio.coroutine
    def _post(self, url, **kwargs):
        eventLoop = asyncio.get_event_loop()
        future = eventLoop.run_in_executor(None, self._httpRequest, 'POST', url, kwargs)

        try:
            data = yield from future
            eventLoop.call_soon_threadsafe(self.callback, data)
        except Exception as e:
            self.exceptionHandler(e)
            eventLoop.call_soon_threadsafe(self.callback, False)
            return False

        return data

    def setCallback(self, func):
        self.callback = func

    def setExceptionHandler(self, func):
        self.exceptionHandler = func

    def get(self, url, **kwargs):
        """
        check out 'http://docs.python-requests.org/en/master/' getting help.
        """
        self.tasks.append(asyncio.ensure_future(self._get(url, **kwargs)))

    def post(self, url, **kwargs):
        """
        check out 'http://docs.python-requests.org/en/master/' getting help.
        """
        self.tasks.append(asyncio.ensure_future(self._post(url, **kwargs)))


if __name__ == '__main__':

    help(AsRequests)

