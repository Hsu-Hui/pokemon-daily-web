#!/usr/bin/env bash
# 把 gas/ 上傳到 Apps Script，並更新「看板」和「接收資料」兩個部署（網址不變）。
# 兩個部署的執行身分不同，而網頁應用程式的設定來自每個版本的 appsscript.json，
# 所以各自改好 webapp 設定、上傳、建立新版本再更新部署。
# 找不到該說明的部署時會新建一個，網址印在執行記錄。
set -euo pipefail

MANIFEST=gas/appsscript.json
CLASP=${CLASP:-clasp}

set_webapp() {
  python3 - "$MANIFEST" "$1" "$2" <<'PY'
import json, sys
path, execute_as, access = sys.argv[1:]
manifest = json.load(open(path, encoding="utf-8"))
manifest["webapp"] = {"executeAs": execute_as, "access": access}
json.dump(manifest, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
}

deploy() {
  local description=$1 execute_as=$2 access=$3 id
  set_webapp "$execute_as" "$access"
  $CLASP push --force
  id=$($CLASP deployments | awk -v d="$description" '$3 ~ /^@[0-9]+$/ && $4 == "-" && $5 == d { print $2; exit }')
  if [ -n "$id" ]; then
    $CLASP deploy --deploymentId "$id" --description "$description"
  else
    id=$($CLASP deploy --description "$description" | awk '/^- / { print $2 }' | tail -1)
    echo "新建立「$description」部署"
  fi
  echo "「$description」網址：https://script.google.com/macros/s/$id/exec"
  [ -z "${GITHUB_STEP_SUMMARY:-}" ] || echo "- $description：https://script.google.com/macros/s/$id/exec" >> "$GITHUB_STEP_SUMMARY"
}

deploy "接收資料" USER_DEPLOYING ANYONE_ANONYMOUS
deploy "看板" USER_ACCESSING MYSELF
