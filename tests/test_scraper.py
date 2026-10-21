import unittest
from datetime import datetime, timedelta

from scraper import config, main, sources, translate


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

    def test_known_titles_are_skipped(self):
        kept = sources.dedupe_news([news("寶可夢快閃店進駐高雄 為期兩週")], ["寶可夢快閃店進駐高雄，為期兩週"])
        self.assertEqual(kept, [])

    def test_google_title_suffix_removed(self):
        self.assertEqual(sources._clean_title("皮卡丘來了 - 自由時報", "自由時報"), "皮卡丘來了")

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
        self.assertEqual(g.tasks, [
            ("捕捉10隻幽靈屬性寶可夢", "星星沙×1000"),
            ("轉動5個補給站", "奇異糖果×3"),
            ("孵化2顆蛋", ""),
            ("使用5顆莓果", "超級球×10"),
        ])

    def test_post_without_tasks_is_skipped(self):
        html = BAHAMUT_POST.replace("捕捉", "").replace("轉動", "").replace("孵化", "").replace("使用", "")
        self.assertIsNone(sources.parse_bahamut_post(html, "u", "1", NOW))

    def test_period_crosses_year(self):
        posted = datetime(2026, 12, 28, tzinfo=config.TZ)
        start, end = sources.parse_period("12/30 10:00 ~ 1/3 20:00", posted)
        self.assertEqual((start.year, end.year, end.month), (2026, 2027, 1))

    def test_single_day_period(self):
        start, end = sources.parse_period("10月25日 14:00 ~ 17:00", NOW)
        self.assertEqual((start.hour, end.day, end.hour), (14, 25, 17))

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

    def test_translate_still_works(self):
        self.assertEqual(translate.event_name("Charmander Community Day"), "小火龍社群日")


if __name__ == "__main__":
    unittest.main()
