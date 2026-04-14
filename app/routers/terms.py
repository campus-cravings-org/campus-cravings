from fastapi.responses import HTMLResponse
from fastapi import Request
from . import router, templates


@router.get("/terms", response_class=HTMLResponse)
async def terms_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="terms.html",
    )
