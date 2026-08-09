"""
GitHub Sync Service
Sincroniza recursos desde el repositorio de GitHub cuando está en producción.
Fallback a carpeta local cuando está en desarrollo.
"""
import os
import json
import base64
import httpx
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class GitHubConfig:
    token: str
    owner: str = "brendars91"
    repo: str = "Gem-Trinity-Genesis"
    branch: str = "main"

class GitHubSyncService:
    def __init__(self, config: Optional[GitHubConfig] = None):
        # Detectar entorno
        self.is_production = os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("VERCEL_ENV")
        
        # Configuración de GitHub - hardcoded token for local development
        default_token = os.environ.get("GITHUB_TOKEN", "<REDACTED_GITHUB_TOKEN>")
        
        if config:
            self.config = config
        else:
            self.config = GitHubConfig(
                token=default_token,
                owner=os.environ.get("GITHUB_OWNER", "brendars91"),
                repo=os.environ.get("GITHUB_REPO", "Gem-Trinity-Genesis"),
                branch=os.environ.get("GITHUB_BRANCH", "main")
            )
        
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Cache local
        self.cache_dir = Path("cache/github")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, any] = {}
    
    def is_configured(self) -> bool:
        """Check if GitHub token is configured"""
        return bool(self.config.token)
    
    async def test_connection(self) -> Dict:
        """Test GitHub API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/user",
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "connected",
                        "user": data.get("login"),
                        "repos": data.get("public_repos", 0) + data.get("total_private_repos", 0)
                    }
                else:
                    return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_file_content(self, path: str) -> Optional[str]:
        """Get file content from GitHub repository"""
        # Check cache first
        cache_key = f"{self.config.repo}/{path}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_base}/repos/{self.config.owner}/{self.config.repo}/contents/{path}"
                response = await client.get(
                    url,
                    headers=self.headers,
                    params={"ref": self.config.branch},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("encoding") == "base64":
                        content = base64.b64decode(data["content"]).decode("utf-8")
                        self._cache[cache_key] = content
                        return content
                return None
        except Exception as e:
            print(f"Error fetching {path}: {e}")
            return None
    
    async def get_directory_contents(self, path: str) -> List[Dict]:
        """Get directory listing from GitHub repository"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_base}/repos/{self.config.owner}/{self.config.repo}/contents/{path}"
                response = await client.get(
                    url,
                    headers=self.headers,
                    params={"ref": self.config.branch},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    items = response.json()
                    return [
                        {
                            "name": item["name"],
                            "path": item["path"],
                            "type": item["type"],  # "file" or "dir"
                            "size": item.get("size", 0)
                        }
                        for item in items
                    ]
                return []
        except Exception as e:
            print(f"Error listing {path}: {e}")
            return []
    
    async def get_agent_folders(self) -> Dict[str, List[Dict]]:
        """Get all agent folders from the repository structure"""
        agents = {
            "gem-architect": [],
            "gem-builder": [],
            "engine": []
        }
        
        for agent_name in agents.keys():
            # Try to get skills folder for each agent
            skills_path = f"modules/{agent_name}/.agent/skills" if agent_name != "gem-architect" else f"modules/{agent_name}/skills"
            contents = await self.get_directory_contents(skills_path)
            agents[agent_name] = contents
        
        return agents
    
    async def sync_skill(self, skill_path: str, local_dest: Path) -> bool:
        """Sync a skill from GitHub to local cache"""
        try:
            # Get skill directory contents
            contents = await self.get_directory_contents(skill_path)
            
            local_dest.mkdir(parents=True, exist_ok=True)
            
            for item in contents:
                if item["type"] == "file":
                    content = await self.get_file_content(item["path"])
                    if content:
                        (local_dest / item["name"]).write_text(content)
                elif item["type"] == "dir":
                    # Recursively sync subdirectories
                    await self.sync_skill(item["path"], local_dest / item["name"])
            
            return True
        except Exception as e:
            print(f"Error syncing skill {skill_path}: {e}")
            return False
    
    async def sync_all_resources(self) -> Dict:
        """Sync all resources from GitHub to local cache"""
        results = {
            "synced": [],
            "failed": [],
            "source": "github" if self.is_production else "local"
        }
        
        if not self.is_production:
            # Use local files directly
            results["message"] = "Using local files (development mode)"
            return results
        
        if not self.is_configured():
            results["message"] = "GitHub token not configured"
            results["source"] = "local_fallback"
            return results
        
        # Sync resources/skills
        skills_contents = await self.get_directory_contents("resources/skills")
        for skill in skills_contents:
            if skill["type"] == "dir":
                dest = self.cache_dir / "skills" / skill["name"]
                success = await self.sync_skill(skill["path"], dest)
                if success:
                    results["synced"].append(skill["name"])
                else:
                    results["failed"].append(skill["name"])
        
        return results
    
    def get_local_or_cached_skill(self, skill_id: str) -> Optional[Path]:
        """Get skill path, preferring cache in production"""
        # Check local resources first
        local_path = Path("resources/skills") / skill_id
        if local_path.exists():
            return local_path
        
        # Check cache
        cached_path = self.cache_dir / "skills" / skill_id
        if cached_path.exists():
            return cached_path
        
        return None


# Singleton instance
github_sync = GitHubSyncService()


# Synchronous wrappers for use in non-async code
def test_github_connection() -> Dict:
    """Test GitHub connection (sync wrapper)"""
    return asyncio.run(github_sync.test_connection())

def sync_resources_from_github() -> Dict:
    """Sync all resources from GitHub (sync wrapper)"""
    return asyncio.run(github_sync.sync_all_resources())

def get_resource_from_github(path: str) -> Optional[str]:
    """Get single resource from GitHub (sync wrapper)"""
    return asyncio.run(github_sync.get_file_content(path))
