"""
Mirror Sync v2.0 - Delta Check Optimization
Bidirectional synchronization with hash-based delta checking.
"""
import sys
import time
import hashlib
import shutil
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Optional, Set
from collections import defaultdict
import threading

# Path mappings (internal -> external)
PATHS_MAP = {
    "modules/gem-architect": r"C:\Users\ASUS\.gemini\Creador-proyectos-compilador\gem-architect",
    "modules/gem-builder": r"C:\Users\ASUS\.gemini\Creador-proyectos-compilador\gem-builder",
    "modules/engine": r"C:\Users\ASUS\.gemini\Agente Copilot Engine",
    "resources/skills": r"C:\Users\ASUS\.gemini\Skills proyectos",
}

# Directories to ignore
IGNORE_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'logs', 'tmp',
    'artifacts', 'dist', '.next', '.pytest_cache', 'smart-coding-cache'
}

# File extensions to ignore
IGNORE_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dylib', '.dll', '.exe',
    '.log', '.tmp', '.cache', '.swp', '.swo'
}

# Maximum file size to sync (in bytes) - 100MB default
MAX_SYNC_SIZE = 100 * 1024 * 1024

class FileHashCache:
    """
    Cache for file hashes to avoid recomputing.

    Uses MD5 for fast comparison of file changes.
    """

    def __init__(self, cache_file: Optional[Path] = None):
        self.cache: Dict[str, Dict] = {}
        self.cache_file = cache_file or Path("artifacts/mirror_sync_cache.json")
        self.lock = threading.Lock()
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk if exists"""
        if self.cache_file.exists():
            try:
                self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[Mirror Sync] Cache load failed: {e}")
                self.cache = {}

    def _save_cache(self):
        """Save cache to disk"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[Mirror Sync] Cache save failed: {e}")

    def get_file_hash(self, file_path: Path) -> Optional[str]:
        """Get cached hash for file, or None if not cached"""
        path_str = str(file_path)
        with self.lock:
            if path_str in self.cache:
                entry = self.cache[path_str]
                # Check if file mtime matches cache
                if entry.get("mtime") == file_path.stat().st_mtime:
                    return entry.get("hash")
        return None

    def set_file_hash(self, file_path: Path, file_hash: str):
        """Set hash for file in cache"""
        path_str = str(file_path)
        with self.lock:
            self.cache[path_str] = {
                "hash": file_hash,
                "mtime": file_path.stat().st_mtime,
                "size": file_path.stat().st_size
            }
            # Periodically save cache
            if len(self.cache) % 100 == 0:
                self._save_cache()

    def remove_file(self, file_path: Path):
        """Remove file from cache"""
        path_str = str(file_path)
        with self.lock:
            self.cache.pop(path_str, None)

    def cleanup_missing_files(self, existing_paths: Set[Path]):
        """Remove cache entries for files that no longer exist"""
        with self.lock:
            existing_strs = {str(p) for p in existing_paths}
            self.cache = {
                k: v for k, v in self.cache.items()
                if k in existing_strs
            }

    @staticmethod
    def compute_hash(file_path: Path) -> Optional[str]:
        """
        Compute MD5 hash of file.

        Returns None if file cannot be read.
        """
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None

class SyncStatistics:
    """Track synchronization statistics"""

    def __init__(self):
        self.files_synced = 0
        self.files_skipped = 0
        self.bytes_synced = 0
        self.errors = 0
        self.start_time = time.time()

    def record_sync(self, file_size: int):
        """Record a successful sync"""
        self.files_synced += 1
        self.bytes_synced += file_size

    def record_skip(self):
        """Record a skipped file (no change)"""
        self.files_skipped += 1

    def record_error(self):
        """Record an error"""
        self.errors += 1

    def get_report(self) -> Dict:
        """Get statistics report"""
        elapsed = time.time() - self.start_time
        return {
            "files_synced": self.files_synced,
            "files_skipped": self.files_skipped,
            "errors": self.errors,
            "bytes_synced": self.bytes_synced,
            "bytes_synced_mb": round(self.bytes_synced / (1024 * 1024), 2),
            "elapsed_seconds": round(elapsed, 1),
            "sync_rate_mb_per_sec": round((self.bytes_synced / (1024 * 1024)) / elapsed, 2) if elapsed > 0 else 0
        }

class OptimizedMirrorHandler(FileSystemEventHandler):
    """
    Optimized mirror handler with delta checking.

    Features:
    - Hash-based delta detection
    - File hash caching
    - Size limits
    - Debouncing
    - Statistics tracking
    """

    def __init__(self, source_root: Path, target_root: Path, name: str,
                 hash_cache: FileHashCache, stats: SyncStatistics):
        self.source_root = source_root.resolve()
        self.target_root = target_root.resolve()
        self.name = name
        self.hash_cache = hash_cache
        self.stats = stats

        # Debouncing: track recent syncs
        self.recent_syncs: Dict[str, float] = {}
        self.debounce_interval = 2.0  # seconds

        # Pending sync queue (debounce)
        self.pending_syncs: Set[str] = set()
        self.pending_lock = threading.Lock()

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored"""
        # Check directory ignore list
        if any(part in IGNORE_DIRS for part in path.parts):
            return True

        # Check file extension
        if path.suffix.lower() in IGNORE_EXTENSIONS:
            return True

        return False

    def _needs_sync(self, src_path: Path, dest_path: Path) -> bool:
        """
        Check if file needs synchronization using delta checking.

        Returns True if:
        - Destination doesn't exist
        - Source file size differs from destination
        - Source file hash differs from destination
        - Source hash differs from cache
        """
        if not dest_path.exists():
            return True

        # Quick size check
        src_stat = src_path.stat()
        dest_stat = dest_path.stat()

        if src_stat.st_size != dest_stat.st_size:
            return True

        # Hash check
        cached_hash = self.hash_cache.get_file_hash(src_path)

        if cached_hash:
            # Check if destination hash matches cache
            dest_hash = self.hash_cache.get_file_hash(dest_path)
            if dest_hash == cached_hash:
                return False

        # Compute source hash if not cached
        if not cached_hash:
            src_hash = FileHashCache.compute_hash(src_path)
            if src_hash:
                self.hash_cache.set_file_hash(src_path, src_hash)
                cached_hash = src_hash

        # Compute destination hash for comparison
        dest_hash = FileHashCache.compute_hash(dest_path)
        if dest_hash and cached_hash == dest_hash:
            return False

        return True

    def _sync_file(self, src_path: Path, dest_path: Path, rel_path: Path):
        """Synchronize a single file"""
        try:
            src_stat = src_path.stat()

            # Check file size limit
            if src_stat.st_size > MAX_SYNC_SIZE:
                print(f"[{self.name}] ⚠️ Skipped (too large): {rel_path} ({src_stat.st_size / (1024*1024):.1f} MB)")
                self.stats.record_skip()
                return

            # Check if sync needed
            if not self._needs_sync(src_path, dest_path):
                self.stats.record_skip()
                return

            # Ensure parent directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file with metadata preservation
            shutil.copy2(src_path, dest_path)

            # Update hash cache
            file_hash = FileHashCache.compute_hash(src_path)
            if file_hash:
                self.hash_cache.set_file_hash(src_path, file_hash)
                self.hash_cache.set_file_hash(dest_path, file_hash)

            self.stats.record_sync(src_stat.st_size)

            if src_stat.st_size > 1024 * 100:  # Log files > 100KB
                size_mb = src_stat.st_size / (1024 * 1024)
                print(f"[{self.name}] ✅ Synced: {rel_path} ({size_mb:.2f} MB)")

        except Exception as e:
            print(f"[{self.name}] ❌ Error syncing {rel_path}: {e}")
            self.stats.record_error()

    def _sync_directory(self, src_path: Path, dest_path: Path, rel_path: Path):
        """Synchronize a directory (create if missing)"""
        try:
            dest_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[{self.name}] ❌ Error creating directory {rel_path}: {e}")

    def _sync(self, src_path: Path):
        """Main sync logic with debouncing"""
        try:
            rel_path = src_path.relative_to(self.source_root)

            # Check ignore list
            if self._should_ignore(rel_path):
                return

            dest_path = self.target_root / rel_path

            # Debounce check
            now = time.time()
            path_str = str(src_path)

            if path_str in self.recent_syncs:
                if now - self.recent_syncs[path_str] < self.debounce_interval:
                    return

            self.recent_syncs[path_str] = now

            # Clean old entries from recent_syncs
            if len(self.recent_syncs) > 1000:
                cutoff = now - 60  # Remove entries older than 1 minute
                self.recent_syncs = {
                    k: v for k, v in self.recent_syncs.items()
                    if v > cutoff
                }

            # Perform sync
            if src_path.is_dir():
                self._sync_directory(src_path, dest_path, rel_path)
            elif src_path.is_file():
                self._sync_file(src_path, dest_path, rel_path)

        except ValueError:
            # Path not relative to source (shouldn't happen)
            pass
        except Exception as e:
            # Ignore errors for ephemeral files
            pass

    def on_created(self, event):
        """Handle file/directory creation"""
        if not event.is_directory:
            self._sync(Path(event.src_path))

    def on_modified(self, event):
        """Handle file modification"""
        if not event.is_directory:
            self._sync(Path(event.src_path))

    def on_moved(self, event):
        """Handle file/directory move"""
        self._sync(Path(event.dest_path))

    def on_deleted(self, event):
        """Handle file/directory deletion"""
        try:
            rel_path = Path(event.src_path).relative_to(self.source_root)
            dest_path = self.target_root / rel_path

            if dest_path.exists():
                dest_path.unlink()
                self.hash_cache.remove_file(dest_path)
                print(f"[{self.name}] 🗑️ Deleted: {rel_path}")
        except Exception:
            pass

class MirrorSyncEngine:
    """
    Main mirror sync engine with statistics and monitoring.

    Features:
    - Bidirectional synchronization
    - Hash-based delta checking
    - Statistics tracking
    - Automatic cache cleanup
    """

    def __init__(self):
        self.hash_cache = FileHashCache()
        self.stats = SyncStatistics()
        self.observer = None
        self.handlers = []

    def start(self):
        """Start the mirror sync engine"""
        print("--- Gem Trinity: Mirror Engine v2.0 Started ---")
        print(f"    Delta checking: ENABLED")
        print(f"    Max file size: {MAX_SYNC_SIZE / (1024*1024):.0f} MB")
        print(f"    Debounce: {OptimizedMirrorHandler.debounce_interval}s")
        print("")

        self.observer = Observer()
        base_dir = Path.cwd()

        for internal_rel, external_abs in PATHS_MAP.items():
            internal_path = base_dir / internal_rel
            external_path = Path(external_abs)

            if not internal_path.exists():
                print(f"[WARN] Skipping {internal_rel} - Internal path missing")
                continue

            if not external_path.exists():
                print(f"[WARN] Skipping {internal_rel} - External path missing")
                continue

            # Monitor Internal -> External
            handler_out = OptimizedMirrorHandler(
                internal_path, external_path,
                f"OUT:{internal_rel}",
                self.hash_cache, self.stats
            )
            self.observer.schedule(handler_out, str(internal_path), recursive=True)
            self.handlers.append(handler_out)
            print(f"[WATCH] Monitoring Internal: {internal_rel}")

            # Monitor External -> Internal
            handler_in = OptimizedMirrorHandler(
                external_path, internal_path,
                f"IN:{external_path.name}",
                self.hash_cache, self.stats
            )
            self.observer.schedule(handler_in, str(external_path), recursive=True)
            self.handlers.append(handler_in)
            print(f"[WATCH] Monitoring External: {external_path}")

        print("")
        print("[INFO] Mirror sync monitoring started. Press Ctrl+C to stop.")
        print("")

        self.observer.start()

        # Statistics printer (every 60 seconds)
        try:
            while True:
                time.sleep(60)
                report = self.stats.get_report()
                print(f"[Mirror Sync Stats] "
                      f"Synced: {report['files_synced']} | "
                      f"Skipped: {report['files_skipped']} | "
                      f"Errors: {report['errors']} | "
                      f"Transferred: {report['bytes_synced_mb']} MB")
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the mirror sync engine"""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        # Save hash cache
        self.hash_cache._save_cache()

        # Print final statistics
        report = self.stats.get_report()
        print("")
        print("--- Mirror Sync Final Statistics ---")
        print(f"Files synced: {report['files_synced']}")
        print(f"Files skipped: {report['files_skipped']}")
        print(f"Errors: {report['errors']}")
        print(f"Total transferred: {report['bytes_synced_mb']} MB")
        print(f"Elapsed time: {report['elapsed_seconds']}s")
        print(f"Average rate: {report['sync_rate_mb_per_sec']} MB/s")
        print("---")

def start_mirroring():
    """Start the mirror sync engine (entry point)"""
    engine = MirrorSyncEngine()
    engine.start()

if __name__ == "__main__":
    start_mirroring()
