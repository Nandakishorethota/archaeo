from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    Index
)

from app.database.base import Base


class File(Base):

    __tablename__ = "files"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False,
        index=True
    )

    path = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=True
    )


Index("ix_files_repo_path", File.repository_id, File.path)