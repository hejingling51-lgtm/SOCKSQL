# database.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class VisitCounter(db.Model):
    __tablename__ = "visit_counter"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0, nullable=False)

    @classmethod
    def get_count(cls):
        row = cls.query.first()
        if row is None:
            row = cls(count=0)
            db.session.add(row)
            db.session.commit()
        return row.count

    @classmethod
    def increment(cls):
        row = cls.query.first()
        if row is None:
            row = cls(count=0)
            db.session.add(row)
        row.count += 1
        db.session.commit()
        return row.count


def add_message(name, email, message):
    msg = Message(name=name, email=email, message=message)
    db.session.add(msg)
    db.session.commit()
    return msg


def list_messages(limit=200):
    return (Message.query
            .order_by(Message.id.desc())
            .limit(limit)
            .all())