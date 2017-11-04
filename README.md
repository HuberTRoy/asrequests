# AsRequests: Asyncio + Requests.

AsRequests allow you to use Requests with asyncio to make asynchronous HTTP Requests easily.

# Usage:

Usage is simple:

```
from  asrequests import AsRequests

urls = [
    'http://nodomain/',
    'https://github.com',
    'https://www.python.org/'
]
```

Send them all the same time.

```
>>> with AsRequests() as ar:
            for i in urls:
                ar.get(i)
...
>>>print(ar.result)
[<Response [200]>, ErrorRequest(url='http://nodomain/', text='', ...), <Response [200]>]
```

Use callback.

```
>>> def my_callback(result):
            if not result.get(error_info, False):
                print("This url '{url}' is connectable.".format(result.url))
            else:
                print("This url '{url}' is unconnectable.".format(result.url))
>>> with AsRequests(callback=my_callback) as ar:
            for i in urls:
                ar.get(i)
...
This url 'https://github.com/' is connectable.
This url 'http://nodomain/' is unconnectable.
This url 'https://www.python.org/' is connectable.
>>>
```

Installation.
============
Download.