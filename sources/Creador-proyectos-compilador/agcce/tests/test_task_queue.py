"""
Tests para task_queue.py
"""
import pytest
from pathlib import Path
import sys
import shutil

# Añadir scripts al path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from task_queue import TaskQueue, QUEUE_BASE


class TestTaskQueue:
    """Tests para TaskQueue."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup y cleanup para cada test."""
        # Limpiar cola antes de cada test
        TaskQueue._ensure_dirs()
        yield
        # No limpiar después para inspección manual si es necesario
    
    def test_add_task(self):
        """Debe crear tarea con ID válido."""
        task_id = TaskQueue.add("Test task", {"test": True})
        
        assert task_id.startswith("TASK-")
        assert len(task_id) == 13  # TASK- + 8 chars
    
    def test_get_next_moves_to_in_progress(self):
        """Debe mover tarea a in_progress al obtenerla."""
        task_id = TaskQueue.add("Test task for get_next")
        
        task = TaskQueue.get_next()
        
        assert task is not None
        assert task["status"] == "in_progress"
        assert "started_at" in task
    
    def test_complete_task(self):
        """Debe marcar tarea como completada."""
        task_id = TaskQueue.add("Test task to complete")
        task = TaskQueue.get_next()
        
        success = TaskQueue.complete(task["id"], {"result": "ok"})
        
        assert success == True
    
    def test_fail_task(self):
        """Debe marcar tarea como fallida."""
        task_id = TaskQueue.add("Test task to fail")
        task = TaskQueue.get_next()
        
        success = TaskQueue.fail(task["id"], "Test error")
        
        assert success == True
    
    def test_retry_failed_task(self):
        """Debe reintentar tarea fallida."""
        task_id = TaskQueue.add("Test task to retry")
        task = TaskQueue.get_next()
        TaskQueue.fail(task["id"], "Temporary error")
        
        success = TaskQueue.retry(task["id"])
        
        assert success == True
    
    def test_get_stats(self):
        """Debe retornar estadísticas válidas."""
        stats = TaskQueue.get_stats()
        
        assert "pending" in stats
        assert "in_progress" in stats
        assert "completed" in stats
        assert "failed" in stats
        
        # Todos deben ser números
        assert isinstance(stats["pending"], int)
    
    def test_list_all(self):
        """Debe listar todas las tareas."""
        TaskQueue.add("Task 1")
        TaskQueue.add("Task 2")
        
        tasks = TaskQueue.list_all()
        
        assert isinstance(tasks, list)
        assert len(tasks) >= 2
    
    def test_list_filtered_by_status(self):
        """Debe filtrar por status."""
        TaskQueue.add("Pending task")
        
        pending = TaskQueue.list_all("pending")
        
        assert all(t["status"] == "pending" for t in pending)
    
    def test_priority_ordering(self):
        """Debe retornar tareas en orden de prioridad."""
        TaskQueue.add("Low priority", priority=10)
        TaskQueue.add("High priority", priority=1)
        
        task = TaskQueue.get_next()
        
        # La de mayor prioridad (menor número) debe venir primero
        assert task["priority"] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
