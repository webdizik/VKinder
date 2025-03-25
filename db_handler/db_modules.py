import sqlalchemy as sq
from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

DSN = 'postgresql://postgres:123@localhost:5432/vkinder'
engine = create_engine(DSN)


class User(Base):
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=True, nullable=False)

    favorites = relationship("Favorite", back_populates="user")
    user_state = relationship("UserState", back_populates="user")


class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"))
    first_name = sq.Column(sq.String(length=255), nullable=False)
    last_name = sq.Column(sq.String(length=255), nullable=False)
    vk_link = sq.Column(sq.String(length=255), unique=True, nullable=False)

    user = relationship("User", back_populates="favorites")


class UserState(Base):
    __tablename__ = "user_states"

    state_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"))
    current_index = sq.Column(sq.Integer, nullable=False)
    offset = sq.Column(sq.Integer, nullable=False)
    candidates = sq.Column(JSON)
    favorites = sq.Column(JSON)

    user = relationship("User", back_populates="user_state")


def create_tables(engine):
    Base.metadata.create_all(engine)


create_tables(engine)
