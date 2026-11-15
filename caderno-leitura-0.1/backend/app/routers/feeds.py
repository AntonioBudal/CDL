"""F0.12.04 (spec 117): feeds públicos dos estudos publicados (RSS 2.0, Atom 1.0, JSON Feed 1.1)."""
from __future__ import annotations

from collections.abc import Callable

from fastapi import APIRouter, Request, Response

from app.dependencies import DatabaseSession
from app.services import feed_service as svc

router = APIRouter(include_in_schema=False)


def _respond(request: Request, body: str, media_type: str) -> Response:
    etag = svc.etag_for(body)
    headers = {"ETag": etag, "Cache-Control": "public, no-cache"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(content=body.encode("utf-8"), media_type=media_type, headers=headers)


def _feed(builder: Callable, media_type: str):
    def endpoint(request: Request, session: DatabaseSession) -> Response:
        return _respond(request, builder(svc.feed_items(session)), media_type)

    return endpoint


router.add_api_route("/feed.xml", _feed(svc.build_rss, "application/rss+xml; charset=utf-8"), methods=["GET", "HEAD"])
router.add_api_route("/feed.atom", _feed(svc.build_atom, "application/atom+xml; charset=utf-8"), methods=["GET", "HEAD"])
router.add_api_route("/feed.json", _feed(svc.build_json_feed, "application/feed+json; charset=utf-8"), methods=["GET", "HEAD"])
