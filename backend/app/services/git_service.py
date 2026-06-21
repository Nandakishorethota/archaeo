from git import Repo
import tempfile
import shutil
import os


class GitService:

    @staticmethod
    def clone_repository(repo_url: str):

        temp_dir = tempfile.mkdtemp()

        try:

            repo = Repo.clone_from(
                repo_url,
                temp_dir
            )

            repo_name = (
              repo_url.rstrip("/")
              .split("/")[-1]
              .replace(".git", "")
            )

            return {
                "repo": repo,
                "path": temp_dir,
                "name": repo_name
            }

        except Exception as e:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

            raise Exception(
                f"Clone failed: {str(e)}"
            )

    @staticmethod
    def cleanup_temp_dir(temp_dir: str):
        """Clean up temporary directory after extracting data."""
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
        
    @staticmethod
    def extract_commits(repo):

        commits = []

        for commit in repo.iter_commits():

            commits.append(
               {
                   "hash": commit.hexsha,
                   "author": str(commit.author),
                   "message": commit.message.strip(),
                   "commit_date": commit.committed_datetime
               }
        )

        return commits
    
    @staticmethod
    def extract_files(path):

       files = []

       for root, dirs, filenames in os.walk(path):

           for filename in filenames:

                full_path = os.path.join(
                   root,
                   filename
                )

                relative_path = os.path.relpath(
                    full_path,
                    path
                )

                files.append(
                   relative_path
                )

       return files
    

    @staticmethod
    def read_file_content(file_path):

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

             return file.read()

        except Exception:

           return None