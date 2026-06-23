"""Tests for repository file awareness functionality."""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from backend.app.models.repository import Repository
from backend.app.models.file import File
from backend.app.services.repository_service import RepositoryService


class TestRepositoryFileAwareness:
    """Test repository file awareness and metadata-based answering."""

    def test_build_repository_knowledge_index(self):
        """Test building repository knowledge index."""
        files = [
            Mock(path="src/main.jsx", content="import React from 'react';"),
            Mock(path="src/components/Navbar.jsx", content="export default function Navbar() { return null; }"),
            Mock(path="src/api/repositories.py", content="from fastapi import APIRouter;"),
            Mock(path="README.md", content="# Project README"),
            Mock(path="tests/test_example.py", content="def test_example(): pass"),
            Mock(path="Dockerfile", content="FROM python:3.9"),
            Mock(path="package.json", content='{"name": "project"}'),
        ]

        knowledge = RepositoryService._build_repository_knowledge_index(files)

        assert knowledge["repository_type"] == "Full-stack Application"
        assert len(knowledge["frontend_files"]) == 2
        assert len(knowledge["backend_files"]) == 1
        assert len(knowledge["documentation_files"]) == 1
        assert len(knowledge["test_files"]) == 1
        assert len(knowledge["infrastructure_files"]) == 1
        assert len(knowledge["config_files"]) == 1
        assert "React" in knowledge["tech_stack"]
        assert "FastAPI" in knowledge["tech_stack"]

    def test_get_lightweight_file_index(self, db_session):
        """Test getting lightweight file index."""
        # Create a mock repository
        repository = Mock(
            id=1,
            name="test-repo",
            description="Test repository"
        )

        # Create mock files
        files = [
            Mock(
                id=1,
                path="src/main.jsx",
                content="import React from 'react';",
                repository_id=1
            ),
            Mock(
                id=2,
                path="src/components/Navbar.jsx",
                content="export default function Navbar() { return null; }",
                repository_id=1
            ),
            Mock(
                id=3,
                path="backend/app/main.py",
                content="from fastapi import FastAPI;",
                repository_id=1
            ),
            Mock(
                id=4,
                path="README.md",
                content="# Test Project",
                repository_id=1
            ),
        ]

        with patch.object(RepositoryService, 'get_files_by_repository', return_value=files):
            with patch.object(RepositoryService, '_build_repository_knowledge_index') as mock_build:
                mock_build.return_value = {
                    "repository_type": "Full-stack Application",
                    "tech_stack": ["React", "FastAPI"],
                    "entry_points": ["src/main.jsx"],
                    "frontend_files": ["src/main.jsx", "src/components/Navbar.jsx"],
                    "backend_files": ["backend/app/main.py"],
                    "database_files": [],
                    "infrastructure_files": [],
                    "config_files": [],
                    "documentation_files": ["README.md"],
                    "test_files": [],
                    "api_files": [],
                    "auth_files": [],
                    "important_files": ["src/main.jsx", "src/components/Navbar.jsx", "backend/app/main.py", "README.md"],
                    "readme_summary": "# Test Project"
                }

                lightweight_index = RepositoryService.get_lightweight_file_index(db_session, 1)

                assert lightweight_index["repository_name"] == "Full-stack Application"
                assert len(lightweight_index["repository_structure"]["frontend_files"]) == 2
                assert len(lightweight_index["repository_structure"]["backend_files"]) == 1
                assert len(lightweight_index["repository_structure"]["documentation_files"]) == 1

    def test_is_simple_metadata_question(self):
        """Test identifying simple metadata questions."""
        simple_questions = [
            "list react files",
            "react files",
            "frontend files",
            "what frontend files",
            "list backend files",
            "backend files",
            "what backend files",
            "what files exist",
            "what files are available",
            "list all files",
            "what services exist",
            "what services",
            "services",
            "what database files",
            "database files",
            "models",
            "what infrastructure files",
            "infrastructure",
            "docker",
            "what config files",
            "config",
            "configuration",
            "what documentation files",
            "documentation",
            "readme",
            "what test files",
            "test",
            "testing",
        ]

        for question in simple_questions:
            assert RepositoryService._is_simple_metadata_question(question), f"Failed for: {question}"

    def test_is_simple_metadata_question_complex(self):
        """Test that complex questions are not identified as simple."""
        complex_questions = [
            "How does the authentication system work?",
            "Explain the architecture of the project",
            "What are the main components and how do they connect?",
            "How is the database structured?",
            "What happens when the application starts?",
            "How is the frontend state managed?",
            "Where are the API routes defined?",
            "How are tests organized and what do they cover?",
            "How does the main application flow work?",
        ]

        for question in complex_questions:
            assert not RepositoryService._is_simple_metadata_question(question), f"Incorrectly identified as simple: {question}"

    def test_answer_from_metadata_react_files(self):
        """Test answering from metadata for React files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx", "src/components/Navbar.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": ["README.md"],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("list react files", lightweight_index)
        assert answer is not None
        assert "Frontend files available:" in answer
        assert "src/main.jsx" in answer
        assert "src/components/Navbar.jsx" in answer

    def test_answer_from_metadata_backend_files(self):
        """Test answering from metadata for backend files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": ["backend/app/main.py", "backend/app/api/repositories.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": [],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what backend files exist", lightweight_index)
        assert answer is not None
        assert "Backend files available:" in answer
        assert "backend/app/main.py" in answer
        assert "backend/app/api/repositories.py" in answer

    def test_answer_from_metadata_all_files(self):
        """Test answering from metadata for all files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx", "src/components/Navbar.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": ["package.json"],
                "documentation_files": ["README.md"],
                "test_files": ["tests/test_example.py"],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what files are available", lightweight_index)
        assert answer is not None
        assert "Files available:" in answer
        assert "src/main.jsx" in answer
        assert "src/components/Navbar.jsx" in answer
        assert "backend/app/main.py" in answer
        assert "package.json" in answer
        assert "README.md" in answer
        assert "tests/test_example.py" in answer

    def test_answer_from_metadata_services(self):
        """Test answering from metadata for services question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": [
                    "backend/app/main.py",
                    "backend/app/api/repositories.py",
                    "backend/app/services/repository_service.py",
                    "backend/app/models/repository.py"
                ],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": [],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what services exist", lightweight_index)
        assert answer is not None
        assert "Service files available:" in answer
        assert "backend/app/services/repository_service.py" in answer

    def test_answer_from_metadata_database_files(self):
        """Test answering from metadata for database files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": [
                    "backend/app/main.py",
                    "backend/app/models/repository.py",
                    "backend/app/models/commit.py"
                ],
                "database_files": ["backend/app/database/base.py"],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": [],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what database files exist", lightweight_index)
        assert answer is not None
        assert "Database files available:" in answer
        assert "backend/app/database/base.py" in answer

    def test_answer_from_metadata_infrastructure_files(self):
        """Test answering from metadata for infrastructure files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": ["Dockerfile"],
                "config_files": [],
                "documentation_files": [],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what infrastructure files exist", lightweight_index)
        assert answer is not None
        assert "Infrastructure files available:" in answer
        assert "Dockerfile" in answer

    def test_answer_from_metadata_config_files(self):
        """Test answering from metadata for config files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": ["package.json", "requirements.txt"],
                "documentation_files": [],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what config files exist", lightweight_index)
        assert answer is not None
        assert "Configuration files available:" in answer
        assert "package.json" in answer
        assert "requirements.txt" in answer

    def test_answer_from_metadata_documentation_files(self):
        """Test answering from metadata for documentation files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": ["README.md", "docs/api.md"],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what documentation files exist", lightweight_index)
        assert answer is not None
        assert "Documentation files available:" in answer
        assert "README.md" in answer
        assert "docs/api.md" in answer

    def test_answer_from_metadata_test_files(self):
        """Test answering from metadata for test files question."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": [],
                "test_files": ["tests/test_example.py", "tests/test_api.py"],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("what test files exist", lightweight_index)
        assert answer is not None
        assert "Test files available:" in answer
        assert "tests/test_example.py" in answer
        assert "tests/test_api.py" in answer

    def test_answer_from_metadata_no_match(self):
        """Test that questions without matching keywords return None."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": [],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        answer = RepositoryService._answer_from_metadata("How does authentication work?", lightweight_index)
        assert answer is None

    def test_answer_simple_question_metadata_answer(self, db_session):
        """Test that simple questions are answered from metadata."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx", "src/components/Navbar.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": ["README.md"],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        with patch.object(RepositoryService, 'get_lightweight_file_index', return_value=lightweight_index):
            with patch.object(RepositoryService, '_answer_from_metadata') as mock_answer:
                mock_answer.return_value = "Frontend files available: src/main.jsx, src/components/Navbar.jsx"

                result = RepositoryService.answer_simple_question(db_session, 1, "list react files")

                assert result["answer"] == "Frontend files available: src/main.jsx, src/components/Navbar.jsx"
                assert result["files"] == []

    def test_answer_simple_question_ai_answer(self, db_session):
        """Test that complex questions are answered by AI."""
        lightweight_index = {
            "repository_structure": {
                "frontend_files": ["src/main.jsx"],
                "backend_files": ["backend/app/main.py"],
                "database_files": [],
                "infrastructure_files": [],
                "config_files": [],
                "documentation_files": [],
                "test_files": [],
                "api_files": [],
                "auth_files": [],
                "important_files": []
            }
        }

        with patch.object(RepositoryService, 'get_lightweight_file_index', return_value=lightweight_index):
            with patch.object(RepositoryService, '_answer_from_metadata', return_value=None):
                with patch.object(RepositoryService, 'answer_question_with_ai') as mock_ai:
                    mock_ai.return_value = {
                        "answer": "The authentication system uses JWT tokens and FastAPI security.",
                        "files": []
                    }

                    result = RepositoryService.answer_simple_question(db_session, 1, "How does authentication work?")

                    assert result["answer"] == "The authentication system uses JWT tokens and FastAPI security."
                    assert result["files"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
