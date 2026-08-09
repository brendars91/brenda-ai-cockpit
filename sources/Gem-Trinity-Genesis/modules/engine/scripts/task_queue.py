#!/usr/bin/env python3
"""
AGCCE Task Queue v1.0
Sistema de cola de tareas persistente.

Uso:
  from task_queue import TaskQueue
  TaskQueue.add("Mi tarea", {"plan_id": "PLAN-XXX"})
  task = TaskQueue.get_next()
  TaskQueue.complete(task["id"])
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Rutas de la cola
QUEUE_BASE = Path(__file__).parent.parent / "plans" / "queue"
PENDING_DIR = QUEUE_BASE / "pending"
IN_PROGRESS_DIR = QUEUE_BASE / "in_progress"
COMPLETED_DIR = QUEUE_BASE / "completed"
FAILED_DIR = QUEUE_BASE / "failed"


class TaskQueue:
    """Sistema de cola de tareas persistente."""
    
    @staticmethod
    def _ensure_dirs():
        """Asegura que las carpetas existan."""
        for dir_path in [PENDING_DIR, IN_PROGRESS_DIR, COMPLETED_DIR, FAILED_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _generate_id() -> str:
        """Genera ID único para tarea."""
        return f"TASK-{uuid.uuid4().hex[:8].upper()}"
    
    @classmethod
    def add(
        cls,
        description: str,
        metadata: Dict = None,
        priority: int = 5
    ) -> str:
        """
        Añade una tarea a la cola.
        
        Args:
            description: Descripción de la tarea
            metadata: Metadatos adicionales (plan_id, files, etc.)
            priority: Prioridad 1-10 (1=máxima)
        
        Returns:
            ID de la tarea creada
        """
        cls._ensure_dirs()
        
        task_id = cls._generate_id()
        task = {
            "id": task_id,
            "description": description,
            "metadata": metadata or {},
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        filepath = PENDING_DIR / f"{task_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        return task_id
    
    @classmethod
    def get_next(cls) -> Optional[Dict]:
        """
        Obtiene la siguiente tarea pendiente (por prioridad).
        La mueve a in_progress.
        """
        cls._ensure_dirs()
        
        pending_files = list(PENDING_DIR.glob("TASK-*.json"))
        if not pending_files:
            return None
        
        # Ordenar por prioridad
        tasks = []
        for filepath in pending_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                task = json.load(f)
                task["_filepath"] = filepath
                tasks.append(task)
        
        tasks.sort(key=lambda t: (t.get("priority", 5), t.get("created_at", "")))
        
        if not tasks:
            return None
        
        # Mover a in_progress
        task = tasks[0]
        old_path = task.pop("_filepath")
        new_path = IN_PROGRESS_DIR / old_path.name
        
        task["status"] = "in_progress"
        task["started_at"] = datetime.now().isoformat()
        task["updated_at"] = datetime.now().isoformat()
        
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        old_path.unlink()
        
        return task
    
    @classmethod
    def complete(cls, task_id: str, result: Dict = None) -> bool:
        """
        Marca una tarea como completada.
        
        Args:
            task_id: ID de la tarea
            result: Resultado de la ejecución
        
        Returns:
            True si se completó, False si no se encontró
        """
        cls._ensure_dirs()
        
        # Buscar en in_progress
        filepath = IN_PROGRESS_DIR / f"{task_id}.json"
        if not filepath.exists():
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            task = json.load(f)
        
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        task["updated_at"] = datetime.now().isoformat()
        task["result"] = result or {}
        
        new_path = COMPLETED_DIR / f"{task_id}.json"
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        filepath.unlink()
        return True
    
    @classmethod
    def fail(cls, task_id: str, error: str) -> bool:
        """
        Marca una tarea como fallida.
        
        Args:
            task_id: ID de la tarea
            error: Mensaje de error
        
        Returns:
            True si se marcó, False si no se encontró
        """
        cls._ensure_dirs()
        
        # Buscar en in_progress
        filepath = IN_PROGRESS_DIR / f"{task_id}.json"
        if not filepath.exists():
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            task = json.load(f)
        
        task["status"] = "failed"
        task["failed_at"] = datetime.now().isoformat()
        task["updated_at"] = datetime.now().isoformat()
        task["error"] = error
        
        new_path = FAILED_DIR / f"{task_id}.json"
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        filepath.unlink()
        return True
    
    @classmethod
    def retry(cls, task_id: str) -> bool:
        """
        Reintenta una tarea fallida (la mueve a pending).
        """
        cls._ensure_dirs()
        
        filepath = FAILED_DIR / f"{task_id}.json"
        if not filepath.exists():
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            task = json.load(f)
        
        task["status"] = "pending"
        task["updated_at"] = datetime.now().isoformat()
        task["retry_count"] = task.get("retry_count", 0) + 1
        
        # Limpiar campos de fallo
        task.pop("failed_at", None)
        task.pop("error", None)
        
        new_path = PENDING_DIR / f"{task_id}.json"
        with open(new_path, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
        
        filepath.unlink()
        return True
    
    @classmethod
    def list_all(cls, status: str = None) -> List[Dict]:
        """Lista tareas, opcionalmente filtradas por status."""
        cls._ensure_dirs()
        
        status_dirs = {
            "pending": PENDING_DIR,
            "in_progress": IN_PROGRESS_DIR,
            "completed": COMPLETED_DIR,
            "failed": FAILED_DIR
        }
        
        dirs_to_search = [status_dirs[status]] if status else status_dirs.values()
        
        tasks = []
        for dir_path in dirs_to_search:
            for filepath in dir_path.glob("TASK-*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    tasks.append(json.load(f))
        
        return tasks
    
    @classmethod
    def get_stats(cls) -> Dict:
        """Obtiene estadísticas de la cola."""
        cls._ensure_dirs()
        
        return {
            "pending": len(list(PENDING_DIR.glob("TASK-*.json"))),
            "in_progress": len(list(IN_PROGRESS_DIR.glob("TASK-*.json"))),
            "completed": len(list(COMPLETED_DIR.glob("TASK-*.json"))),
            "failed": len(list(FAILED_DIR.glob("TASK-*.json")))
        }


def main():
    """CLI para Task Queue."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python task_queue.py [add|next|complete|fail|list|stats]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Nueva tarea"
        task_id = TaskQueue.add(desc)
        print(f"Tarea creada: {task_id}")
    
    elif cmd == "next":
        task = TaskQueue.get_next()
        if task:
            print(f"Tarea: {task['id']}")
            print(f"Descripción: {task['description']}")
        else:
            print("No hay tareas pendientes")
    
    elif cmd == "complete":
        task_id = sys.argv[2] if len(sys.argv) > 2 else ""
        if TaskQueue.complete(task_id):
            print(f"Tarea {task_id} completada")
        else:
            print("Tarea no encontrada")
    
    elif cmd == "fail":
        task_id = sys.argv[2] if len(sys.argv) > 2 else ""
        error = sys.argv[3] if len(sys.argv) > 3 else "Error desconocido"
        if TaskQueue.fail(task_id, error):
            print(f"Tarea {task_id} marcada como fallida")
        else:
            print("Tarea no encontrada")
    
    elif cmd == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        tasks = TaskQueue.list_all(status)
        if tasks:
            for t in tasks:
                print(f"[{t['status']:12}] {t['id']} - {t['description'][:40]}")
        else:
            print("No hay tareas")
    
    elif cmd == "stats":
        stats = TaskQueue.get_stats()
        print(f"Pendientes:  {stats['pending']}")
        print(f"En progreso: {stats['in_progress']}")
        print(f"Completadas: {stats['completed']}")
        print(f"Fallidas:    {stats['failed']}")


if __name__ == '__main__':
    main()
