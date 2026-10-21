"""把 shared/board.json 轉成 gas/Board.gs，讓 Apps Script 用同一份設定。

改了 shared/board.json 之後執行：python scripts/build_gas_config.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "shared" / "board.json"
TARGET = ROOT / "gas" / "Board.gs"


def render() -> str:
    board = json.loads(SOURCE.read_text(encoding="utf-8"))
    body = json.dumps(board, ensure_ascii=False, indent=2)
    return (
        "// 由 scripts/build_gas_config.py 從 shared/board.json 產生，不要直接改這個檔案。\n"
        f"const BOARD = {body};\n"
    )


if __name__ == "__main__":
    TARGET.write_text(render(), encoding="utf-8", newline="\n")
    print(f"已更新 {TARGET.relative_to(ROOT)}")
