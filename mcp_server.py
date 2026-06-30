import subprocess
import os
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("GCP KC Glossary Builder")

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

def _build_cmd(script_name, **kwargs):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = ["python", script_path]
    for k, v in kwargs.items():
        if v:
            cmd.extend([f"--{k}", str(v)])
    return cmd

@mcp.tool()
def import_glossary(json_file: str, project_id: str = "", project_num: str = "", glossary_id: str = "", location: str = "") -> str:
    """
    Import an extracted Glossary JSON into Google Cloud Dataplex.
    Safely handles Long-Running Operations (LROs).
    """
    cmd = _build_cmd("import_glossary.py", json_file=json_file, project_id=project_id, project_num=project_num, glossary_id=glossary_id, location=location)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

@mcp.tool()
def bind_aspects(json_file: str, dataset: str, project_id: str = "", project_num: str = "", glossary_id: str = "", location: str = "") -> str:
    """
    Deep bind Aspects and Definition Links for Glossary Terms to physical BigQuery columns.
    Attaches 'has_calculation' and 'has_physical_mapping' Dataplex Aspects.
    """
    cmd = _build_cmd("bind_aspects.py", json_file=json_file, dataset=dataset, project_id=project_id, project_num=project_num, glossary_id=glossary_id, location=location)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

@mcp.tool()
def delete_glossary(project_id: str = "", project_num: str = "", glossary_id: str = "", location: str = "") -> str:
    """
    Delete a Dataplex Glossary and all its terms.
    Useful for clean-slate recreations and resolving cascading dependency errors.
    """
    cmd = _build_cmd("delete_glossary.py", project_id=project_id, project_num=project_num, glossary_id=glossary_id, location=location)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
