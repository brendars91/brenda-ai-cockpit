import threading
from typing import Optional

from config_manager import config
from sync_engine import SyncEngine
from mcp_grid import MCPGrid
from runner import Runner
from architect_service import ArchitectService
from builder_service import BuilderService
from engine_service import EngineService
from auditor_service import AuditorService
from sap.simulator import SAPSimulator
from sync_service import SyncService

from websocket_manager import get_websocket_manager
from state_store import get_state_store
from progress_tracker import get_progress_tracker
from semantic_cache import get_semantic_cache
from circuit_breaker import get_circuit_breaker
from metrics_collector import get_metrics_collector, get_system_collector, get_app_collector
from error_tracker import get_error_tracker


class ServiceState:
    mirror_active: bool = False
    mirror_thread: Optional[threading.Thread] = None
    sync_thread: Optional[threading.Thread] = None


sync_engine = SyncEngine()
mcp_grid = MCPGrid()
runner = Runner()
architect = ArchitectService()
builder = BuilderService()
engine = EngineService()
auditor = AuditorService()
sap_simulator = SAPSimulator(mode="demo")
resource_sync = SyncService()

ws_manager = get_websocket_manager()
state_store = get_state_store()
progress_tracker = get_progress_tracker()

semantic_cache = get_semantic_cache()
circuit_breaker_manager = get_circuit_breaker()

metrics_collector = get_metrics_collector()
system_collector = get_system_collector()
app_collector = get_app_collector()
error_tracker = get_error_tracker()

state = ServiceState()


def start_background_services() -> None:
    if state.sync_thread and state.sync_thread.is_alive():
        return

    def start_resource_sync() -> None:
        resource_sync.start()

    state.sync_thread = threading.Thread(target=start_resource_sync, daemon=True)
    state.sync_thread.start()
