@echo off
echo Starting Lean-Explore MCP Server (Potion Problem Integration)...
echo.

:: Change to the lean-explore directory
cd /d "C:\Users\id374\mcp-tools\lean-explore"

:: Activate virtual environment and run server
echo Using local backend with potion_problem database...
".venv\Scripts\python.exe" -m lean_explore.mcp.server --backend local --log-level INFO

:: If server exits, pause to see any error messages
pause