#!/usr/bin/env bash

# Resolve symlinks to find the true directory of this script
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Try using uv first for isolated dependencies, fallback to system fastmcp
if command -v uv >/dev/null 2>&1; then
    exec uv run --with "mcp>=1.0.0" --with "google-cloud-dataplex>=1.7.0" --with "google-auth>=2.17.3" --with "requests>=2.28.2" mcp_server.py
else
    # Fallback assuming dependencies and fastmcp are installed in current Python env
    exec fastmcp run mcp_server.py
fi
