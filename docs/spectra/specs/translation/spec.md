# translation Specification

## Purpose

把 LeekDuck 的英文活動名稱、田野調查任務與獎勵寶可夢翻成繁體中文。只用字典與規則，不使用 AI。對應 `scraper/translate.py` 與 `scraper/data/pokemon_names.json`。

## Requirements

### Requirement: Dictionary only

翻譯 SHALL 只使用本機字典與正規表示式規則，不呼叫任何 AI 或外部翻譯服務；對不到的專有名詞 SHALL 保留英文原文。

#### Scenario: Unknown proper noun

- **WHEN** 活動名稱含字典裡沒有的英文專有名詞
- **THEN** 該詞 SHALL 原樣保留

### Requirement: Event name translation

`event_name` SHALL 依序：把寶可夢英文名（`pokemon_names.json`，長名稱優先、前後不能接英文字母）換成中文名，翻月份與流星雨名稱，再依 `PATTERNS` 順序套用整句結構（如「X Spotlight Hour」→「聚焦時刻：X」、「X Community Day」→「X社群日」）與零散字詞（Mega/Shadow/Dynamax/Gigantamax 只在後面接中文名時才翻），最後去掉中文字與 X/Y 之間的空白。

#### Scenario: Spotlight hour

- **WHEN** 名稱為「Pikachu Spotlight Hour」
- **THEN** 結果 SHALL 為「聚焦時刻：皮卡丘」

#### Scenario: Mega before a non-Pokémon word

- **WHEN** 名稱含「Mega Edition」
- **THEN** 「Mega」SHALL 不被翻成「超級」

### Requirement: Research task translation

`research_task` SHALL 依 `_RESEARCH` 規則把常見田野調查句型（捕捉、投球、團體戰、孵蛋、轉動補給站、拍照、進化、強化、夥伴、禮物、交換、火箭隊、對戰聯盟、莓果、放生）翻成中文；「a / an」數量 SHALL 視為 1；都對不到時 SHALL 改用 `event_name`。

#### Scenario: Typed catch

- **WHEN** 任務為「Catch 3 Fire-type Pokémon」
- **THEN** 結果 SHALL 為「捕捉 3 隻火屬性寶可夢」

### Requirement: Reward Pokémon translation

`pokemon` SHALL 把地區形態與暗影/超級前綴（Alolan、Galarian、Hisuian、Paldean、Shadow、Mega）翻成中文前綴，基本名稱查字典，保留後面的編號（例如「Spinda 4」→「晃晃斑 4」）；查不到時 SHALL 改用 `event_name`。

#### Scenario: Regional form

- **WHEN** 獎勵為「Alolan Geodude」
- **THEN** 結果 SHALL 為「阿羅拉小拳石」
