#!/bin/bash

CPP_FILE_PATH=$1
WEB_PATH="https://compile.borworntat.com"

echo "Trying to compile $CPP_FILE_PATH using remote compile-checker service at $WEB_PATH"
curl -X POST -F "file=@{CPP_FILE_PATH}" ${WEB_PATH}/compile --output checker

echo "Compilation finished. Executable saved to 'checker'"
chmod +x checker