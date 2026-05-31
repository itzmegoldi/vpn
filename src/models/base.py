from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, BigInteger
from datetime import datetime

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    @property
    def created_at_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_at)

    @property
    def updated_at_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.updated_at)
