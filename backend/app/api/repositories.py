from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.repository import RepositoryCreate
from app.schemas.question import QuestionRequest
from app.services.ai_summary_service import ai_summary_service

from app.models.repository import Repository
from app.models.commit import Commit
from app.models.file import File
from app.services.architecture_service import ArchitectureService

from app.database.dependencies import get_db

from app.services.git_service import GitService
from app.services.repository_service import RepositoryService

import os

router = APIRouter()


@router.post("/repositories")
def create_repository(
    repo: RepositoryCreate,
    db: Session = Depends(get_db)
):
    try:
        git_data = GitService.clone_repository(repo.url)

        new_repo = Repository(
            name=git_data["name"],
            url=repo.url
        )
        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)

        commits = GitService.extract_commits(git_data["repo"])
        files = GitService.extract_files(git_data["path"])

        file_count = 0
        for file_path in files:
            if not RepositoryService.is_valid_file(file_path):
                continue

            full_path = os.path.join(git_data["path"], file_path)
            content = GitService.read_file_content(full_path)

            file = File(
                repository_id=new_repo.id,
                path=file_path,
                content=content
            )
            db.add(file)
            file_count += 1

        db.commit()

        for commit_data in commits:
            commit = Commit(
                repository_id=new_repo.id,
                hash=commit_data["hash"],
                author=commit_data["author"],
                message=commit_data["message"],
                commit_date=commit_data["commit_date"]
            )
            db.add(commit)

        db.commit()

        return {
            "id": new_repo.id,
            "name": new_repo.name,
            "url": new_repo.url,
            "commit_count": len(commits),
            "file_count": file_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to import repository: {str(e)}"
        )
    finally:
        if 'git_data' in locals():
            GitService.cleanup_temp_dir(git_data["path"])


@router.get("/repositories")
def get_repositories(db: Session = Depends(get_db)):
    repositories = db.query(Repository).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "url": r.url,
        }
        for r in repositories
    ]


@router.get("/repositories/{repository_id}")
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    commit_count = RepositoryService.get_commit_count(db, repository_id)

    return {
        "id": repository.id,
        "name": repository.name,
        "url": repository.url,
        "commit_count": commit_count,
    }


@router.get("/repositories/{repository_id}/stats")
def get_repository_stats(
    repository_id: int,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    return RepositoryService.get_repository_stats(db, repository_id)


@router.get("/repositories/{repository_id}/files")
def get_repository_files(
    repository_id: int,
    db: Session = Depends(get_db)
):
    files = RepositoryService.get_files_by_repository(db, repository_id)
    return [
        {"path": f.path, "content": f.content[:1000] if f.content else ""}
        for f in files
    ]


@router.get("/repositories/{repository_id}/file-tree")
def get_file_tree(
    repository_id: int,
    db: Session = Depends(get_db)
):
    return RepositoryService.get_file_paths_by_repository(db, repository_id)


@router.get("/repositories/{repository_id}/search-content")
def search_content(
    repository_id: int,
    keyword: str,
    db: Session = Depends(get_db)
):
    return RepositoryService.search_files_by_content(db, repository_id, keyword)


@router.get("/repositories/{repository_id}/architecture")
def get_architecture(
    repository_id: int,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    return RepositoryService.get_architecture(db, repository_id)


@router.get("/repositories/{repository_id}/summary")
def get_repository_summary(
    repository_id: int,
    db: Session = Depends(get_db)
):
    summary = RepositoryService.get_summary(db, repository_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Repository not found")

    return summary


@router.post("/repositories/{repository_id}/ask")
def ask_repository(
    repository_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    files = RepositoryService.get_files_by_repository(db, repository_id)
    keywords = request.question.lower().replace("?", "").split()

    matches = []
    for file in files:
        if not file.content:
            continue

        score = 0
        for keyword in keywords:
            score += file.content.lower().count(keyword)

        if score > 0:
            matches.append({
                "path": file.path,
                "score": score,
                "snippet": file.content[:200]
            })

    matches.sort(key=lambda x: x["score"], reverse=True)

    return {
        "question": request.question,
        "total_matches": len(matches),
        "matches": matches[:10]
    }


@router.post("/repositories/{repository_id}/answer")
def answer_repository(
    repository_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    result = RepositoryService.answer_question(
        db, repository_id, request.question
    )

    return {
        "question": request.question,
        "answer": result["answer"],
        "files": result["files"]
    }


@router.get("/repositories/{repository_id}/architecture-tree")
def get_architecture_tree(
    repository_id: int,
    db: Session = Depends(get_db)
):
    repository = (
        db.query(Repository)
        .filter(Repository.id == repository_id)
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    files = RepositoryService.get_files_by_repository(
        db,
        repository_id
    )

    return ArchitectureService.analyze(files)