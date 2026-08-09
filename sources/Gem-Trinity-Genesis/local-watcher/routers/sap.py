from fastapi import APIRouter

from api_models import SAPExecuteRequest
from sap.simulator import SAP_USE_CASES
from runtime import sap_simulator

router = APIRouter()


@router.post("/api/sap/execute")
async def sap_execute(req: SAPExecuteRequest):
    sap_simulator.mode = req.mode
    result = sap_simulator.execute_transaction(req.transaction, req.params)
    return result


@router.get("/api/sap/use_cases")
async def sap_get_use_cases():
    return {"use_cases": SAP_USE_CASES}


@router.get("/api/sap/table/{table_name}")
async def sap_query_table(table_name: str):
    data = sap_simulator.query_table(table_name)
    return {"table": table_name, "rows": data}
