import jinja2
import asyncio
import aiohttp_jinja2

from aiohttp import web

from server.handlers import *


async def init(loop):
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)

    app.router.add_get('/', index)
    app.router.add_get('/nodes', get_nodes)
    app.router.add_get('/connections', get_connections)
    app.router.add_get('/connection-details', get_connection_details)
    app.router.add_get('/routing-table', get_routing_table)
    app.router.add_post('/add-connection', post_add_connection)
    app.router.add_post('/update-connection', post_update_connection)
    app.router.add_delete('/delete-elements', delete_elements)
    app.router.add_static('/static', './client/static')

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('./client/templates'))
    serve = await loop.create_server(app.make_handler(), '127.0.0.1', 8080)
    return serve


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
