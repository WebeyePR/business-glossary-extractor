import subprocess
import os
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("GCP KC Glossary Builder")

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

@mcp.tool()
def import_glossary(project_id: str, project_num: str, glossary_id: str, json_file: str, location: str = "us") -> str:
    """
    Import an extracted Glossary JSON into Google Cloud Dataplex.
    Safely handles Long-Running Operations (LROs).
    """
    script_path = os.path.join(SCRIPTS_DIR, "import_glossary.py")
    cmd = [
        "python", script_path,
        "--project_id", project_id,
        "--project_num", project_num,
        "--location", location,
        "--glossary_id", glossary_id,
        "--json_file", json_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

@mcp.tool()
def bind_aspects(project_id: str, project_num: str, glossary_id: str, json_file: str, dataset: str, location: str = "us") -> str:
    """
    Deep bind Aspects and Definition Links for Glossary Terms to physical BigQuery columns.
    Attaches 'has_calculation' and 'has_physical_mapping' Dataplex Aspects.
    """
    script_path = os.path.join(SCRIPTS_DIR, "bind_aspects.py")
    cmd = [
        "python", script_path,
        "--project_id", project_id,
        "--project_num", project_num,
        "--location", location,
        "--glossary_id", glossary_id,
        "--json_file", json_file,
        "--dataset", dataset
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

@mcp.tool()
def delete_glossary(project_id: str, project_num: str, glossary_id: str, location: str = "us") -> str:
    """
    Delete a Dataplex Glossary and all its terms.
    Useful for clean-slate recreations and resolving cascading dependency errors.
    """
    script_path = os.path.join(SCRIPTS_DIR, "delete_glossary.py")
    cmd = [
        "python", script_path,
        "--project_id", project_id,
        "--project_num", project_num,
        "--location", location,
        "--glossary_id", glossary_id
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
