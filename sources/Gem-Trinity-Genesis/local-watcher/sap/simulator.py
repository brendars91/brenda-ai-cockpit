"""
SAP Simulator Module
Simulates SAP FI/CO/ABAP operations without real SAP connection.
Supports switching to production mode when SAP credentials are available.
"""
import time
import random
from typing import Dict, List
from datetime import datetime, timedelta

class SAPSimulator:
    def __init__(self, mode: str = "demo"):
        self.mode = mode  # "demo" or "production"
        self.mock_data = SAPMockData()
        
    def execute_transaction(self, transaction: str, params: Dict) -> Dict:
        """Execute SAP transaction (simulated)"""
        if self.mode == "production":
            return self._execute_production(transaction, params)
        else:
            return self._execute_demo(transaction, params)
    
    def _execute_demo(self, transaction: str, params: Dict) -> Dict:
        """Execute in demo mode with mock data"""
        # Simulate latency
        time.sleep(random.uniform(0.05, 0.2))
        
        if transaction == "FB50":
            return self._simulate_fb50(params)
        elif transaction == "F-53":
            return self._simulate_f53(params)
        elif transaction == "F110":
            return self._simulate_f110(params)
        elif transaction == "F.13":
            return self._simulate_f13(params)
        elif transaction.startswith("Z_"):
            return self._simulate_abap_custom(transaction, params)
        else:
            return {"status": "error", "message": f"Transaction {transaction} not simulated"}
    
    def _execute_production(self, transaction: str, params: Dict) -> Dict:
        """Execute in production mode (requires real SAP connection)"""
        # In production, this would use pyrfc library
        # from pyrfc import Connection
        # conn = Connection(ashost=SAP_HOST, user=SAP_USER, ...)
        # result = conn.call('RFC_FUNCTION', params)
        raise NotImplementedError("Production mode requires SAP connection (pyrfc)")
    
    def _simulate_fb50(self, params: Dict) -> Dict:
        """Simulate FB50 - Post General Ledger Entry"""
        doc_number = f"5000{random.randint(100000, 999999)}"
        return {
            "status": "success",
            "transaction": "FB50",
            "document_number": doc_number,
            "fiscal_year": datetime.now().year,
            "company_code": "1000",
            "posting_date": datetime.now().strftime("%Y-%m-%d"),
            "amount": params.get("amount","0.00"),
            "currency": params.get("currency", "EUR"),
            "gl_account": params.get("gl_account", "400000"),
            "message": f"Document {doc_number} posted successfully"
        }
    
    def _simulate_f53(self, params: Dict) -> Dict:
        """Simulate F-53 - Customer Payment Posting"""
        clearing_doc = f"1900{random.randint(100000, 999999)}"
        return {
            "status": "success",
            "transaction": "F-53",
            "clearing_document": clearing_doc,
            "customer": params.get("customer", "10001"),
            "amount": params.get("amount", "0.00"),
            "currency": params.get("currency", "EUR"),
            "cleared_items": params.get("items", []),
            "message": f"Payment cleared with document {clearing_doc}"
        }
    
    def _simulate_f110(self, params: Dict) -> Dict:
        """Simulate F110 - Automatic Payment Run"""
        run_id = f"PAYRUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return {
            "status": "success",
            "transaction": "F110",
            "run_id": run_id,
            "payment_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "vendors_processed": random.randint(15, 45),
            "total_amount": f"{random.uniform(50000, 500000):.2f}",
            "currency": "EUR",
            "payment_method": params.get("payment_method", "T"),
            "message": f"Payment run {run_id} executed successfully"
        }
    
    def _simulate_f13(self, params: Dict) -> Dict:
        """Simulate F.13 - Bank Reconciliation"""
        return {
            "status": "success",
            "transaction": "F.13",
            "bank_account": params.get("bank_account", "1100"),
            "statement_balance": f"{random.uniform(100000, 1000000):.2f}",
            "sap_balance": f"{random.uniform(100000, 1000000):.2f}",
            "difference": f"{random.uniform(-5000, 5000):.2f}",
            "reconciled_items": random.randint(8, 25),
            "outstanding_items": random.randint(0, 5),
            "message": "Bank reconciliation completed"
        }
    
    def _simulate_abap_custom(self, program: str, params: Dict) -> Dict:
        """Simulate custom ABAP program execution"""
        return {
            "status": "success",
            "program": program,
            "execution_time": f"{random.uniform(0.5, 3.5):.2f}s",
            "records_processed": random.randint(100, 5000),
            "output": f"Custom ABAP program {program} executed successfully",
            "sy_subrc": 0,
            "message": "ABAP execution complete"
        }
    
    def query_table(self, table: str, fields: List[str] = None, where: str = "") -> List[Dict]:
        """Query SAP table (simulated)"""
        if self.mode == "production":
            raise NotImplementedError("Production mode requires SAP connection")
        
        if table == "BSEG":
            return self.mock_data.get_bseg_data()[:10]
        elif table == "BKPF":
            return self.mock_data.get_bkpf_data()[:10]
        elif table == "SKA1":
            return self.mock_data.get_ska1_data()[:10]
        elif table == "BSIS":
            return self.mock_data.get_bsis_data()[:10]
        else:
            return []


class SAPMockData:
    """Mock SAP table data"""
    
    def get_bseg_data(self) -> List[Dict]:
        """BSEG - Accounting Document Segment"""
        return [
            {
                "BUKRS": "1000",
                "BELNR": f"5000{random.randint(100000, 999999)}",
                "GJAHR": str(datetime.now().year),
                "BUZEI": "001",
                "HKONT": "400000",
                "DMBTR": f"{random.uniform(1000, 50000):.2f}",
                "WAERS": "EUR"
            } for _ in range(20)
        ]
    
    def get_bkpf_data(self) -> List[Dict]:
        """BKPF - Accounting Document Header"""
        return [
            {
                "BUKRS": "1000",
                "BELNR": f"5000{random.randint(100000, 999999)}",
                "GJAHR": str(datetime.now().year),
                "BLART": "SA",
                "BLDAT": datetime.now().strftime("%Y-%m-%d"),
                "BUDAT": datetime.now().strftime("%Y-%m-%d"),
                "USNAM": "TESTUSER"
            } for _ in range(20)
        ]
    
    def get_ska1_data(self) -> List[Dict]:
        """SKA1 - G/L Account Master"""
        return [
            {"KTOPL": "INT", "SAKNR": "100000", "XBILK": "X", "KTOKS": "SAK1"},
            {"KTOPL": "INT", "SAKNR": "400000", "XBILK": "X", "KTOKS": "SAK2"},
            {"KTOPL": "INT", "SAKNR": "500000", "XBILK": "X", "KTOKS": "SAK3"}
        ]
    
    def get_bsis_data(self) -> List[Dict]:
        """BSIS - Open Items (GL Accounts)"""
        return [
            {
                "BUKRS": "1000",
                "HKONT": "400000",
                "AUGDT": "",
                "DMBTR": f"{random.uniform(1000, 20000):.2f}",
                "WAERS": "EUR"
            } for _ in range(15)
        ]


# Pre-loaded SAP use cases
SAP_USE_CASES = {
    "monthly_close": {
        "name": "Monthly Financial Close Automation",
        "description": "Automates AR/AP validation, IFRS reclassifications, bank reconciliation, and FX adjustments",
        "transactions": ["FB50", "F-53", "F110", "F.13"],
        "custom_programs": ["Z_MONTHLY_CLOSE", "Z_FX_ADJUSTMENT"],
        "tables": ["BSEG", "BKPF", "SKA1", "BSIS"]
    },
    "ar_ap_validation": {
        "name": "AR/AP Validation and Reconciliation",
        "description": "Validates accounts receivable and payable against source documents",
        "transactions": ["F-53", "F-44"],
        "tables": ["BSEG", "BKPF", "KNA1", "LFA1"]
    },
    "bank_reconciliation": {
        "name": "Automated Bank Reconciliation",
        "description": "Reconciles bank statements with SAP postings",
        "transactions": ["F.13", "FF67"],
        "tables": ["T012", "FEBKO", "BSEG"]
    },
    "abap_report_execution": {
        "name": "Custom ABAP Report Execution",
        "description": "Execute custom ABAP reports for financial analysis",
        "custom_programs": ["Z_FI_ANALYSIS", "Z_GL_REPORT", "Z_VENDOR_AGING"],
        "tables": ["BSEG", "BKPF"]
    }
}
