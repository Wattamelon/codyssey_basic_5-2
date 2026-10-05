from sqlalchemy import select
from sqlalchemy.orm import Session

from models.memo import Memo


def list_memos(db: Session):
    return db.scalars(select(Memo).order_by(Memo.id)).all()


def get_memo(db: Session, memo_id: int):
    return db.get(Memo, memo_id)


def create_memo(db: Session, title: str, content: str):
    memo = Memo(title=title, content=content)
    db.add(memo)
    db.commit()
    db.refresh(memo)
    return memo


def update_memo(db: Session, memo: Memo, title: str, content: str):
    memo.title = title
    memo.content = content
    db.commit()
    return memo


def delete_memo(db: Session, memo: Memo):
    db.delete(memo)
    db.commit()
