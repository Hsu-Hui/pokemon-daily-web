import importlib.util
import unittest
import unittest.mock
from datetime import datetime, timedelta
from pathlib import Path

from scraper import config, main, sources, translate

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"


NOW = datetime(2026, 10, 21, 1, tzinfo=config.TZ)


def news(title, source="A 報", nid=None):
    return sources.News(nid or title + source, title, "https://n/" + title, source, NOW)


class NewsTests(unittest.TestCase):
    def test_same_story_from_different_outlets_is_merged(self):
        items = [
            news("寶可夢中心台北推出萬聖節限定商品 皮卡丘南瓜造型登場", "A 報"),
            news("寶可夢中心台北萬聖節限定商品登場！皮卡丘南瓜造型", "B 報"),
            news("寶可夢快閃店進駐高雄 為期兩週", "C 報"),
        ]
        kept = sources.dedupe_news(items)
        self.assertEqual([k.source for k in kept], ["A 報", "C 報"])
        self.assertEqual(kept[0].others, ["B 報"])

    def test_dedupe_does_not_change_inputs(self):
        items = [news("寶可夢快閃店進駐高雄 為期兩週", "A 報"), news("寶可夢快閃店進駐高雄，為期兩週", "B 報")]
        kept = sources.dedupe_news(items)
        self.assertEqual(kept[0].others, ["B 報"])
        self.assertEqual([i.others for i in items], [[], []])

    def test_google_title_suffix_removed(self):
        self.assertEqual(sources._clean_title("皮卡丘來了 - 自由時報", "自由時報"), "皮卡丘來了")
        self.assertEqual(sources._clean_title("討論牆 | 皮卡丘變身聖誕樹 - LINE TODAY", "LINE TODAY"), "皮卡丘變身聖誕樹")
        self.assertEqual(sources._clean_title("寶可夢中心聖誕商品亮相- 遊戲新聞 - PChome Online 新聞", "PChome Online 新聞"), "寶可夢中心聖誕商品亮相")

    def test_unrelated_news_skipped(self):
        rss = """<rss><channel>
        <item><title>群募新品登場 經發局辦體驗會 - 蕃新聞</title><link>https://n/1</link><source>蕃新聞</source></item>
        <item><title>Pokémon Center TAIPEI 聖誕新品 - 上報</title><link>https://n/2</link><source>上報</source></item>
        </channel></rss>"""
        resp = type("R", (), {"content": rss.encode()})()
        with unittest.mock.patch.object(sources.news, "_get", return_value=resp):
            items = sources.fetch_google_news("q", NOW)
        self.assertEqual([i.title for i in items], ["Pokémon Center TAIPEI 聖誕新品"])

    def test_official_news_classified(self):
        product = sources.News("1", "寶可夢中心新商品發售", "u", "寶可夢官網", NOW)
        event = sources.News("2", "寶可夢嘉年華活動開跑", "u", "寶可夢官網", NOW)
        self.assertEqual(main.news_kind(product, "event"), "product")
        self.assertEqual(main.news_kind(event, "event"), "event")
        self.assertEqual(main.news_kind(news("xx"), "product"), "product")

    def test_build_news_dedupes_across_sources(self):
        out = main.build_news([
            ("event", [sources.News("o1", "寶可夢嘉年華台北場確定舉辦", "u", "寶可夢官網", NOW)]),
            ("event", [news("寶可夢嘉年華台北場確定舉辦！", "D 報")]),
        ])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["source"], "寶可夢官網")
        self.assertEqual(out[0]["others"], ["D 報"])

    def test_collect_splits_products_and_news(self):
        official = [sources.News("o1", "寶可夢中心新商品發售", "u", "寶可夢官網", NOW, category="商品"),
                    sources.News("o2", "寶可夢嘉年華活動開跑", "u", "寶可夢官網", NOW)]
        with unittest.mock.patch.multiple(
            sources, fetch_go_events=lambda: [], fetch_bahamut_tasks=lambda now: [], fetch_field_research=lambda: [],
            fetch_event_research=lambda events, now: [], fetch_pchome=lambda: [], fetch_official_news=lambda now: official, fetch_google_news=lambda q, now: [],
        ):
            payload = main.collect(NOW)
        self.assertEqual(payload["products"], [])
        self.assertEqual([(n["id"], n["kind"]) for n in payload["news"]], [("o1", "product"), ("o2", "event")])


class OfficialTests(unittest.TestCase):
    def test_parse_topics(self):
        html = """
        <a href="/topics/">最新消息</a>
        <a href="/topics/12345"><span>2026.10.20</span><p>寶可夢中心台北 萬聖節商品發售</p></a>
        <a href="/topics/12346">2026/10/18 寶可夢集換式卡牌比賽報名開始</a>
        <a href="/other">其他</a>"""
        items = sources.parse_official_news(html, "https://tw.portal-pokemon.com/topics/")
        self.assertEqual([i.title for i in items], ["寶可夢中心台北 萬聖節商品發售", "寶可夢集換式卡牌比賽報名開始"])
        self.assertEqual(items[0].published.date().isoformat(), "2026-10-20")

    def test_parse_topics_real_layout(self):
        html = """<a href="/topics/abc"><p>【Pokémon Center TAIPEI】2026年10月入店方法說明</p>
        <p>【Pokémon Center TAIPEI】2026年10月入店方法說明</p><span>商品</span><time>10.15.2026</time></a>"""
        [item] = sources.parse_official_news(html, "https://tw.portal-pokemon.com/topics/")
        self.assertEqual(item.title, "【Pokémon Center TAIPEI】2026年10月入店方法說明")
        self.assertEqual(item.category, "商品")
        self.assertEqual(item.published.date().isoformat(), "2026-10-15")
        self.assertEqual(main.news_kind(item, "event"), "product")

    def test_merged_title_halves(self):
        html = '<a href="/topics/x">寶可夢嘉年華開跑 寶可夢嘉年華開跑 活動 09.24.2026</a>'
        [item] = sources.parse_official_news(html, "https://tw.portal-pokemon.com/topics/")
        self.assertEqual((item.title, item.category), ("寶可夢嘉年華開跑", "活動"))


BAHAMUT_POST = """
<h1 class="c-post__header__title">【情報】萬聖節活動 限時調查任務與獎勵</h1>
<div class="c-post__header__info"><a class="edittime" data-mtime="2026-10-17 09:00:00">x</a></div>
<div class="c-article__content">
活動時間：10/17（五）10:00 ~ 10/21（二）20:00<br>
限時調查<br>
・捕捉10隻幽靈屬性寶可夢 → 星星沙×1000<br>
・轉動5個補給站 → 奇異糖果×3<br>
・孵化2顆蛋<br>
<div>使用5顆莓果｜獎勵：超級球×10</div>
本次活動會有更多寶可夢出現在野外<br>
完成所有任務後可以遇見南瓜精
</div>"""


class BahamutTests(unittest.TestCase):
    def test_parse_post(self):
        g = sources.parse_bahamut_post(BAHAMUT_POST, "https://b/1", "1", NOW)
        self.assertEqual(g.name, "萬聖節活動 限時調查任務與獎勵")
        self.assertEqual(g.start, datetime(2026, 10, 17, 10, tzinfo=config.TZ))
        self.assertEqual(g.end, datetime(2026, 10, 21, 20, tzinfo=config.TZ))
        self.assertEqual([(t, r) for _, t, r in g.tasks], [
            ("捕捉10隻幽靈屬性寶可夢", "星星沙×1000"),
            ("轉動5個補給站", "奇異糖果×3"),
            ("孵化2顆蛋", ""),
            ("使用5顆莓果", "超級球×10"),
        ])

    def test_tasks_have_stable_ids(self):
        g = sources.parse_bahamut_post(BAHAMUT_POST, "https://b/1", "1", NOW)
        self.assertEqual(g.tasks[0][0], sources.task_id("捕捉10隻幽靈屬性寶可夢"))
        self.assertEqual(sources.task_id("a"), sources.task_id("a"))
        self.assertNotEqual(sources.task_id("a"), sources.task_id("b"))
        [out] = main.build_tasks([g])
        self.assertTrue(all(t["id"] for t in out["tasks"]))

    def test_post_without_tasks_is_skipped(self):
        html = BAHAMUT_POST.replace("捕捉", "").replace("轉動", "").replace("孵化", "").replace("使用", "")
        self.assertIsNone(sources.parse_bahamut_post(html, "u", "1", NOW))

    def test_pinned_post_without_period_is_skipped(self):
        html = BAHAMUT_POST.replace("活動時間：10/17（五）10:00 ~ 10/21（二）20:00", "")
        self.assertIsNone(sources.parse_bahamut_post(html, "u", "1", NOW))

    def test_period_crosses_year(self):
        posted = datetime(2026, 12, 28, tzinfo=config.TZ)
        start, end = sources.parse_period("12/30 10:00 ~ 1/3 20:00", posted)
        self.assertEqual((start.year, end.year, end.month), (2026, 2027, 1))

    def test_single_day_period(self):
        start, end = sources.parse_period("10月25日 14:00 ~ 17:00", NOW)
        self.assertEqual((start.hour, end.day, end.hour), (14, 25, 17))

    def test_full_date_period(self):
        start, end = sources.parse_period("台灣時間2026年11月9日10:00～2026年11月13日20:00", NOW)
        self.assertEqual((start, end), (datetime(2026, 11, 9, 10, tzinfo=config.TZ), datetime(2026, 11, 13, 20, tzinfo=config.TZ)))
        start, end = sources.parse_period("2026年12月30日 10:00 ~ 1月3日", NOW)
        self.assertEqual((start, end), (datetime(2026, 12, 30, 10, tzinfo=config.TZ), datetime(2027, 1, 3, 23, 59, tzinfo=config.TZ)))

    def test_announcement_post_has_no_tasks(self):
        html = (FIXTURES / "bahamut_announcement.html").read_text(encoding="utf-8")
        self.assertIsNone(sources.parse_bahamut_post(html, "u", "1", NOW))

    def test_parse_list(self):
        html = """
        <a href="C.php?bsn=29659&snA=111&tnum=3">【情報】限時調查任務整理</a>
        <a href="C.php?bsn=29659&snA=222">【閒聊】今天抓到異色</a>
        <a href="C.php?bsn=29659&snA=111&last=1">【情報】限時調查任務整理</a>"""
        self.assertEqual(sources.parse_bahamut_list(html), [
            ("111", "【情報】限時調查任務整理", f"{config.BAHAMUT_POST_URL}?bsn={config.BAHAMUT_BSN}&snA=111"),
        ])


class EventTests(unittest.TestCase):
    def ev(self, eid, start, end, type_="event", name="Event"):
        return sources.GoEvent(eid, name, "Event", type_, "u", start, end)

    def test_filters_and_translates(self):
        n = NOW
        out = main.build_events([
            self.ev("a", n - timedelta(days=1), n + timedelta(days=1), "pokemon-spotlight-hour", "Pikachu Spotlight Hour"),
            self.ev("ended", n - timedelta(days=2), n - timedelta(hours=1)),
            self.ev("far", n + timedelta(days=30), n + timedelta(days=31)),
            self.ev("season", n - timedelta(days=1), n + timedelta(days=60), "season"),
        ], n)
        self.assertEqual([e["id"] for e in out], ["a"])
        self.assertEqual(out[0]["name"], "聚焦時刻：皮卡丘")
        self.assertEqual(out[0]["type"], "聚焦時刻")

    def test_event_without_end_is_dropped(self):
        n = NOW
        out = main.build_events([
            self.ev("noend", None, None, "max-mondays", "Dynamax Sneasel during Max Monday"),
            self.ev("ok", n - timedelta(days=1), n + timedelta(days=1)),
        ], n)
        self.assertEqual([e["id"] for e in out], ["ok"])

    def test_translate_still_works(self):
        self.assertEqual(translate.event_name("Charmander Community Day"), "小火龍社群日")
        self.assertEqual(translate.event_name("Pokémon GO Wild Area 2026: Sendai • Tohoku"), "Pokémon GO 野外區域 2026: 仙台・東北")
        self.assertEqual(translate.event_name("Minior Showers: Orionids 2026"), "小隕星流星雨：獵戶座 2026")


class FieldResearchTests(unittest.TestCase):
    def test_translate_tasks_and_rewards(self):
        self.assertEqual(translate.research_task("Catch 10 Ghost-type Pokémon"), "捕捉 10 隻幽靈屬性寶可夢")
        self.assertEqual(translate.research_task("Make 3 Excellent Throws in a row"), "連續投出 3 次「非常棒」")
        self.assertEqual(translate.research_task("Make 5 Great Curveball Throws in a row"), "連續投出 5 次「很棒曲球」")
        self.assertEqual(translate.research_task("Spin 5 PokéStops or Gyms"), "轉動 5 個補給站或道館")
        self.assertEqual(translate.research_task("Hatch an Egg"), "孵化 1 顆蛋")
        self.assertEqual(translate.pokemon("Alolan Geodude"), "阿羅拉小拳石")
        self.assertEqual(translate.pokemon("Spinda 4"), "晃晃斑 4")

    def test_group_follows_event_with_field_research(self):
        ev = sources.GoEvent("into-the-wild", "Into the Wild", "Event", "event", "u",
                             NOW - timedelta(days=1), NOW + timedelta(days=3), field_research=True)
        [g] = main.build_field_research([sources.Research("Trade a Pokémon", ["Haunter"])], [ev], NOW)
        self.assertEqual(g["id"], "field-into-the-wild")
        self.assertEqual(g["end"], ev.end.isoformat())
        self.assertEqual(g["tasks"], [{"id": "trade-a-pok-mon", "text": "交換 1 隻寶可夢", "reward": "遇見 鬼斯通"}])

    def test_group_without_event_ends_at_month_end(self):
        [g] = main.build_field_research([sources.Research("Explore 2 km", [])], [], NOW)
        self.assertEqual((g["id"], g["name"], g["end"][:16]), ("field-202610", "10 月田野調查", "2026-10-31T23:59"))
        self.assertEqual(main.build_field_research([], [], NOW), [])


class EventResearchTests(unittest.TestCase):
    def ev(self, eid, start, end, url="https://leekduck.com/events/x/", type_="research", name="adidas × Pokémon Timed Research"):
        return sources.GoEvent(eid, name, "Research", type_, url, start, end)

    def test_parse_timed_research_page(self):
        steps = sources.parse_event_research((FIXTURES / "leekduck_timed_research.html").read_text(encoding="utf-8"))
        self.assertEqual(steps[0], ("adidas Timed Research (1/3)", "Spin 10 PokéStops or Gyms", ["Razz Berry ×5"]))
        self.assertEqual(len(steps), 3)

    def test_page_without_research(self):
        self.assertEqual(sources.parse_event_research((FIXTURES / "leekduck_no_research.html").read_text(encoding="utf-8")), [])

    def test_only_active_events_are_read(self):
        n = NOW
        events = [
            self.ev("now", n - timedelta(days=1), n + timedelta(days=1)),
            self.ev("future", n + timedelta(days=3), n + timedelta(days=4)),
            self.ev("ended", n - timedelta(days=3), n - timedelta(days=1)),
            self.ev("season", n - timedelta(days=1), n + timedelta(days=9), type_="season"),
        ]
        html = (FIXTURES / "leekduck_timed_research.html").read_text(encoding="utf-8")
        resp = type("R", (), {"text": html})()
        with unittest.mock.patch.object(sources.leekduck, "_get", return_value=resp) as get:
            found = sources.fetch_event_research(events, n)
        self.assertEqual([ev.id for ev, _ in found], ["now"])
        self.assertEqual(get.call_count, 1)

    def test_group_shape(self):
        ev = self.ev("adidas", NOW - timedelta(days=1), NOW + timedelta(days=30))
        steps = sources.parse_event_research((FIXTURES / "leekduck_timed_research.html").read_text(encoding="utf-8"))
        [g] = main.build_event_research([(ev, steps)])
        self.assertEqual((g["id"], g["url"], g["end"]), ("ld-adidas", ev.url, ev.end.isoformat()))
        self.assertTrue(g["name"].startswith("限時調查："))
        self.assertEqual([(t["text"], t["reward"]) for t in g["tasks"]], [
            ("轉動 10 個補給站或道館", "蔓莓果 ×5"),
            ("捕捉 20 隻寶可夢", "薰香 ×3"),
            ("捕捉 20 隻寶可夢", "路卡利歐超級能量 ×40"),
        ])
        ids = [t["id"] for t in g["tasks"]]
        self.assertEqual(len(set(ids)), 3, "同樣的任務在不同步驟要有不同 id")
        [g] = main.build_event_research([(ev, [("s", "Use a Star Piece", ["Stardust ×7740"])] * 4)])
        self.assertEqual(len({t["id"] for t in g["tasks"]}), 4, "同一步驟重複的任務也要有不同 id")
        self.assertEqual((g["tasks"][0]["text"], g["tasks"][0]["reward"]), ("使用 1 個星星碎片", "星星沙 ×7740"))
        self.assertEqual(translate.research_task("Claim Reward!"), "領取獎勵")

    def test_claim_reward_is_skipped(self):
        ev = self.ev("minior", NOW - timedelta(days=1), NOW + timedelta(days=3))
        steps = [("s", "Use a Star Piece", ["Stardust ×7740"]), ("s", "Claim Reward!", ["Star Piece ×1"])]
        [g] = main.build_event_research([(ev, steps)])
        [full] = main.build_event_research([(ev, steps[:1])])
        self.assertEqual([t["text"] for t in g["tasks"]], ["使用 1 個星星碎片"])
        self.assertEqual(g["tasks"][0]["id"], full["tasks"][0]["id"])
        bh = sources.TaskGroup("bh-1", "巴哈", "u", NOW, NOW + timedelta(days=1), [("a", "捕捉 5 隻", ""), ("b", "領取獎勵", "")])
        self.assertEqual([t["text"] for t in main.build_tasks([bh])[0]["tasks"]], ["捕捉 5 隻"])

    def test_group_order(self):
        bh = sources.TaskGroup("bh-1", "巴哈", "u", NOW, NOW + timedelta(days=1), [("i", "t", "r")])
        ev = self.ev("adidas", NOW - timedelta(days=1), NOW + timedelta(days=30))
        steps = [("s", "Catch 20 Pokémon", [])]
        with unittest.mock.patch.multiple(
            sources, fetch_go_events=lambda: [ev], fetch_bahamut_tasks=lambda now: [bh],
            fetch_field_research=lambda: [sources.Research("Explore 2 km", [])],
            fetch_event_research=lambda events, now: [(ev, steps)], fetch_pchome=lambda: [],
            fetch_official_news=lambda now: [], fetch_google_news=lambda q, now: [],
        ):
            payload = main.collect(NOW)
        self.assertEqual([g["id"] for g in payload["taskGroups"]], ["bh-1", "ld-adidas", "field-202610"])


class CategoryTests(unittest.TestCase):
    def test_categories(self):
        cases = {
            ("pokemon-spotlight-hour", ""): "聚焦時刻",
            ("max-mondays", ""): "極巨化/超極巨化",
            ("raid-hour", ""): "團體戰/超級團體戰",
            ("go-pass", ""): "GO Pass",
            ("research", ""): "限時調查",
            ("event", "Halloween Timed Research"): "限時調查",
            ("community-day", ""): "其他",
            ("event", "Fall Marathon"): "其他",
        }
        for (slug, name), cat in cases.items():
            self.assertEqual(translate.event_category(slug, name), cat, slug + name)

    def test_keywords_in_name(self):
        # 規格 go-events「Six categories」的範例表
        cases = [
            ("event", "Dynamax Trails", "極巨化/超極巨化"),
            ("event", "GO Pass: Halloween", "GO Pass"),
            ("event", "Halloween 2026 Timed Research", "限時調查"),
            ("event", "Shadow Raid Weekend", "團體戰/超級團體戰"),
            ("event", "Fall Marathon: Buddy Trek", "其他"),
            ("raid-day", "Chandelure Super Mega Raid Day", "團體戰/超級團體戰"),
            ("community-day", "November Community Day", "其他"),
        ]
        for slug, name, cat in cases:
            self.assertEqual(translate.event_category(slug, name, translate.event_name(name)), cat, name)

    def test_chinese_keyword(self):
        self.assertEqual(translate.event_category("event", "Something", "夜間團體戰"), "團體戰/超級團體戰")
        self.assertEqual(translate.event_category("event", "go pass: november"), "GO Pass")

    def test_added_keyword_takes_effect(self):
        board = {**config.BOARD, "categories": [dict(c) for c in config.BOARD["categories"]]}
        board["categories"][0]["keywords"] = board["categories"][0]["keywords"] + ["Hour"]
        with unittest.mock.patch.dict(config.BOARD, board):
            self.assertEqual(translate.event_category("event", "Pokémon Hour"), "聚焦時刻")
        self.assertEqual(translate.event_category("event", "Pokémon Hour"), "其他")


class BoardTests(unittest.TestCase):
    def test_board_gs_is_generated(self):
        spec = importlib.util.spec_from_file_location("build_gas_config", ROOT / "scripts" / "build_gas_config.py")
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        self.assertEqual((ROOT / "gas" / "Board.gs").read_text(encoding="utf-8"), build.render(),
                         "shared/board.json 改過了，請執行 python scripts/build_gas_config.py")



class PChomeTests(unittest.TestCase):
    def test_duplicate_products_kept_once(self):
        prods = [
            {"Id": "DECU5W-A900FSAGQ", "name": "皮卡丘 卡比獸 百變怪 精靈球 造型存錢筒", "price": 590},
            {"Id": "DEAS4E-A900FSAIT", "name": "皮卡丘  卡比獸 百變怪 精靈球 造型存錢筒", "price": 590},
            {"Id": "X1", "name": "皮卡丘 玩偶", "price": 500},
            {"Id": "X2", "name": "皮卡丘 玩偶", "price": 650},
        ]
        resp = type("R", (), {"json": lambda self: {"totalPage": 1, "prods": prods}})()
        with unittest.mock.patch.object(sources.pchome, "_get", return_value=resp):
            items = sources.fetch_pchome()
        self.assertEqual([p.id for p in items], ["pchome:DECU5W-A900FSAGQ", "pchome:X1", "pchome:X2"])


if __name__ == "__main__":
    unittest.main()
