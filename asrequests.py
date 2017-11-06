# -*- coding: utf-8 -*-

"""
This module contains an asynchronous method to send get and post http requests.

Use 'AsRequests' to send them.

Simple and effective.
:)

"""
import asyncio

import requests

from collections import namedtuple


__all__ = (
    'AsRequests'
)

ErrorRequest = namedtuple('ErrorRequest', 
                                                        ['url',
                                                        'text',
                                                        'content',
                                                        'code',
                                                        'error_info'])


class RequestsBase(object):
    session = requests.session()

    def __del__(self):
        self.session.close()

    def get(self, url, **kwargs):

        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):

        return self.session.post(url, **kwargs)

    def __del__(self):
        self.session.close()


class AsRequests(RequestsBase):
    """
    An async http requests.

    Accept parameters:

    :param callback: response callback. 
    :param callback default: lambda response: self.result.append(response)

    :param exceptionHandler: exception handling function. 
    :param exceptionHandler default: lambda exception: print(exception)
    
    :param callbackMode: The type of callback function.
    :param callbackMode accept:
        1(or != 2,3) : callback function is a normal function.
        2 : callback function has blocking codes.
        3 : callback function is an asynchronous function.

    Method and Coroutine Method:
        get
        post

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
        [ErrorRequest(url='..', text='', ..), ErrorRequest(url='..', text='', ..), ...]
        # print result.
        <Response [200]>
        <Response [200]>
        <Response [200]>
        <Response [200]>
        <Response [200]>

    Coroutine Usage::
        import asyncio
        urls = ['https://github.com']*5
        
        arequests = AsRequests()
        
        # one.
        @asyncio.coroutine
        def getUrl(url, **kwargs):
            print('url: {0}'.format(url))
            result = yield from arequests.get(url, **kwargs)
            print('url: {0}, response: {1}'.format(url, result))

        eventLoop = asyncio.get_event_loop()
        # run.
        eventLoop.run_until_complete(asyncio.wait([getUrl(url) for url in urls]))
        
        # two.
        @asyncio.coroutine
        def getUrl(url, **kwargs):
            print('url: {0}'.format(url))
            result = yield from arequests.get(url, **kwargs)
            print('url: {0}, response: {1}'.format(url, result))
        
        for url in urls:
            # asyncio.ensure_future or eventLoop.create_task or asyncio.Task.
            asyncio.Task(getUrl(url))

        eventLoop = asyncio.get_event_loop()
        # run.
        eventLoop.run_forever()
        >>>
        url: https://github.com
        url: https://github.com
        ....
        url: https://github.com, response: <Response [200]>
        url: https://github.com, response: <Response [200]>
        ....
    """
    def __init__(self, callback=None, exceptionHandler=None, callbackMode=1):
        super().__init__()
        
        self.callbackMode = callbackMode

        # default callback result.
        self.tasks = []
        self.result = []

        self.callback = callback if callback else lambda response: self.result.append(response)

        # if callback function has blocking codes.
        self.blockingCallbackTasks = []

        self.blockingCallback = lambda response: self.result.append(response)

        # if callback function has asynchronous codes.
        self.asyncCallbackTasks = []
        
        self.asyncCallback = lambda response: self.asyncCallbackTasks.append(self.callback(response))
        
        # default exception handling function.
        self.exceptionHandler = exceptionHandler if exceptionHandler else lambda exception: print(exception)

    def __enter__(self):

        # Initialize the tasks and result.
        self.tasks = []
        self.result = []

        # if callback function has blocking codes.
        self.blockingCallbackTasks = []

        # if callback function has asynchronous codes.
        self.asyncCallbackTasks = []

        return self

    def __exit__(self, except_type, value, tb):
        """
            Without manual setting.
        """
        self._executeTasks()

        return True

    def __repr__(self):
        """
            Return the session string and the tasks string.
        """

        return '<AsRequests: tasks: {tasks}>'.format(tasks=self.tasks)

    def _httpRequest(self, method, url, kwargs):
        method = method.upper()
        if method == 'GET':
            data = super().get(url, **kwargs)
        elif method == 'POST':
            data = super().post(url, **kwargs)

        return data

    @asyncio.coroutine
    def _aHttpRequest(self, method, url, kwargs):
        eventLoop = asyncio.get_event_loop()
        # it is still a thread. check out 'asyncio.base_event' getting more details.
        # check out this:
        # https://stackoverflow.com/questions/22190403/how-could-i-use-requests-in-asyncio
        # getting more explain.
        future = eventLoop.run_in_executor(None, self._httpRequest, method, url, kwargs)

        try:
            data = yield from future
        except Exception as e:
            data = ErrorRequest(url=url,
                                                      text='',
                                                      content=b'',
                                                      code='404',
                                                      error_info=e)
            self.exceptionHandler(e)
        finally:
            if self.callbackMode == 3:
                eventLoop.call_soon_threadsafe(self.asyncCallback, data)
            elif self.callbackMode == 2:
                eventLoop.call_soon_threadsafe(self.blockingCallback, data)
            else:
                eventLoop.call_soon_threadsafe(self.callback, data)
        return data       

    @asyncio.coroutine
    def _get(self, url, **kwargs):
        return self._aHttpRequest('GET', url, kwargs)

    @asyncio.coroutine
    def _post(self, url, **kwargs):
        return self._aHttpRequest('POST', url, kwargs)

    def _executeTasks(self):
        eventLoop = asyncio.get_event_loop()
        eventLoop.run_until_complete(asyncio.wait(self.tasks))

        newLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(newLoop)
        if self.callbackMode == 3:
            newLoop.run_until_complete(asyncio.wait([asyncio.Task(_) for _ in self.asyncCallbackTasks]))
        elif self.callbackMode == 2:
            for i in self.result:
                future = newLoop.run_in_executor(None, self.callback, i)
                self.blockingCallbackTasks.append(asyncio.ensure_future(future))

            newLoop.run_until_complete(asyncio.wait(self.blockingCallbackTasks))

    def setCallback(self, func):
        self.callback = func

    def setExceptionHandler(self, func):
        self.exceptionHandler = func

    def get(self, url, **kwargs):
        """
        check out 'http://docs.python-requests.org/en/master/' getting help.
        """
        future = asyncio.ensure_future(self._get(url, **kwargs))
        self.tasks.append(future)

        return future

    def post(self, url, **kwargs):
        """
        check out 'http://docs.python-requests.org/en/master/' getting help.
        """
        future = asyncio.ensure_future(self._post(url, **kwargs))
        self.tasks.append(future)

        return future


asrequests = AsRequests()


if __name__ == '__main__':
    help(asrequests)