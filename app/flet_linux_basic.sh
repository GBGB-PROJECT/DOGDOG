#!/bin/bash
cd "$(dirname "$0")"

export PYTHONPATH=$(pwd)

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "❌ Error: .venv/bin/activate not found."
    exit 1
fi

echo "---------------------------------------------------"
echo "🚀 Flet Hot Reload Mode Starting..."
echo "[Web Mode] http://localhost:34636"
echo "[Exit] Ctrl + C"
echo "---------------------------------------------------"

if command -v xdg-open > /dev/null; then
    # 백그라운드(&)로 실행하여 터미널을 잡고 있지 않게 함
    xdg-open http://localhost:34636 > /dev/null 2>&1 &
else
    echo "⚠️  'xdg-open' not found. Please install 'xdg-utils' or open URL manually."
fi

export FLET_NO_BROWSER=1

watchfiles "python main.py"

echo ""
read -p "Press Enter to exit..."
