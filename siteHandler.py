import json
import random
import resource
import string
import time

import asyncio
import requests
from aiohttp import web
import aiohttp_cors
import uuid

import aiogramHandler

resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

path_to_pics = "/home/anton/Desktop/OSM_tg_bot/pictures"
path_to_get_osm = "/home/anton/Desktop/OSM_roads_parser/get_osm.py"
path_to_osm_parser_python = "/home/anton/Desktop/OSM_roads_parser/main.py"
path_to_osm_parser_cpp = "/home/anton/Desktop/OSM_roads_parser_cpp_act/release/OSM_roads_parser_cpp"

ioloop = asyncio.get_event_loop()

def create_title():
    title = uuid.uuid4().hex[:20].upper()
    return title

async def receive_data(request):
    # response = {'result': 'success'}
    try:
        handler = asyncio.create_task(handle_data(request))
        response = await handler
    except json.JSONDecodeError:
        response = {'result': 'failed_get_json'}
        # response['result'] = 'failed_get_json'

    # return web.json_response({'status': 'success'})
    return response

async def run_command(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout, stderr

async def handle_data(request):
    a = time.time()
    content = await request.json()
    tl = content["tl"]
    dr = content["dr"]
    hash_id = content["hash_id"]
    if await aiogramHandler.get_user_state(hash_id) != "wait_select_rectangle":
        return web.json_response({'status': 'outdated_page'})

    minlat = min(tl["lat"], dr["lat"])
    minlon = min(tl["lon"], dr["lon"])
    maxlat = max(tl["lat"], dr["lat"])
    maxlon = max(tl["lon"], dr["lon"])

    title = create_title()
    path_to_osm = f"{path_to_pics}/osm/{title}.osm"
    path_to_pic = f"{path_to_pics}/pics/{title}.jpg"
    b = time.time()

    get_osm_cmd = f'python3 {path_to_get_osm} {minlat} {minlon} {maxlat} {maxlon} {path_to_osm}'
    osm_parser_cmd = f'{path_to_osm_parser_cpp} {path_to_osm} {path_to_pic}'
    await run_command(get_osm_cmd)
    c = time.time()
    await run_command(osm_parser_cmd)

    d = time.time()
    print(b - a)
    print(c - b)
    print(d - c)

    await aiogramHandler.send_pic(hash_id, path_to_osm, path_to_pic)
    return web.json_response({'result': 'success'})

async def start():
    app = web.Application()
    app.router.add_post('/send', receive_data)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
