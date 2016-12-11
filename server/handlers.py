import aiohttp_jinja2

from aiohttp import web

from server.network.glob import GlobalNetwork

network = GlobalNetwork()


async def index(request):
    return aiohttp_jinja2.render_template('index.html', request, {})


async def get_connections(request):
    return web.json_response(network.serialize_connections())


async def get_nodes(request):
    return web.json_response(network.serialize_nodes())


async def get_connection_details(request):
    conn_id = request.rel_url.query['connection_id']
    connection = network.connections[conn_id]
    return web.json_response(connection.to_dict())


async def get_routing_table(request):
    node_id = request.rel_url.query['node_id']
    table = network.nodes[int(node_id)].routing_table
    return web.json_response(table)


async def post_update_connection(request):
    data = await request.post()
    network.update_connection(data)
    return web.json_response({})


async def post_add_connection(request):
    data = await request.post()
    connection = network.add_connection(int(data['from']), int(data['to']),
                                        recalc_table=True)
    return web.json_response(connection.to_dict())

async def delete_elements(request):
    data = await request.post()
    try:
        for connection_id in data.getall('edges[]'):
            network.delete_connection(connection_id)
        for node_id in data.getall('nodes[]'):
            network.delete_node(int(node_id))
    except:
        pass
    return web.json_response({})
