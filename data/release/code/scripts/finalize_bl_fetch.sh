#!/bin/bash
# BL 取得完了を待ち、統一表を再生成(コミットは人間/Code の確認後に手動 — 自動コミットはしない)
cd "$(dirname "$0")/.."
until grep -q "^done" data/raw/bl_fetch2.log; do sleep 60; done
python3 scripts/bl_log_stats.py > data/raw/bl_log_stats.log 2>&1
echo "FINALIZED $(date)" >> data/raw/bl_log_stats.log
