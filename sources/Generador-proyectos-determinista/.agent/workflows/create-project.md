---
description: Create a new project and register it in the Dashboard
---

1. Ask the user for the Project Name and optional Location.
2. If no location is provided, default to creating it inside `Agente Copilot Engine`.
3. Run the project creator script:
   ```powershell
   python scripts/project_creator.py "PROJECT_NAME" --path "OPTIONAL_PATH"
   ```
4. Confirm to the user that the project has been created and is visible in the Dashboard.
