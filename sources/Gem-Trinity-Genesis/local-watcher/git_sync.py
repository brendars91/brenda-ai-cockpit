
import subprocess
from pathlib import Path
from config_manager import config

class GitOps:
    def __init__(self):
        self.repo_root = config.base_dir
        
    def sync_to_cloud(self, message="Auto-sync Gem Trinity"):
        """
        Realiza add, commit y push del repositorio completo.
        Usado para respaldar el estado autónomo en la nube.
        """
        print(f"[GITOPS] Starting sync for {self.repo_root}")
        
        try:
            # 1. Add all
            subprocess.run(["git", "add", "."], cwd=self.repo_root, check=True)
            
            # 2. Commit
            # Allow empty commits? No.
            res = subprocess.run(
                ["git", "commit", "-m", message], 
                cwd=self.repo_root, 
                capture_output=True,
                text=True
            )
            
            if "nothing to commit" in res.stdout:
                print("[GITOPS] No changes to commit.")
                return {"status": "skipped", "reason": "no_changes"}
                
            # 3. Push
            subprocess.run(["git", "push"], cwd=self.repo_root, check=True)
            print("[GITOPS] Push successful.")
            return {"status": "success"}
            
        except subprocess.CalledProcessError as e:
            print(f"[GITOPS ERROR] Git command failed: {e}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    gitops = GitOps()
    gitops.sync_to_cloud()
