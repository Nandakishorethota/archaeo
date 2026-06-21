from collections import defaultdict


class ArchitectureService:

    FRONTEND_KEYWORDS = [
        "frontend",
        "src",
        "components",
        "pages",
        "hooks",
        "layouts",
        "views",
        "public",
    ]

    BACKEND_KEYWORDS = [
        "backend",
        "api",
        "routes",
        "controllers",
        "services",
        "models",
        "database",
        "repositories",
        "schemas",
    ]

    INFRA_KEYWORDS = [
        ".github",
        "docker",
        "dockerfile",
        "k8s",
        "kubernetes",
        "terraform",
        "nginx",
        "compose",
    ]

    ENTRY_POINT_FILES = [
        "main.py",
        "app.py",
        "server.py",
        "run.py",
        "manage.py",
        "wsgi.py",
        "asgi.py",
        "index.js",
        "index.ts",
        "main.jsx",
        "main.tsx",
        "app.jsx",
        "app.tsx",
    ]

    CONFIG_FILES = [
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env",
    ]

    EXTENSION_TYPES = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".md": "Markdown",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".toml": "TOML",
        ".json": "JSON",
        ".txt": "Text",
        ".html": "HTML",
        ".css": "CSS",
        ".sh": "Shell",
    }

    @staticmethod
    def get_file_extension(path: str) -> str:
        lower = path.lower()
        for ext, label in ArchitectureService.EXTENSION_TYPES.items():
            if lower.endswith(ext):
                return label
        if "dockerfile" in lower:
            return "Docker"
        if lower.endswith(".env"):
            return "Environment"
        return "File"

    @staticmethod
    def get_file_purpose(path: str, category: str) -> str:
        lower = path.lower()
        filename = lower.split("/")[-1] if "/" in lower else lower

        purpose_map = {
            "entry_points": {
                "main": "Application bootstrap and root initialization",
                "app": "Primary application structure and routing",
                "index": "Application entry point",
                "server": "Server startup and configuration",
                "manage": "CLI management commands",
                "run": "Application runner",
                "wsgi": "WSGI server interface",
                "asgi": "ASGI server interface",
            },
            "frontend": {
                "component": "Reusable UI component",
                "page": "Page-level view component",
                "hook": "Custom React hook",
                "layout": "Layout wrapper component",
                "context": "React context provider",
                "store": "State management",
                "style": "Stylesheet",
                "test": "Frontend test",
            },
            "backend": {
                "route": "API route handler",
                "controller": "Request controller",
                "service": "Business logic service",
                "model": "Data model definition",
                "schema": "Validation schema",
                "database": "Database configuration",
                "migration": "Database migration",
                "middleware": "Request middleware",
            },
            "configuration": {
                "requirements": "Python dependencies",
                "pyproject": "Project metadata and build config",
                "package": "Node.js dependencies and scripts",
                "dockerfile": "Container build instructions",
                "docker-compose": "Multi-container orchestration",
                "tsconfig": "TypeScript configuration",
                "vite": "Build tool configuration",
                ".env": "Environment variables",
            },
            "documentation": {
                "readme": "Project overview and setup guide",
                "changelog": "Version history",
                "contributing": "Contribution guidelines",
                "license": "License information",
            },
            "tests": {
                "test": "Test suite",
                "spec": "Test specification",
                "conftest": "Test fixtures and configuration",
                "fixture": "Test data fixtures",
            },
            "infrastructure": {
                "dockerfile": "Container definition",
                "compose": "Container orchestration",
                "nginx": "Web server configuration",
                "terraform": "Infrastructure as code",
                "workflow": "CI/CD pipeline",
                "deploy": "Deployment configuration",
            },
        }

        category_purposes = purpose_map.get(category, {})
        for keyword, purpose in category_purposes.items():
            if keyword in filename:
                return purpose

        return "Source file"

    @staticmethod
    def get_file_importance(path: str, category: str) -> str:
        lower = path.lower()
        filename = lower.split("/")[-1] if "/" in lower else lower

        if category == "entry_points":
            return "High"
        if category == "configuration":
            if any(x in filename for x in ["package.json", "pyproject.toml", "requirements.txt"]):
                return "High"
            return "Medium"
        if category == "documentation":
            if "readme" in filename:
                return "High"
            return "Medium"
        if category == "tests":
            return "Medium"
        if category == "frontend":
            if any(x in filename for x in ["app.jsx", "app.tsx", "main.jsx", "main.tsx", "index.jsx"]):
                return "High"
            return "Medium"
        if category == "backend":
            if any(x in filename for x in ["main.py", "app.py", "server.py"]):
                return "High"
            return "Medium"
        return "Low"

    @staticmethod
    def analyze(files):
        architecture = {
            "frontend": [],
            "backend": [],
            "infrastructure": [],
            "documentation": [],
            "configuration": [],
            "entry_points": [],
            "tests": [],
            "other": [],
        }

        file_context = {}

        for file in files:
            path = file.path
            path_lower = path.lower()

            categories_assigned = []

            if any(path_lower.endswith(x) for x in ArchitectureService.ENTRY_POINT_FILES):
                architecture["entry_points"].append(path)
                categories_assigned.append("entry_points")

            if "readme" in path_lower or path_lower.endswith(".md"):
                architecture["documentation"].append(path)
                categories_assigned.append("documentation")

            if any(x in path_lower for x in ArchitectureService.CONFIG_FILES):
                architecture["configuration"].append(path)
                categories_assigned.append("configuration")

            if "test" in path_lower:
                architecture["tests"].append(path)
                categories_assigned.append("tests")

            if any(x in path_lower for x in ArchitectureService.FRONTEND_KEYWORDS):
                architecture["frontend"].append(path)
                categories_assigned.append("frontend")
            elif any(x in path_lower for x in ArchitectureService.BACKEND_KEYWORDS):
                architecture["backend"].append(path)
                categories_assigned.append("backend")
            elif any(x in path_lower for x in ArchitectureService.INFRA_KEYWORDS):
                architecture["infrastructure"].append(path)
                categories_assigned.append("infrastructure")
            elif not categories_assigned:
                architecture["other"].append(path)

            primary_category = categories_assigned[0] if categories_assigned else "other"
            file_context[path] = {
                "file_type": ArchitectureService.get_file_extension(path),
                "purpose": ArchitectureService.get_file_purpose(path, primary_category),
                "importance": ArchitectureService.get_file_importance(path, primary_category),
            }

        return {
            "frontend": architecture["frontend"],
            "backend": architecture["backend"],
            "infrastructure": architecture["infrastructure"],
            "documentation": architecture["documentation"],
            "configuration": architecture["configuration"],
            "entry_points": architecture["entry_points"],
            "tests": architecture["tests"],
            "other": architecture["other"],
            "file_context": file_context,
            "summary": {
                "frontend_files": len(architecture["frontend"]),
                "backend_files": len(architecture["backend"]),
                "infra_files": len(architecture["infrastructure"]),
                "docs_files": len(architecture["documentation"]),
                "config_files": len(architecture["configuration"]),
                "entry_points": len(architecture["entry_points"]),
                "test_files": len(architecture["tests"]),
            },
        }