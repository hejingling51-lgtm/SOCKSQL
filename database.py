# database.py
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update

db = SQLAlchemy()


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class VisitCounter(db.Model):
    __tablename__ = "visit_counter"

    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False, default=0)

    @staticmethod
    def get_count():
        """取得目前瀏覽次數；若不存在則建立一筆初始資料。"""
        row = db.session.get(VisitCounter, 1)
        if row is None:
            row = VisitCounter(id=1, count=0)
            db.session.add(row)
            db.session.commit()
        return row.count

    @staticmethod
    def increment():
        """原子性 +1，回傳最新值。PostgreSQL 安全。"""
        # 確保資料列存在
        row = db.session.get(VisitCounter, 1)
        if row is None:
            row = VisitCounter(id=1, count=0)
            db.session.add(row)
            db.session.commit()

        # 原子更新：UPDATE visit_counter SET count = count + 1 WHERE id = 1
        db.session.execute(
            update(VisitCounter)
            .where(VisitCounter.id == 1)
            .values(count=VisitCounter.count + 1)
        )
        db.session.commit()

        # 重新讀取最新值
        db.session.expire_all()
        return db.session.get(VisitCounter, 1).count


def add_message(name, email, message):
    msg = Message(name=name, email=email, message=message)
    db.session.add(msg)
    db.session.commit()
    return msg


def list_messages(limit=200):
    return (
        Message.query.order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
