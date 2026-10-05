from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import PROJECT_DIR, get_db
from services import memo_service as service

router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_DIR / "templates"))


def render(request, name, context=None, status_code=200):
    return templates.TemplateResponse(
        request=request, name=name, context=context or {}, status_code=status_code
    )


def redirect_to_list():
    return RedirectResponse(url="/memos", status_code=303)


@router.get("/")
def home(request: Request):
    return render(request, "home.html", {
        "app_name": "나의 메모 앱",
        "description": "메모를 기록하고 목록과 상세 내용을 확인하며 수정·삭제하는 앱입니다.",
    })


@router.get("/memos")
def list_memos(request: Request, db: Session = Depends(get_db)):
    return render(request, "memo_list.html", {"memos": service.list_memos(db)})


@router.get("/memos/new")
def new_memo(request: Request):
    return render(request, "memo_create.html")


@router.post("/memos")
def create_memo(request: Request, title: str = Form(""), content: str = Form(""),
                db: Session = Depends(get_db)):
    try:
        service.create_memo(db, title, content)
    except ValueError as error:
        return render(request, "memo_create.html", {
            "error": str(error), "title": title, "content": content,
        }, 422)
    return redirect_to_list()


@router.get("/memos/{memo_id}")
def read_memo(request: Request, memo_id: int, db: Session = Depends(get_db)):
    memo = service.get_memo(db, memo_id)
    if memo is None:
        return render(request, "memo_not_found.html", status_code=404)
    return render(request, "memo_detail.html", {"memo": memo})


@router.get("/memos/{memo_id}/edit")
def edit_memo(request: Request, memo_id: int, db: Session = Depends(get_db)):
    memo = service.get_memo(db, memo_id)
    if memo is None:
        return render(request, "memo_not_found.html", status_code=404)
    return render(request, "memo_edit.html", {"memo": memo})


@router.post("/memos/{memo_id}/edit")
def update_memo(request: Request, memo_id: int, title: str = Form(""),
                content: str = Form(""), db: Session = Depends(get_db)):
    try:
        service.update_memo(db, memo_id, title, content)
    except ValueError as error:
        return render(request, "memo_edit.html", {
            "memo": {"id": memo_id, "title": title, "content": content},
            "error": str(error),
        }, 422)
    return redirect_to_list()


@router.post("/memos/{memo_id}/delete")
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    service.delete_memo(db, memo_id)
    return redirect_to_list()
