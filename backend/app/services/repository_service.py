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
    def answer_simple_question(
        db: Session, repository_id: int, question: str
    ) -> Dict:
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"=== Simple Question Request ===")
        logger.info(f"Question: {question}")

        if RepositoryService._detect_file_existence_question(question):
            filename = RepositoryService._extract_filename_from_question(question)
            logger.info(f"File existence question detected. Extracted filename: {filename}")
            if filename:
                matches = RepositoryService._verify_file_existence(db, repository_id, filename)
                logger.info(f"File existence verification: {len(matches)} matches found")
                if matches:
                    paths = "\n".join([f"  {m['path']}" for m in matches])
                    answer = f"{filename} exists.\n\nFound at:\n{paths}\n\nCategory: {matches[0]['category']}"
                else:
                    answer = f"{filename} was not found in the repository file index."
                return {
                    "answer": answer,
                    "files": [m["path"] for m in matches],
                }

        lightweight_index = RepositoryService.get_lightweight_file_index(db, repository_id)

        answer = RepositoryService._answer_from_metadata(question, lightweight_index)
        if answer:
            logger.info(f"Answer provided from metadata: {answer}")
            return {
                "answer": answer,
                "files": []
            }

        logger.info(f"Question requires AI analysis - proceeding to AI answer")
        return RepositoryService.answer_question_with_ai(db, repository_id, question)

    @staticmethod
    def answer_question_with_ai(
        db: Session, repository_id: int, question: str
    ) -> Dict:
        from app.services.ai_summary_service import ai_summary_service
        import logging
        
        logger = logging.getLogger(__name__)
        
        logger.info(f"=== AI Answer Request ===")
        logger.info(f"Question: {question}")
        
        files = RepositoryService.get_files_by_repository(db, repository_id)
        
        logger.info(f"Total files available: {len(files)}")
        
        # Build repository knowledge index
        repo_knowledge = RepositoryService._build_repository_knowledge_index(files)
        logger.info(f"Repository type: {repo_knowledge['repository_type']}")
        logger.info(f"Technology stack: {repo_knowledge['tech_stack']}")
        logger.info(f"Entry points: {repo_knowledge['entry_points']}")
        
        # Build lightweight file index for metadata-based answers
        lightweight_index = RepositoryService.get_lightweight_file_index(db, repository_id)
        
        # Check if question can be answered directly from metadata
        answer_from_metadata = RepositoryService._answer_from_metadata(question, lightweight_index)
        if answer_from_metadata:
            logger.info(f"Answer provided from metadata: {answer_from_metadata}")
            return {
                "answer": answer_from_metadata,
                "files": []
            }
        
        # File existence questions: verify against ALL repository paths first
        if RepositoryService._detect_file_existence_question(question):
            filename = RepositoryService._extract_filename_from_question(question)
            logger.info(f"File existence question detected in AI path. Extracted filename: {filename}")
            if filename:
                matches = RepositoryService._verify_file_existence(db, repository_id, filename)
                logger.info(f"File existence verification: {len(matches)} matches found")
                if matches:
                    paths = "\n".join([f"  {m['path']}" for m in matches])
                    answer = f"{filename} exists.\n\nFound at:\n{paths}\n\nCategory: {matches[0]['category']}"
                else:
                    answer = f"{filename} was not found in the repository file index."
                return {
                    "answer": answer,
                    "files": [m["path"] for m in matches],
                }
        
        # Detect explicit file references in question
        explicit_file = RepositoryService._detect_explicit_file_reference(question)
        logger.info(f"Explicit file reference detected: {explicit_file}")
        
        # Enhanced file categorization
        important_files = []
        file_scores = []
        
        for file in files[:20]:
            if file.content:
                file_info = f"{file.path}: {file.content[:80]}..."
                
                score = 0
                keywords = re.sub(r'[?!.]', '', question.lower()).split()
                for keyword in keywords:
                    score += file.content.lower().count(keyword)
                
                file_type = RepositoryService._get_file_type(file.path)
                category = RepositoryService._categorize_file(file.path, repo_knowledge)
                
                file_scores.append({
                    "path": file.path,
                    "score": score,
                    "type": file_type,
                    "category": category,
                    "info": file_info,
                    "importance": RepositoryService._calculate_file_importance(file.path, repo_knowledge)
                })
        
        logger.info(f"File scores before intent ranking:")
        for fs in file_scores[:10]:
            logger.info(f"  - {fs['path']} (type: {fs['type']}, category: {fs['category']}, score: {fs['score']}, importance: {fs['importance']})")
        
        file_scores.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Top 10 files by keyword score:")
        for fs in file_scores[:10]:
            logger.info(f"  - {fs['path']} (type: {fs['type']}, category: {fs['category']}, score: {fs['score']})")
        
        intent_ranking = RepositoryService._apply_intent_ranking(question, file_scores, repo_knowledge)
        
        logger.info(f"Top 10 files after intent ranking:")
        for fs in intent_ranking[:10]:
            logger.info(f"  - {fs['path']} (type: {fs['type']}, category: {fs['category']}, score: {fs['score']}, intent_score: {fs.get('intent_score', 0)}, importance: {fs['importance']})")
        
        # If explicit file reference detected, verify it exists and prioritize it
        if explicit_file:
            logger.info(f"Verifying explicit file reference: {explicit_file}")
            verified = RepositoryService._verify_file_existence(db, repository_id, explicit_file)
            if verified:
                matched_path = verified[0]['path']
                logger.info(f"File verified in repository: {matched_path}")
                
                # Load actual file content directly from database
                target_file = None
                for f in files:
                    if f.path == matched_path:
                        target_file = f
                        break
                
                if target_file and target_file.content:
                    logger.info(f"File loaded successfully. Content length: {len(target_file.content)} characters")
                    
                    # Build specialized prompt with actual file content
                    file_type = RepositoryService._get_file_type(matched_path)
                    prompt = f"""You are explaining a repository file.

File: {matched_path}
File Type: {file_type}

Content:
{target_file.content}

Question: {question}

Explain the purpose, responsibilities, imports, exports, state management, API usage, and component behavior. Be concise and specific to this file."""
                    
                    logger.info(f"File explanation prompt built. Prompt length: {len(prompt)} characters")
                    
                    try:
                        response = ai_summary_service.client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an expert software architect explaining repository files based on their actual content."
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
                        logger.info(f"AI response generated for file explanation")
                        
                        return {
                            "answer": answer,
                            "files": [matched_path],
                        }
                    except Exception as e:
                        logger.error(f"Error generating AI answer: {str(e)}")
                        return {
                            "answer": f"Error generating AI answer: {str(e)}",
                            "files": [matched_path],
                        }
                else:
                    logger.info(f"File '{matched_path}' found but content not available. Proceeding with normal retrieval.")
                    
                    # Try to match in intent_ranking as fallback
                    for fs in intent_ranking:
                        path_filename = fs["path"].split("/")[-1].split("\\")[-1]
                        if path_filename.lower() == explicit_file.lower() or fs["path"].lower().endswith(explicit_file.lower()):
                            intent_ranking.remove(fs)
                            intent_ranking.insert(0, fs)
                            logger.info(f"Matched and prioritized: {fs['path']}")
                            break
            else:
                logger.info(f"File '{explicit_file}' not found in repository. Proceeding without prioritization.")
        
        selected_files = intent_ranking[:10]
        important_files = [fs["info"] for fs in selected_files]
        
        # Build enhanced prompt with file contents
        prompt = f"""Answer this question about the repository in 2-3 lines:

Repository Overview:
- Type: {repo_knowledge['repository_type']}
- Technology Stack: {repo_knowledge['tech_stack']}
- Entry Points: {repo_knowledge['entry_points']}
- Frontend Files: {len(repo_knowledge['frontend_files'])}
- Backend Files: {len(repo_knowledge['backend_files'])}
- Database Files: {len(repo_knowledge['database_files'])}
- Infrastructure Files: {len(repo_knowledge['infrastructure_files'])}
- Configuration Files: {len(repo_knowledge['config_files'])}
- Documentation Files: {len(repo_knowledge['documentation_files'])}
- Test Files: {len(repo_knowledge['test_files'])}

Repository File Inventory:
- Frontend Files: {', '.join(lightweight_index['repository_structure']['frontend_files'][:15])}{'...' if len(lightweight_index['repository_structure']['frontend_files']) > 15 else ''}
- Backend Files: {', '.join(lightweight_index['repository_structure']['backend_files'][:15])}{'...' if len(lightweight_index['repository_structure']['backend_files']) > 15 else ''}
- Documentation Files: {', '.join(lightweight_index['repository_structure']['documentation_files'][:10])}{'...' if len(lightweight_index['repository_structure']['documentation_files']) > 10 else ''}
- Test Files: {', '.join(lightweight_index['repository_structure']['test_files'][:10])}{'...' if len(lightweight_index['repository_structure']['test_files']) > 10 else ''}

Selected Files for Context:
{chr(10).join([f'  - {fs["path"]}' for fs in selected_files])}

Selected File Contents:
{chr(10).join([f'  - {fs["path"]}:\n    {fs["info"]}' for fs in selected_files if fs["info"]])}

Question: {question}

Provide a concise 2-3 line answer based on the repository content. Answer equally about both frontend and backend components. If the question cannot be answered from the available content, please say so."""
        
        logger.info(f"Final context sent to OpenRouter:")
        logger.info(f"  - Question: {question}")
        logger.info(f"  - Repository Type: {repo_knowledge['repository_type']}")
        logger.info(f"  - Technology Stack: {repo_knowledge['tech_stack']}")
        logger.info(f"  - Files: {important_files}")
        logger.info(f"  - Total files in context: {len(important_files)}")
        logger.info(f"  - Selected files: {[fs['path'] for fs in selected_files]}")
        logger.info(f"  - Context length: {len(prompt)} characters")
        
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
            
            logger.info(f"AI Answer: {answer}")
            
            return {
                "answer": answer,
                "files": important_files
            }
        except Exception as e:
            logger.error(f"Error generating AI answer: {str(e)}")
            return {
                "answer": f"Error generating AI answer: {str(e)}",
                "files": []
            }

    @staticmethod
    def _detect_explicit_file_reference(question: str) -> Optional[str]:
        """Detect explicit file references in a question and return original-cased filename."""
        import re
        
        # Patterns to match file references (case-insensitive)
        patterns = [
            r'explain\s+(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))',
            r'what\s+does\s+(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))\s+do',
            r'analyze\s+(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))',
            r'explore\s+(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))',
            r'look\s+at\s+(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))',
            r'review\s+(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))',
            r'check\s+(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))',
            r'\b(\S+\.(?:jsx?|tsx?|js|ts|py|md|txt|json|yml|yaml|toml))\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                matched_lower = matches[0].lower()
                # Try to find the original-cased word in the question
                for word in question.split():
                    if word.lower() == matched_lower or word.lower().startswith(matched_lower.split('.')[0]):
                        return word
                # Fallback: return the lowercase match
                return matched_lower
        
        return None

    @staticmethod
    def _detect_file_existence_question(question: str) -> bool:
        """Detect questions asking about file existence."""
        lower = question.lower()
        patterns = [
            r'does\s+(it|this|the\s+repo|this\s+repo|the\s+repository|this\s+repository)\s+have\s+\S+\.\w+',
            r'is\s+\S+\.\w+\s+(present|there|included|available)',
            r'does\s+this\s+repository\s+contain\s+\S+\.\w+',
            r'is\s+there\s+a\s+\S+\.\w+',
            r'do\s+we\s+have\s+\S+\.\w+',
            r'can\s+you\s+find\s+\S+\.\w+',
            r'where\s+is\s+\S+\.\w+',
            r'show\s+me\s+\S+\.\w+',
            r'locate\s+\S+\.\w+',
        ]
        for pattern in patterns:
            if re.search(pattern, lower):
                return True
        return False

    @staticmethod
    def _extract_filename_from_question(question: str) -> Optional[str]:
        """Extract a filename from a file existence question, preserving original case."""
        ext_pattern = r'(?:jsx?|tsx?|py|md|txt|json|yml|yaml|toml)'
        patterns = [
            rf'does\s+(?:it|this|the\s+repo|this\s+repo|the\s+repository|this\s+repository)\s+have\s+(\S+\.{ext_pattern})',
            rf'is\s+(\S+\.{ext_pattern})\s+(?:present|there|included|available)',
            rf'does\s+this\s+repository\s+contain\s+(\S+\.{ext_pattern})',
            rf'is\s+there\s+a\s+(\S+\.{ext_pattern})',
            rf'do\s+we\s+have\s+(\S+\.{ext_pattern})',
            rf'can\s+you\s+find\s+(\S+\.{ext_pattern})',
            rf'where\s+is\s+(\S+\.{ext_pattern})',
            rf'show\s+me\s+(\S+\.{ext_pattern})',
            rf'locate\s+(\S+\.{ext_pattern})',
        ]
        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                candidate = match.group(1)
                for word in question.split():
                    if word.lower().rstrip("?.!") == candidate.lower():
                        return word.rstrip("?.!")
                return candidate
        return None

    @staticmethod
    def _verify_file_existence(
        db: Session, repository_id: int, filename: str
    ) -> List[Dict[str, str]]:
        """Search ALL repository file paths for a filename. Case-insensitive, exact + partial match."""
        import logging
        logger = logging.getLogger(__name__)

        all_files = RepositoryService.get_files_by_repository(db, repository_id)
        filename_lower = filename.lower()
        name_without_ext = filename_lower.rsplit(".", 1)[0] if "." in filename_lower else filename_lower

        exact_matches = []
        partial_matches = []

        for f in all_files:
            path_lower = f.path.lower()
            basename = path_lower.split("/")[-1].split("\\")[-1]

            if basename == filename_lower:
                exact_matches.append(f)
            elif basename.startswith(name_without_ext):
                partial_matches.append(f)

        results = []
        seen = set()
        for f in exact_matches + partial_matches:
            if f.path not in seen:
                seen.add(f.path)
                category = RepositoryService._get_file_type(f.path)
                results.append({
                    "path": f.path,
                    "category": category,
                })

        logger.info(f"File existence check: filename={filename}")
        logger.info(f"  Exact matches: {len(exact_matches)}")
        logger.info(f"  Partial matches: {len(partial_matches)}")
        logger.info(f"  Total unique results: {len(results)}")
        for r in results:
            logger.info(f"    - {r['path']} (category: {r['category']})")

        return results

    @staticmethod
    def _is_simple_metadata_question(question: str) -> bool:
        lower_question = question.lower()
        
        simple_keywords = [
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
            "explain main.jsx",
            "what does app.jsx do",
            "analyze auth.py",
            "explain repository_service.py",
            "what does",
            "explain",
            "analyze",
            "explore",
            "look at",
            "review",
            "check"
        ]
        
        return any(keyword in lower_question for keyword in simple_keywords)

    @staticmethod
    def _answer_from_metadata(question: str, lightweight_index: dict) -> Optional[str]:
        lower_question = question.lower()
        
        # Questions about listing files
        if any(keyword in lower_question for keyword in ["list react files", "react files", "frontend files", "what frontend files"]):
            frontend_files = lightweight_index["repository_structure"]["frontend_files"]
            if frontend_files:
                return f"React files available: {', '.join(frontend_files)}"
        
        elif any(keyword in lower_question for keyword in ["list backend files", "backend files", "what backend files"]):
            backend_files = lightweight_index["repository_structure"]["backend_files"]
            if backend_files:
                return f"Backend files available: {', '.join(backend_files)}"
        
        elif any(keyword in lower_question for keyword in ["what files exist", "what files are available", "list all files"]):
            all_files = []
            for category, files in lightweight_index["repository_structure"].items():
                if files:
                    all_files.extend(files)
            
            if all_files:
                return f"Files available: {', '.join(all_files[:25])}{'...' if len(all_files) > 25 else ''}"
        
        elif any(keyword in lower_question for keyword in ["what services exist", "what services", "services"]):
            service_files = [f for f in lightweight_index["repository_structure"]["backend_files"] if any(x in f.lower() for x in ["service", "api", "route", "controller"])]
            if service_files:
                return f"Service files available: {', '.join(service_files)}"
        
        elif any(keyword in lower_question for keyword in ["what database files", "database files", "models"]):
            db_files = lightweight_index["repository_structure"]["database_files"]
            if db_files:
                return f"Database files available: {', '.join(db_files)}"
        
        elif any(keyword in lower_question for keyword in ["what infrastructure files", "infrastructure", "docker"]):
            infra_files = lightweight_index["repository_structure"]["infrastructure_files"]
            if infra_files:
                return f"Infrastructure files available: {', '.join(infra_files)}"
        
        elif any(keyword in lower_question for keyword in ["what config files", "config", "configuration"]):
            config_files = lightweight_index["repository_structure"]["config_files"]
            if config_files:
                return f"Configuration files available: {', '.join(config_files)}"
        
        elif any(keyword in lower_question for keyword in ["what documentation files", "documentation", "readme"]):
            doc_files = lightweight_index["repository_structure"]["documentation_files"]
            if doc_files:
                return f"Documentation files available: {', '.join(doc_files)}"
        
        elif any(keyword in lower_question for keyword in ["what test files", "test", "testing"]):
            test_files = lightweight_index["repository_structure"]["test_files"]
            if test_files:
                return f"Test files available: {', '.join(test_files)}"
        
        return None

    @staticmethod
    def _build_repository_knowledge_index(files: list) -> dict:
        knowledge = {
            "repository_type": "Unknown",
            "tech_stack": [],
            "entry_points": [],
            "frontend_files": [],
            "backend_files": [],
            "database_files": [],
            "infrastructure_files": [],
            "config_files": [],
            "documentation_files": [],
            "test_files": [],
            "api_files": [],
            "auth_files": [],
            "important_files": [],
            "readme_summary": ""
        }
        
        for file in files:
            path = file.path
            file_type = RepositoryService._get_file_type(path)
            
            if file_type == "architecture":
                knowledge["entry_points"].append(path)
            elif file_type == "frontend":
                knowledge["frontend_files"].append(path)
            elif file_type == "backend-api":
                knowledge["backend_files"].append(path)
                knowledge["api_files"].append(path)
            elif file_type == "backend-database":
                knowledge["database_files"].append(path)
            elif file_type == "backend-security":
                knowledge["auth_files"].append(path)
            elif file_type == "infrastructure":
                knowledge["infrastructure_files"].append(path)
            elif file_type == "config":
                knowledge["config_files"].append(path)
            elif file_type == "documentation":
                knowledge["documentation_files"].append(path)
            elif file_type == "test":
                knowledge["test_files"].append(path)
            
            if "readme" in path.lower() and file.content:
                knowledge["readme_summary"] = file.content[:200] + "..."
            
            if file_type in ["architecture", "frontend", "backend-api", "backend-database", "backend-security"]:
                knowledge["important_files"].append(path)
        
        knowledge["tech_stack"] = RepositoryService._detect_tech_stack(files)
        knowledge["repository_type"] = RepositoryService._detect_repository_type(knowledge)
        
        return knowledge

    @staticmethod
    def _get_file_type(path: str) -> str:
        lower_path = path.lower()
        
        # Enhanced React frontend detection
        if any(x in lower_path for x in [
            "frontend", "component", "page", "ui", "react", "hooks", "context", "provider", "store", "services", "utils", "lib", "src", "tsx", "jsx"
        ]):
            return "frontend"
        
        # Backend API detection
        elif any(x in lower_path for x in ["api", "route", "controller", "service", "endpoint", "router", "app.py", "main.py"]):
            return "backend-api"
        
        # Database detection
        elif any(x in lower_path for x in ["model", "repository", "entity", "schema", "database", "migration", "orm"]):
            return "backend-database"
        
        # Authentication detection
        elif any(x in lower_path for x in ["auth", "login", "security", "permission", "role", "user", "jwt", "token"]):
            return "backend-security"
        
        # Infrastructure detection
        elif any(x in lower_path for x in ["docker", "dockerfile", "kubernetes", "k8s", "helm", "compose", "docker-compose", "terraform", "ansible"]):
            return "infrastructure"
        
        # Configuration detection
        elif any(x in lower_path for x in ["config", "setting", "env", "yaml", "json", "toml", ".env", "ini", "pyproject", "setup.py"]):
            return "config"
        
        # Documentation detection
        elif any(x in lower_path for x in ["readme", "doc", "guide", "manual", "md", "rst", "changelog", "contributing"]):
            return "documentation"
        
        # Test detection
        elif any(x in lower_path for x in ["test", "spec", "unit", "integration", "e2e", "testing", "mock", "fixture", "conftest"]):
            return "test"
        
        # Architecture detection
        elif any(x in lower_path for x in ["main", "app", "index", "entry", "server", "__init__.py", "setup.cfg"]):
            return "architecture"
        
        # DevOps detection
        elif any(x in lower_path for x in ["ci", "cd", "github", "gitlab", "jenkins", "workflow", "pipeline", "github", "actions", "travis", "circle"]):
            return "devops"
        
        # Deployment detection
        elif any(x in lower_path for x in ["deploy", "deployment", "install", "setup", "provision", "deploy.sh", "Makefile"]):
            return "deployment"
        
        else:
            return "other"

    @staticmethod
    def _calculate_file_importance(path: str, knowledge: dict) -> int:
        importance = 0
        
        # Entry points are highly important
        if any(entry in path for entry in knowledge["entry_points"]):
            importance += 10
        
        # README files are very important
        if "readme" in path.lower():
            importance += 8
        
        # Tech stack files are important
        for tech in knowledge["tech_stack"]:
            if tech.lower() in path.lower():
                importance += 5
                break
        
        # Main application files are important
        if any(x in path.lower() for x in ["main.py", "app.py", "main.js", "app.js", "index.js", "server.js"]):
            importance += 7
        
        # Configuration files are important
        if any(x in path.lower() for x in ["dockerfile", "docker-compose.yml", "docker-compose.yaml", "package.json", "requirements.txt", "pyproject.toml"]):
            importance += 6
        
        # API files are important
        if any(x in path.lower() for x in ["api", "route", "controller", "service"]):
            importance += 5
        
        # Database files are important
        if any(x in path.lower() for x in ["model", "repository", "entity", "schema"]):
            importance += 4
        
        # Documentation files are important
        if any(x in path.lower() for x in ["readme", "doc", "guide", "manual"]):
            importance += 3
        
        # Test files are important
        if any(x in path.lower() for x in ["test", "spec"]):
            importance += 2
        
        return importance

    @staticmethod
    def _detect_tech_stack(files: list) -> list:
        tech_stack = set()
        
        for file in files:
            path_lower = file.path.lower()
            content_lower = file.content.lower() if file.content else ""
            
            if "react" in content_lower or "react" in path_lower:
                tech_stack.add("React")
            elif "vue" in content_lower or "vue" in path_lower:
                tech_stack.add("Vue.js")
            elif "angular" in content_lower or "angular" in path_lower:
                tech_stack.add("Angular")
            elif "express" in content_lower or "express" in path_lower:
                tech_stack.add("Express")
            elif "fastapi" in content_lower or "fastapi" in path_lower:
                tech_stack.add("FastAPI")
            elif "django" in content_lower or "django" in path_lower:
                tech_stack.add("Django")
            elif "flask" in content_lower or "flask" in path_lower:
                tech_stack.add("Flask")
            elif "node" in content_lower or "node" in path_lower:
                tech_stack.add("Node.js")
            elif "python" in content_lower or "python" in path_lower:
                tech_stack.add("Python")
            elif "java" in content_lower or "java" in path_lower:
                tech_stack.add("Java")
            elif "go" in content_lower or "go" in path_lower:
                tech_stack.add("Go")
            elif "rust" in content_lower or "rust" in path_lower:
                tech_stack.add("Rust")
            elif "php" in content_lower or "php" in path_lower:
                tech_stack.add("PHP")
            elif "ruby" in content_lower or "ruby" in path_lower:
                tech_stack.add("Ruby")
            elif "csharp" in content_lower or "csharp" in path_lower:
                tech_stack.add("C#")
            elif "cpp" in content_lower or "cpp" in path_lower:
                tech_stack.add("C++")
            elif "javascript" in content_lower or "javascript" in path_lower:
                tech_stack.add("JavaScript")
            elif "typescript" in content_lower or "typescript" in path_lower:
                tech_stack.add("TypeScript")
            
            if "docker" in content_lower or "docker" in path_lower:
                tech_stack.add("Docker")
            elif "kubernetes" in content_lower or "kubernetes" in path_lower:
                tech_stack.add("Kubernetes")
            elif "aws" in content_lower or "aws" in path_lower:
                tech_stack.add("AWS")
            elif "azure" in content_lower or "azure" in path_lower:
                tech_stack.add("Azure")
            elif "gcp" in content_lower or "gcp" in path_lower:
                tech_stack.add("GCP")
            
            if "postgresql" in content_lower or "postgres" in path_lower:
                tech_stack.add("PostgreSQL")
            elif "mysql" in content_lower or "mysql" in path_lower:
                tech_stack.add("MySQL")
            elif "mongodb" in content_lower or "mongodb" in path_lower:
                tech_stack.add("MongoDB")
            elif "sqlite" in content_lower or "sqlite" in path_lower:
                tech_stack.add("SQLite")
            elif "redis" in content_lower or "redis" in path_lower:
                tech_stack.add("Redis")
        
        return sorted(list(tech_stack))

    @staticmethod
    def _detect_repository_type(knowledge: dict) -> str:
        if knowledge["frontend_files"] and knowledge["backend_files"]:
            return "Full-stack Application"
        elif knowledge["frontend_files"]:
            return "Frontend Application"
        elif knowledge["backend_files"]:
            return "Backend API"
        elif knowledge["database_files"]:
            return "Database Project"
        elif knowledge["infrastructure_files"]:
            return "Infrastructure"
        elif knowledge["documentation_files"]:
            return "Documentation"
        else:
            return "Unknown"

    @staticmethod
    def _categorize_file(path: str, knowledge: dict) -> str:
        lower_path = path.lower()
        
        # Enhanced React frontend detection
        if any(x in lower_path for x in [
            "frontend", "component", "page", "ui", "react", "hooks", "context", "provider", "store", "services", "utils", "lib", "src", "tsx", "jsx"
        ]):
            return "frontend"
        
        # Backend API detection
        elif any(x in lower_path for x in ["api", "route", "controller", "service", "endpoint", "router", "app.py", "main.py"]):
            return "backend-api"
        
        # Database detection
        elif any(x in lower_path for x in ["model", "repository", "entity", "schema", "database", "migration", "orm"]):
            return "backend-database"
        
        # Authentication detection
        elif any(x in lower_path for x in ["auth", "login", "security", "permission", "role", "user", "jwt", "token"]):
            return "backend-security"
        
        # Infrastructure detection
        elif any(x in lower_path for x in ["docker", "dockerfile", "kubernetes", "k8s", "helm", "compose", "docker-compose", "terraform", "ansible"]):
            return "infrastructure"
        
        # Configuration detection
        elif any(x in lower_path for x in ["config", "setting", "env", "yaml", "json", "toml", ".env", "ini", "pyproject", "setup.py"]):
            return "config"
        
        # Documentation detection
        elif any(x in lower_path for x in ["readme", "doc", "guide", "manual", "md", "rst", "changelog", "contributing"]):
            return "documentation"
        
        # Test detection
        elif any(x in lower_path for x in ["test", "spec", "unit", "integration", "e2e", "testing", "mock", "fixture", "conftest"]):
            return "test"
        
        # Architecture detection
        elif any(x in lower_path for x in ["main", "app", "index", "entry", "server", "__init__.py", "setup.cfg"]):
            return "architecture"
        
        # DevOps detection
        elif any(x in lower_path for x in ["ci", "cd", "github", "gitlab", "jenkins", "workflow", "pipeline", "github", "actions", "travis", "circle"]):
            return "devops"
        
        # Deployment detection
        elif any(x in lower_path for x in ["deploy", "deployment", "install", "setup", "provision", "deploy.sh", "Makefile"]):
            return "deployment"
        
        else:
            return "other"

    @staticmethod
    def _apply_intent_ranking(question: str, file_scores: list, knowledge: dict) -> list:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"=== Intent Ranking Request ===")
        logger.info(f"Question: {question}")
        logger.info(f"Total files to rank: {len(file_scores)}")
        
        lower_question = question.lower()
        
        for fs in file_scores:
            intent_score = 0
            
            # Technical implementation intents
            detected_intent = None
            if any(x in lower_question for x in [
                "rendering", "graphics", "pipeline", "engine", "initialization",
                "texture loading", "memory", "networking", "api flow", "api",
                "network", "memory management", "buffer", "shader", "gpu",
                "rendering pipeline", "graphics pipeline", "engine architecture",
                "initialization process", "texture", "framebuffer", "render target",
                "draw call", "vertex shader", "fragment shader", "render pass",
                "command buffer", "descriptor set", "pipeline layout", "render queue"
            ]):
                detected_intent = "technical_implementation"
                # Prioritize source code files for technical implementation
                if fs["type"] in ["frontend", "backend-api", "backend-database", "backend-security", "architecture"]:
                    intent_score += 15
                elif fs["type"] in ["infrastructure", "config", "documentation"]:
                    intent_score += 5
                intent_score += fs["importance"] * 0.5
                
                # Boost score for source code extensions
                if fs["path"].endswith(('.c', '.cpp', '.h', '.hpp', '.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.java')):
                    intent_score += 10
                
                # Reduce score for documentation files
                if fs["path"].endswith(('.md', '.txt')) or any(doc in fs["path"].lower() for doc in ["readme", "faq", "history", "contributing", "issue_template"]):
                    intent_score -= 5
            
            # Architecture intents
            elif any(x in lower_question for x in ["architecture", "structure", "design", "flow", "main", "entry", "project overview", "overall", "what does this project", "explain the architecture"]):
                detected_intent = "architecture"
                if fs["type"] == "architecture":
                    intent_score += 15
                elif fs["type"] in ["frontend", "backend-api", "backend-database"]:
                    intent_score += 8
                elif fs["type"] in ["backend-security", "infrastructure", "config"]:
                    intent_score += 5
                intent_score += fs["importance"] * 0.5
            
            
            # Frontend intents
            elif any(x in lower_question for x in ["frontend", "ui", "component", "page", "react", "vue", "angular", "tsx", "jsx", "interface", "screen", "layout", "what does the frontend", "frontend architecture"]):
                if fs["type"] == "frontend":
                    intent_score += 15
                elif fs["type"] == "backend-api":
                    intent_score += 8
                elif fs["type"] == "architecture":
                    intent_score += 5
                intent_score += fs["importance"] * 0.5
            
            # Backend intents
            elif any(x in lower_question for x in ["backend", "server", "api", "route", "controller", "service", "endpoint", "router", "node", "express", "fastapi", "django", "flask", "what does the backend", "backend architecture"]):
                if fs["type"] in ["backend-api", "backend-database", "backend-security"]:
                    intent_score += 15
                elif fs["type"] == "frontend":
                    intent_score += 5
                elif fs["type"] == "architecture":
                    intent_score += 8
                intent_score += fs["importance"] * 0.5
            
            # Database intents
            elif any(x in lower_question for x in ["database", "db", "sql", "query", "model", "schema", "migration", "repository", "entity", "data storage", "database structure"]):
                if fs["type"] == "backend-database":
                    intent_score += 15
                elif fs["type"] in ["backend-api", "backend-security"]:
                    intent_score += 8
                elif fs["type"] == "config":
                    intent_score += 5
                intent_score += fs["importance"] * 0.5
            
            # Authentication intents
            elif any(x in lower_question for x in ["auth", "login", "security", "permission", "role", "user", "jwt", "token", "authentication", "authorize", "what does auth", "authentication system"]):
                if fs["type"] == "backend-security":
                    intent_score += 15
                elif fs["type"] == "backend-api":
                    intent_score += 10
                elif fs["type"] == "frontend":
                    intent_score += 8
                intent_score += fs["importance"] * 0.5
            
            # Infrastructure intents
            elif any(x in lower_question for x in ["deploy", "docker", "kubernetes", "k8s", "helm", "compose", "infrastructure", "server", "hosting", "cloud", "deployment", "infrastructure setup"]):
                if fs["type"] == "infrastructure":
                    intent_score += 15
                elif fs["type"] in ["backend-api", "config"]:
                    intent_score += 8
                intent_score += fs["importance"] * 0.5
            
            # Configuration intents
            elif any(x in lower_question for x in ["config", "setting", "env", "yaml", "json", "toml", ".env", "ini", "configuration", "config file"]):
                if fs["type"] == "config":
                    intent_score += 15
                elif fs["type"] in ["backend-api", "infrastructure"]:
                    intent_score += 8
                intent_score += fs["importance"] * 0.5
            
            # Testing intents
            elif any(x in lower_question for x in ["test", "spec", "unit", "integration", "e2e", "testing", "mock", "coverage", "testing setup"]):
                if fs["type"] == "test":
                    intent_score += 15
                elif fs["type"] in ["backend-api", "frontend"]:
                    intent_score += 8
                intent_score += fs["importance"] * 0.5
            
            # DevOps intents
            elif any(x in lower_question for x in ["ci", "cd", "github", "gitlab", "jenkins", "workflow", "pipeline", "build", "deploy", "devops", "continuous integration"]):
                if fs["type"] == "devops":
                    intent_score += 15
                elif fs["type"] in ["infrastructure", "config"]:
                    intent_score += 8
                intent_score += fs["importance"] * 0.5
            
            # General intents
            else:
                if fs["type"] in ["frontend", "backend-api", "backend-database", "backend-security"]:
                    intent_score += 5
                elif fs["type"] in ["architecture", "infrastructure", "config", "documentation"]:
                    intent_score += 3
                intent_score += fs["importance"] * 0.3
            
            fs["intent_score"] = intent_score
        
        file_scores.sort(key=lambda x: (x["score"] * 0.6 + x.get("intent_score", 0) * 0.4), reverse=True)
        
        logger.info(f"=== Intent Ranking Results ===")
        logger.info(f"Top 10 files after intent ranking:")
        for fs in file_scores[:10]:
            logger.info(f"  - {fs['path']} (type: {fs['type']}, category: {fs['category']}, score: {fs['score']}, intent_score: {fs.get('intent_score', 0)}, importance: {fs['importance']})")
        
        return file_scores


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

    @staticmethod
    def get_lightweight_file_index(db: Session, repository_id: int) -> Dict:
        import logging
        logger = logging.getLogger(__name__)

        files = RepositoryService.get_files_by_repository(db, repository_id)
        knowledge = RepositoryService._build_repository_knowledge_index(files)

        logger.info(f"Building lightweight file index for repository {repository_id}")
        logger.info(f"Total files: {len(files)}")
        logger.info(f"Frontend files: {len(knowledge['frontend_files'])}")
        logger.info(f"Backend files: {len(knowledge['backend_files'])}")
        logger.info(f"Documentation files: {len(knowledge['documentation_files'])}")
        logger.info(f"Test files: {len(knowledge['test_files'])}")
        logger.info(f"Infrastructure files: {len(knowledge['infrastructure_files'])}")
        logger.info(f"Config files: {len(knowledge['config_files'])}")

        file_index = {
            "repository_name": knowledge.get("repository_type", "Unknown"),
            "repository_structure": {
                "frontend_files": knowledge["frontend_files"],
                "backend_files": knowledge["backend_files"],
                "database_files": knowledge["database_files"],
                "infrastructure_files": knowledge["infrastructure_files"],
                "config_files": knowledge["config_files"],
                "documentation_files": knowledge["documentation_files"],
                "test_files": knowledge["test_files"],
                "api_files": knowledge["api_files"],
                "auth_files": knowledge["auth_files"],
                "important_files": knowledge["important_files"],
            },
            "tech_stack": knowledge["tech_stack"],
            "entry_points": knowledge["entry_points"],
            "readme_summary": knowledge["readme_summary"],
        }

        logger.info(f"Lightweight file index built successfully")
        logger.info(f"Frontend files in index: {len(file_index['repository_structure']['frontend_files'])}")
        logger.info(f"Backend files in index: {len(file_index['repository_structure']['backend_files'])}")
        logger.info(f"Context length: {len(str(file_index))} characters")

        return file_index

    @staticmethod
    def _format_answer_from_context(question: str, context: dict) -> str:
        """Format AI answer to be concise (2-3 lines)."""
        
        if "frontend" in question.lower() or "ui" in question.lower():
            frontend_files = context.get("frontend_files", [])
            if frontend_files:
                return f"This React frontend has {len(frontend_files)} components including {', '.join(frontend_files[:3])}."
        
        elif "backend" in question.lower() or "api" in question.lower():
            backend_files = context.get("backend_files", [])
            if backend_files:
                return f"This Node.js backend has {len(backend_files)} services including {', '.join(backend_files[:3])}."
        
        elif "tech stack" in question.lower() or "technology" in question.lower():
            tech_stack = context.get("tech_stack", [])
            if tech_stack:
                return f"Tech stack: {', '.join(tech_stack)}. Architecture: {context.get('repository_type', 'Unknown')}."
        
        elif "file" in question.lower():
            all_files = context.get("frontend_files", []) + context.get("backend_files", [])
            if all_files:
                return f"Repository contains {len(all_files)} main files including {', '.join(all_files[:3])}."
        
        else:
            return f"This {context.get('repository_type', 'repository')} has {len(all_files)} main files with {', '.join(context.get('tech_stack', []))}."
