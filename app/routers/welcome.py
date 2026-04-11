from fastapi.responses import HTMLResponse
from fastapi import Request
from . import router, templates


@router.get("/welcome", response_class=HTMLResponse)
async def welcome_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="welcome.html",
    )
