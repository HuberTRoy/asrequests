"""
This module contains an asynchronous method to send get and post http requests.

Use 'AsRequests' to send them.

Simple and effective.
:)

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

Using like requests:
```
from asrequests import asrequests

async def get_http():
        for i in urls:
            response = await asrequests.get(i)
            print(response)

....
asyncio.run_until_complete(get_http)

===
<Response [200]>
ErrorRequest(url='http://nodomain/', text='', ...)
<Response [200]>
```

"""
from setuptools import setup

setup(
    name='asrequests',
    version='0.1.1',
    url='https://github.com/HuberTRoy/asrequests',
    license='MIT',
    author='cyrbuzz',
    author_email='cyrbuzz@foxmail.com',
    description='Requests + asyncio',
    long_description=__doc__,
    install_requires=[
        'requests'
    ],
    py_modules=['asrequests'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)