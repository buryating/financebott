from aiohttp import web

from config import get_user_by_token
from processing import process_entry

routes = web.RouteTableDef()


@routes.post("/add")
async def handle_add(request: web.Request) -> web.Response:
    token = request.query.get("token")
    user = get_user_by_token(token)
    if user is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    try:
        data = await request.json()
    except ValueError:
        return web.json_response({"error": "invalid json"}, status=400)

    text = (data.get("text") or "").strip()
    if not text:
        return web.json_response({"error": "empty text"}, status=400)

    reply = process_entry(text, user)
    return web.json_response({"message": reply})


def create_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    return app
