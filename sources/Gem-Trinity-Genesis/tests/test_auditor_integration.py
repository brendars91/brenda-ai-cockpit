
import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from pathlib import Path

# Add local-watcher to path to import BuilderService
sys.path.append(os.path.join(os.getcwd(), 'local-watcher'))

from builder_service import BuilderService, BuildStatus

@pytest.fixture
def mock_builder():
    return BuilderService()

@patch('subprocess.run')
@patch('pathlib.Path.write_text')
@patch('pathlib.Path.read_text')
def test_auditor_invocation(mock_read, mock_write, mock_subprocess, mock_builder):
    """
    Verify that the Auditor Agent is invoked via subprocess 
    when an agent is compiled.
    """
    # Setup Mocks
    mock_read.return_value = "class Agent_{{AGENT_ID}}: pass" # Template content
    
    # Mock return of subprocess (Auditor execution)
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "Auditor finished successfully."
    mock_subprocess.return_value = mock_process

    # Create a dummy build item
    build_item = {
        "build_id": "test-build-123",
        "payload_id": "payload-123",
        "agent_name": "Test Agent",
        "model": "gemini-2.0-flash",
        "tools": [],
        "status": BuildStatus.PENDING,
        "progress": 0,
        "eta_seconds": 45,
        "created_at": 1234567890,
        "started_at": None,
        "completed_at": None
    }
    
    # Inject into queue to satisfy _process_build internals if needed, 
    # though we are calling _process_build directly or we need to mock lock
    
    # We will call _process_build directly. 
    # It requires the item to be in self.queue for status updates.
    with mock_builder.queue_lock:
        mock_builder.queue.append(build_item)

    # EXECUTE
    mock_builder._process_build(build_item)

    # VERIFY
    # Check if subprocess.run was called
    assert mock_subprocess.called
    
    # Check arguments passed to subprocess
    args, _ = mock_subprocess.call_args
    cmd_list = args[0]
    
    # Verify command structure
    assert cmd_list[0] == "python"
    assert "auditor_agent_v2.1.py" in str(cmd_list[1])
    assert "AUDIT_CRITICAL" in cmd_list[2] # The task description
    assert cmd_list[3] == "--workspace"
    
    print("\n✅ Verification Successful: Auditor was invoked with correct parameters.")
