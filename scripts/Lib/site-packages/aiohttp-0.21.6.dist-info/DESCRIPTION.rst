http client/server for asyncio
==============================

.. image:: https://raw.github.com/KeepSafe/aiohttp/master/docs/_static/aiohttp-icon-128x128.png
  :height: 64px
  :width: 64px
  :alt: aiohttp logo

.. image:: https://travis-ci.org/KeepSafe/aiohttp.svg?branch=master
  :target:  https://travis-ci.org/KeepSafe/aiohttp
  :align: right

.. image:: https://coveralls.io/repos/KeepSafe/aiohttp/badge.svg?branch=master&service=github
  :target:  https://coveralls.io/github/KeepSafe/aiohttp?branch=master
  :align: right

.. image:: https://badge.fury.io/py/aiohttp.svg
    :target: https://badge.fury.io/py/aiohttp

Features
--------

- Supports both client and server side of HTTP protocol.
- Supports both client and server Web-Sockets out-of-the-box.
- Web-server has middlewares and pluggable routing.


Getting started
---------------

Client
^^^^^^

To retrieve something from the web:

.. code-block:: python

  import aiohttp
  import asyncio

  async def fetch(session, url):
      with aiohttp.Timeout(10):
          async with session.get(url) as response:
              return await response.text()

  if __name__ == '__main__':
      loop = asyncio.get_event_loop()
      with aiohttp.ClientSession(loop=loop) as session:
          html = loop.run_until_complete(
              fetch(session, 'http://python.org'))
          print(html)


Server
^^^^^^

This is simple usage example:

.. code-block:: python

    from aiohttp import web

    async def handle(request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name
        return web.Response(body=text.encode('utf-8'))

    async def wshandler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.tp == web.MsgType.text:
                ws.send_str("Hello, {}".format(msg.data))
            elif msg.tp == web.MsgType.binary:
                ws.send_bytes(msg.data)
            elif msg.tp == web.MsgType.close:
                break

        return ws


    app = web.Application()
    app.router.add_route('GET', '/echo', wshandler)
    app.router.add_route('GET', '/{name}', handle)

    web.run_app(app)


Note: examples are written for Python 3.5+ and utilize PEP-492 aka
async/await.  If you are using Python 3.4 please replace ``await`` with
``yield from`` and ``async def`` with ``@coroutine`` e.g.::

    async def coro(...):
        ret = await f()

shoud be replaced by::

    @asyncio.coroutine
    def coro(...):
        ret = yield from f()

Documentation
-------------

http://aiohttp.readthedocs.org/

Discussion list
---------------

*aio-libs* google group: https://groups.google.com/forum/#!forum/aio-libs

Requirements
------------

- Python >= 3.4.1
- chardet https://pypi.python.org/pypi/chardet

Optionally you may install cChardet library:
https://pypi.python.org/pypi/cchardet/1.0.0


License
-------

``aiohttp`` is offered under the Apache 2 license.


Source code
------------

The latest developer version is available in a github repository:
https://github.com/KeepSafe/aiohttp

Benchmarks
----------

If you are interested in by efficiency, AsyncIO community maintains a
list of benchmarks on the official wiki:
https://github.com/python/asyncio/wiki/Benchmarks

CHANGES
=======

0.21.6 (05-05-2016)
-------------------

- Drop initial query parameters on redirects #853


0.21.5 (03-22-2016)
-------------------

- Fix command line arg parsing #797

0.21.4 (03-12-2016)
-------------------

- Fix ResourceAdapter: dont add method to allowed if resource is not
  match #826

- Fix Resouce: append found method to returned allowed methods

0.21.2 (02-16-2016)
-------------------

- Fix a regression: support for handling ~/path in static file routes was
  broken #782

0.21.1 (02-10-2016)
-------------------

- Make new resources classes public #767

- Add `router.resources()` view

- Fix cmd-line parameter names in doc

0.21.0 (02-04-2016)
--------------------

- Introduce on_shutdown signal #722

- Implement raw input headers #726

- Implement web.run_app utility function #734

- Introduce on_cleanup signal

- Deprecate Application.finish() / Application.register_on_finish() in favor of
  on_cleanup.

- Get rid of bare aiohttp.request(), aiohttp.get() and family in docs #729

- Deprecate bare aiohttp.request(), aiohttp.get() and family #729

- Refactor keep-alive support #737:

  - Enable keepalive for HTTP 1.0 by default

  - Disable it for HTTP 0.9 (who cares about 0.9, BTW?)

  - For keepalived connections

      - Send `Connection: keep-alive` for HTTP 1.0 only

      - don't send `Connection` header for HTTP 1.1

  - For non-keepalived connections

      - Send `Connection: close` for HTTP 1.1 only

      - don't send `Connection` header for HTTP 1.0

- Add version parameter to ClientSession constructor,
  deprecate it for session.request() and family #736  

- Enable access log by default #735

- Deprecate app.router.register_route() (the method was not documented
  intentionally BTW).

- Deprecate app.router.named_routes() in favor of app.router.named_resources()

- route.add_static accepts pathlib.Path now #743

- Add command line support: `$ python -m aiohttp.web package.main` #740

- FAQ section was added to docs. Enjoy and fill free to contribute new topics

- Add async context manager support to ClientSession

- Document ClientResponse's host, method, url properties

- Use CORK/NODELAY in client API #748

- ClientSession.close and Connector.close are coroutines now

- Close client connection on exception in ClientResponse.release()

- Allow to read multipart parts without content-length specified #750

- Add support for unix domain sockets to gunicorn worker #470

- Add test for default Expect handler #601

- Add the first demo project

- Rename `loader` keyword argument in `web.Request.json` method. #646

- Add local socket binding for TCPConnector #678

