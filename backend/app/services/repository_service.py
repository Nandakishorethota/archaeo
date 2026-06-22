from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import os
import re
from collections import Counter

from app.services.ai_summary_service import ai_summary_service

from app.models.repository import Repository
from app.models.commit import Commit
from app.models.file import File


class RepositoryService:

    ALLOWED_EXTENSIONS = (
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".java", ".go", ".md", ".txt", ".toml",
        ".yml", ".yaml"
    )
    ENTRY_POINTS = (
        "main.py",
        "app.py",
        "server.py",
        "run.py",
        "manage.py",
       "index.js",
        "index.ts",
        "main.jsx",
        "main.tsx",
         "app.jsx",
        "app.tsx"
        ) 

    EXTENSION_TO_TECH = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript React",
        ".jsx": "React",
        ".java": "Java",
        ".go": "Go",
        ".rb": "Ruby",
        ".rs": "Rust",
        ".php": "PHP",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
    }
     
    IMPORTANT_DIRECTORIES = (
        "api",
        "routes",
        "controllers",
        "services",
        "models",
        "components",
        "pages",
        "hooks",
        "database",
     )
    CONFIG_TO_TECH = {
        "pyproject.toml": "Python",
        "requirements.txt": "Python",
        "setup.py": "Python",
        "package.json": "Node.js",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "pom.xml": "Java",
        "Gemfile": "Ruby",
        "dockerfile": "Docker",
        "docker-compose": "Docker",
    }

    @staticmethod
    def get_files_by_repository(
        db: Session, repository_id: int
    ) -> List[File]:
        return (
            db.query(File)
            .filter(File.repository_id == repository_id)
            .all()
        )

    @staticmethod
    def get_file_paths_by_repository(
        db: Session, repository_id: int
    ) -> List[Dict[str, str]]:
        files = (
            db.query(File.path)
            .filter(File.repository_id == repository_id)
            .all()
        )
        return [{"path": f.path} for f in files]

    @staticmethod
    def get_file_count(
        db: Session, repository_id: int
    ) -> int:
        return (
            db.query(File)
            .filter(File.repository_id == repository_id)
            .count()
        )

    @staticmethod
    def get_commit_count(
        db: Session, repository_id: int
    ) -> int:
        return (
            db.query(Commit)
            .filter(Commit.repository_id == repository_id)
            .count()
        )

    @staticmethod
    def get_contributor_count(
        db: Session, repository_id: int
    ) -> int:
        return (
            db.query(Commit.author)
            .filter(Commit.repository_id == repository_id)
            .distinct()
            .count()
        )

    @staticmethod
    def get_repository_stats(
        db: Session, repository_id: int
    ) -> Dict:
        return {
            "total_commits": RepositoryService.get_commit_count(db, repository_id),
            "contributors": RepositoryService.get_contributor_count(db, repository_id),
            "total_files": RepositoryService.get_file_count(db, repository_id),
        }

    @staticmethod
    def get_architecture(
        db: Session, repository_id: int
    ) -> Dict[str, List[str]]:
        files = RepositoryService.get_files_by_repository(db, repository_id)

        entry_points = []
        config_files = []
        documentation = []
        tests = []

        for file in files:
            path = file.path.lower()

            if path.endswith(RepositoryService.ENTRY_POINTS):
                  entry_points.append(file.path)

            if any(x in path for x in [
                "pyproject.toml", "requirements.txt",
                "dockerfile", "package.json"
            ]) or path.endswith((".yml", ".yaml", ".toml")):
                config_files.append(file.path)

            if "readme" in path:
                documentation.append(file.path)

            if "test" in path:
                tests.append(file.path)

        return {
            "entry_points": entry_points,
            "config_files": config_files,
            "documentation": documentation,
            "tests": tests,
        }

    @staticmethod
    def search_files_by_content(
        db: Session, repository_id: int, keyword: str
    ) -> List[Dict]:
        files = (
            db.query(File)
            .filter(File.repository_id == repository_id)
            .filter(File.content.ilike(f"%{keyword}%"))
            .all()
        )

        return [
            {"path": f.path, "content": f.content[:500] if f.content else ""}
            for f in files
        ]

    @staticmethod
    def answer_question(
        db: Session, repository_id: int, question: str
    ) -> Dict:
        keywords = re.sub(r'[?!.]', '', question.lower()).split()

        files = RepositoryService.get_files_by_repository(db, repository_id)

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
                    "score": score
                })

        matches.sort(key=lambda x: x["score"], reverse=True)
        top_matches = matches[:3]

        if not top_matches:
            return {
                "answer": "No relevant files found for this question.",
                "files": []
            }

        answer = f"The most relevant files for '{question}' are: "
        answer += ", ".join(m["path"] for m in top_matches)

        return {
            "answer": answer,
            "files": top_matches
        }

    @staticmethod
    def answer_question_with_ai(
        db: Session, repository_id: int, question: str
    ) -> Dict:
        from app.services.ai_summary_service import ai_summary_service
        
        files = RepositoryService.get_files_by_repository(db, repository_id)
        
        important_files = []
        for file in files[:3]:
            if file.content:
                important_files.append(f"{file.path}: {file.content[:80]}...")
        
        prompt = f"""Answer this question about the repository in 2-3 lines:

Question: {question}

Repository files:
{chr(10).join(important_files)}

Provide a concise 2-3 line answer based on the repository content. Answer about both frontend and backend components equally. If the question cannot be answered from the available content, please say so."""
        
        try:
            response = ai_summary_service.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect. Answer questions about code repositories based on their content. Keep answers concise (2-3 lines). Answer equally about both frontend and backend components."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=300,
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "files": important_files
            }
        except Exception as e:
            return {
                "answer": f"Error generating AI answer: {str(e)}",
                "files": []
            }

    @staticmethod
    def is_valid_file(path: str) -> bool:
        return (
            path.endswith(RepositoryService.ALLOWED_EXTENSIONS)
            or path.lower() == "dockerfile"
        )

    @staticmethod
    def detect_tech_stack(files: List[File]) -> List[str]:
        tech_stack = set()

        for file in files:
            path_lower = file.path.lower()

            for ext, tech in RepositoryService.EXTENSION_TO_TECH.items():
                if path_lower.endswith(ext):
                    tech_stack.add(tech)

            for config, tech in RepositoryService.CONFIG_TO_TECH.items():
                if config in path_lower:
                    tech_stack.add(tech)

        return sorted(tech_stack)

    @staticmethod
    def detect_frameworks(files: List[File]) -> List[str]:
        frameworks = set()

        for file in files:
            if not file.content:
                continue

            content_lower = file.content.lower()
            path_lower = file.path.lower()

            if "fastapi" in content_lower or "fastapi" in path_lower:
                frameworks.add("FastAPI")
            if "flask" in content_lower or "flask" in path_lower:
                frameworks.add("Flask")
            if "django" in content_lower or "django" in path_lower:
                frameworks.add("Django")
            if "react" in content_lower or "react" in path_lower:
                frameworks.add("React")
            if "vue" in content_lower:
                frameworks.add("Vue.js")
            if "express" in content_lower:
                frameworks.add("Express")
            if "next" in content_lower and "nextjs" in path_lower:
                frameworks.add("Next.js")

        return sorted(frameworks)

    @staticmethod
    def get_key_components(files: List[File], architecture: Dict) -> List[Dict[str, str]]:
        components = []

        for file_path in architecture.get("entry_points", [])[:3]:
            components.append({
                "path": file_path,
                "type": "entry_point",
                "description": "Application entry point"
            })

        for file_path in architecture.get("config_files", [])[:2]:
            components.append({
                "path": file_path,
                "type": "config",
                "description": "Project configuration"
            })

        for file_path in architecture.get("documentation", [])[:2]:
            components.append({
                "path": file_path,
                "type": "documentation",
                "description": "Project documentation"
            })

        for file_path in architecture.get("tests", [])[:2]:
            components.append({
                "path": file_path,
                "type": "test",
                "description": "Test file"
            })

        return components

    @staticmethod
    def get_starting_files(architecture: Dict) -> List[Dict[str, str]]:
        starting_files = []

        for file_path in architecture.get("documentation", []):
            if "readme" in file_path.lower():
                starting_files.append({
                    "path": file_path,
                    "reason": "Start here - project documentation"
                })

        for file_path in architecture.get("entry_points", []):
            if any(x in file_path.lower() for x in ["main.py", "app.py", "index.js"]):
                starting_files.append({
                    "path": file_path,
                    "reason": "Main application entry point"
                })

        for file_path in architecture.get("config_files", []):
            if any(x in file_path.lower() for x in ["pyproject.toml", "package.json", "requirements.txt"]):
                starting_files.append({
                    "path": file_path,
                    "reason": "Dependencies and project setup"
                })

        seen = set()
        unique_files = []
        for f in starting_files:
            if f["path"] not in seen:
                seen.add(f["path"])
                unique_files.append(f)

        return unique_files[:5]

    @staticmethod
    def generate_purpose(repository: Repository, files: List[File], architecture: Dict) -> str:
        name = repository.name.replace("-", " ").replace("_", " ")

        readme_content = None
        for file in files:
            if "readme" in file.path.lower() and file.content:
                readme_content = file.content[:500]
                break

        if readme_content:
            lines = readme_content.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("!") and len(line) > 20:
                    return line[:200]

        tech_stack = RepositoryService.detect_tech_stack(files)
        main_tech = tech_stack[0] if tech_stack else "code"

        return f"A {main_tech} project named {name}"

    @staticmethod
    def generate_ai_insight(
        repository: Repository,
        files: List[File],
        architecture: Dict,
        tech_stack: List[str],
        frameworks: List[str],
        stats: Dict,
    ) -> Dict:
        name = repository.name.replace("-", " ").replace("_", " ")
        total_files = stats.get("total_files", len(files))
        total_commits = stats.get("total_commits", 0)

        has_frontend = len(architecture.get("entry_points", [])) > 0 or any(
            "frontend" in f.path.lower() or "src" in f.path.lower()
            for f in files[:50]
        )
        has_backend = any(
            any(kw in f.path.lower() for kw in ["api", "routes", "services", "backend", "database"])
            for f in files[:50]
        )
        has_tests = len(architecture.get("tests", [])) > 0
        has_docs = len(architecture.get("documentation", [])) > 0

        flow_parts = []
        if has_frontend:
            flow_parts.append("Frontend")
        if has_backend:
            flow_parts.append("Backend")
        if has_tests:
            flow_parts.append("Tests")
        main_flow = " → ".join(flow_parts) if flow_parts else "Single-tier application"

        if total_files < 20:
            complexity = "Low"
            onboarding = "5 minutes"
        elif total_files < 80:
            complexity = "Medium"
            onboarding = "10 minutes"
        elif total_files < 200:
            complexity = "High"
            onboarding = "20 minutes"
        else:
            complexity = "Very High"
            onboarding = "30+ minutes"

        tech_desc = ", ".join(tech_stack[:3]) if tech_stack else "code"
        fw_desc = f" using {', '.join(frameworks[:2])}" if frameworks else ""
        insight_text = f"This repository is a {tech_desc}{fw_desc} application."

        return {
            "text": insight_text,
            "main_flow": main_flow,
            "estimated_onboarding": onboarding,
            "complexity": complexity,
            "tech_stack": tech_stack,
            "frameworks": frameworks,
        }

    @staticmethod
    def generate_learning_path(
        architecture: Dict,
        starting_files: List[Dict],
        tech_stack: List[str],
    ) -> List[Dict]:
        steps = []
        step_num = 1

        readme_files = [f for f in architecture.get("documentation", []) if "readme" in f.lower()]
        if readme_files:
            steps.append({
                "step": step_num,
                "title": "Read the Documentation",
                "description": "Understand the project purpose and setup instructions.",
                "file": readme_files[0],
                "file_type": "Documentation",
            })
            step_num += 1

        entry_files = architecture.get("entry_points", [])[:2]
        for ef in entry_files:
            steps.append({
                "step": step_num,
                "title": f"Explore Entry Point",
                "description": "Learn how the application starts and initializes.",
                "file": ef,
                "file_type": "Entry Point",
            })
            step_num += 1

        config_files = architecture.get("config_files", [])[:1]
        for cf in config_files:
            steps.append({
                "step": step_num,
                "title": "Review Configuration",
                "description": "Understand dependencies, build process, and project setup.",
                "file": cf,
                "file_type": "Configuration",
            })
            step_num += 1

        frontend_files = architecture.get("frontend", [])
        if frontend_files:
            steps.append({
                "step": step_num,
                "title": "Understand the Frontend",
                "description": "Explore the client-side components and UI structure.",
                "file": frontend_files[0],
                "file_type": "Frontend",
            })
            step_num += 1

        backend_files = architecture.get("backend", [])
        if backend_files:
            steps.append({
                "step": step_num,
                "title": "Understand the Backend",
                "description": "Explore server-side logic, API routes, and services.",
                "file": backend_files[0],
                "file_type": "Backend",
            })
            step_num += 1

        test_files = architecture.get("tests", [])[:1]
        for tf in test_files:
            steps.append({
                "step": step_num,
                "title": "Review Tests",
                "description": "See how the codebase is tested and what coverage exists.",
                "file": tf,
                "file_type": "Test",
            })
            step_num += 1

        if len(steps) < 3 and starting_files:
            for sf in starting_files:
                if sf["path"] not in [s["file"] for s in steps]:
                    steps.append({
                        "step": step_num,
                        "title": "Review Key File",
                        "description": sf["reason"],
                        "file": sf["path"],
                        "file_type": "Important",
                    })
                    step_num += 1
                    if len(steps) >= 5:
                        break

        return steps[:5]

    @staticmethod
    def generate_questions_to_ask(
        architecture: Dict,
        tech_stack: List[str],
        frameworks: List[str],
    ) -> List[Dict]:
        questions = []

        questions.append({
            "question": "How does the main application flow work?",
            "category": "Architecture",
        })

        if architecture.get("entry_points"):
            questions.append({
                "question": "What happens when the application starts?",
                "category": "Getting Started",
            })

        if architecture.get("backend") or any(
            any(kw in "".join(architecture.get("backend", [])) for kw in ["api", "route"])
            for _ in [1]
        ):
            questions.append({
                "question": "Where are the API routes defined?",
                "category": "Architecture",
            })

        if "React" in frameworks or "react" in [t.lower() for t in tech_stack]:
            questions.append({
                "question": "How is the frontend state managed?",
                "category": "Frontend",
            })

        if any("database" in "".join(architecture.get("backend", [])).lower() for _ in [1]):
            questions.append({
                "question": "How is the database structured?",
                "category": "Data",
            })

        if architecture.get("tests"):
            questions.append({
                "question": "How are tests organized and what do they cover?",
                "category": "Quality",
            })

        if any("auth" in "".join(architecture.get("backend", [])).lower() for _ in [1]):
            questions.append({
                "question": "How does authentication work?",
                "category": "Security",
            })

        questions.append({
            "question": "What are the main modules and how do they connect?",
            "category": "Architecture",
        })

        return questions[:6]

    @staticmethod
    def get_summary(db: Session, repository_id: int) -> Optional[Dict]:
        repository = (
            db.query(Repository)
            .filter(Repository.id == repository_id)
            .first()
        )

        if not repository:
            return None

        files = RepositoryService.get_files_by_repository(db, repository_id)
        architecture = RepositoryService.get_architecture(db, repository_id)
        stats = RepositoryService.get_repository_stats(db, repository_id)

        tech_stack = RepositoryService.detect_tech_stack(files)
        frameworks = RepositoryService.detect_frameworks(files)
        key_components = RepositoryService.get_key_components(files, architecture)
        starting_files = RepositoryService.get_starting_files(architecture)
        purpose = RepositoryService.generate_purpose(repository, files, architecture)

        ai_insight = RepositoryService.generate_ai_insight(
            repository, files, architecture, tech_stack, frameworks, stats
        )
        learning_path = RepositoryService.generate_learning_path(
            architecture, starting_files, tech_stack
        )
        questions_to_ask = RepositoryService.generate_questions_to_ask(
            architecture, tech_stack, frameworks
        )

        return {
            "repository_id": repository_id,
            "name": repository.name,
            "purpose": purpose,
            "tech_stack": tech_stack,
            "frameworks": frameworks,
            "architecture": {
                "entry_points": architecture.get("entry_points", []),
                "config_files": architecture.get("config_files", []),
                "documentation": architecture.get("documentation", []),
                "tests": architecture.get("tests", []),
            },
            "key_components": key_components,
            "starting_files": starting_files,
            "stats": stats,
            "ai_insight": ai_insight,
            "learning_path": learning_path,
            "questions_to_ask": questions_to_ask,
        }
