
import time
import shutil
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ResourceSyncHandler(FileSystemEventHandler):
    def __init__(self, source_dir: Path, target_dir: Path, name: str):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.name = name

    def on_modified(self, event):
        if event.is_directory:
            return
        self._sync()

    def on_created(self, event):
        if event.is_directory:
            return
        self._sync()

    def _sync(self):
        print(f"[{self.name}] Detected change... Syncing...")
        try:
            # Simple recursive copy for now (could be optimized)
            shutil.copytree(self.source_dir, self.target_dir, dirs_exist_ok=True)
            print(f"[{self.name}] Synced successfully!")
        except Exception as e:
            print(f"[{self.name}] Sync failed: {e}")

class SyncService:
    def __init__(self):
        self.watches = [
            {
                "name": "Skills",
                "source": Path.home() / ".gemini" / "Skills proyectos" / "vendor" / "anthropics-skills" / "skills",
                "target": Path("resources/skills")
            },
            {
                "name": "MCPs",
                "source": Path.home() / ".gemini" / "Reglas MCP Antigravity",
                "target": Path("resources/mcp_definitions")
            }
        ]
        self.observer = Observer()

    def start(self):
        print("--- Starting Resource Sync Service ---")
        active_watches = 0
        for watch in self.watches:
            try:
                if watch["source"].exists():
                    handler = ResourceSyncHandler(watch["source"], watch["target"], watch["name"])
                    self.observer.schedule(handler, str(watch["source"]), recursive=True)
                    print(f"[INFO] Watching {watch['name']} for updates...")
                    active_watches += 1
                else:
                    # Expected in Cloud/Railway
                    print(f"ℹ️ Sync Source skipped (Not found): {watch['source']}")
            except Exception as e:
                print(f"⚠️ Error initializing watch for {watch['name']}: {e}")
        
        if active_watches > 0:
            self.observer.start()
        else:
            print("ℹ️ No active watches. Sync Service idle (Cloud Mode).")

    def stop(self):
        self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    service = SyncService()
    service.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
