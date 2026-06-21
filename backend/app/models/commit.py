from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from app.database.base import Base


class Commit(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
        index=True
    )

    hash = Column(String, nullable=False)

    author = Column(String)

    message = Column(String)

    commit_date = Column(DateTime, index=True)


Index("ix_commits_repo_date", Commit.repository_id, Commit.commit_date)