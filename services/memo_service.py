from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from repositories import memo_repository as repository


@dataclass(frozen=True)
class MemoData:
    id: int
    title: str
    content: str
    created_at: datetime


def to_data(memo):
    return MemoData(memo.id, memo.title, memo.content, memo.created_at)


def validate(title: str, content: str):
    title, content = title.strip(), content.strip()
    if not title or not content:
        raise ValueError("제목과 내용을 모두 입력해주세요.")
    if len(title) > 100:
        raise ValueError("제목은 100자 이하로 입력해주세요.")
    return title, content


def list_memos(db: Session):
    return [to_data(memo) for memo in repository.list_memos(db)]


def get_memo(db: Session, memo_id: int):
    memo = repository.get_memo(db, memo_id)
    return to_data(memo) if memo else None


def create_memo(db: Session, title: str, content: str):
    title, content = validate(title, content)
    return to_data(repository.create_memo(db, title, content))


def update_memo(db: Session, memo_id: int, title: str, content: str):
    memo = repository.get_memo(db, memo_id)
    if memo is None:
        return None
    title, content = validate(title, content)
    return to_data(repository.update_memo(db, memo, title, content))


def delete_memo(db: Session, memo_id: int):
    memo = repository.get_memo(db, memo_id)
    if memo is not None:
        repository.delete_memo(db, memo)
