# gas-deployment Specification

## Purpose

`gas/` 有改動並合併到 main 時，用 clasp 自動上傳 Apps Script 並更新「看板」與「接收資料」兩個部署，網址不變。對應 `.github/workflows/deploy-gas.yml`、`scripts/deploy_gas.sh` 與 `gas/appsscript.json`。

## Requirements

### Requirement: 部署觸發條件

部署 workflow SHALL 在 push 到 main 且改動 `gas/**`、`scripts/deploy_gas.sh` 或 `.github/workflows/deploy-gas.yml` 時執行，並支援手動觸發；同時只允許一個部署執行。

#### Scenario: 只改爬蟲

- **WHEN** 合併到 main 的改動只有 `scraper/`
- **THEN** 部署 workflow SHALL 不執行

### Requirement: 缺少部署憑證

缺少 `CLASPRC_JSON` 或 `GAS_SCRIPT_ID` secret 時，workflow SHALL 發出警告並略過部署步驟，不視為失敗。

#### Scenario: 沒有設定 secret

- **WHEN** repo 沒有設定這兩個 secret
- **THEN** workflow SHALL 顯示「還沒設定 CLASPRC_JSON / GAS_SCRIPT_ID，略過自動部署」並成功結束

### Requirement: 兩個部署

部署腳本 SHALL 用固定版本的 clasp（2.4.2）以 `gas` 為 rootDir 上傳，對每個部署先改寫 `appsscript.json` 的 `webapp` 設定再 `clasp push --force`，依說明找到既有部署就更新、找不到就新建並印出網址：

- 「接收資料」：`executeAs` 為 `USER_DEPLOYING`、`access` 為 `ANYONE_ANONYMOUS`
- 「看板」：`executeAs` 為 `USER_ACCESSING`、`access` 為 `MYSELF`

部署網址 SHALL 寫入 GitHub Actions 執行摘要。

#### Scenario: 已有部署

- **WHEN** 已有說明為「看板」的部署
- **THEN** 腳本 SHALL 更新該部署，網址不變

#### Scenario: 找不到部署

- **WHEN** 找不到說明為「接收資料」的部署
- **THEN** 腳本 SHALL 新建一個並印出「新建立「接收資料」部署」與網址

### Requirement: Apps Script 設定檔

`gas/appsscript.json` SHALL 使用 `Asia/Taipei` 時區、V8 runtime 與 Stackdriver 例外記錄。

#### Scenario: 時間相關的計算

- **WHEN** Apps Script 計算時間或觸發器
- **THEN** 時區 SHALL 為台灣時間
