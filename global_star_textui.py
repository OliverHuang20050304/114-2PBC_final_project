from __future__ import annotations

import curses
import textwrap
from dataclasses import dataclass
from typing import Optional

import global_star_cli as core


@dataclass(slots=True)
class _Session:
    state: core.GameState
    current: core.NodeId
    ch1_bucket: Optional[str] = None
    scroll: int = 0


def _wrap(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for para in text.splitlines():
        if not para.strip():
            lines.append("")
            continue
        lines.extend(textwrap.wrap(para, width=width, break_long_words=False, replace_whitespace=False))
    return lines


def _render_end(session: _Session) -> str:
    s = session.state
    flags: list[str] = []
    if s.has_mystery_producer:
        flags.append("伏筆：你曾與神祕製作人合作（星辰議會的影子仍在）。")
    if core._maybe_force_controversy(s):
        flags.append("提示：你的 image 偏低，較容易走向爭議巨星型態。")
    return "\n".join(
        [
            "（完）",
            "",
            f"城市：{s.city_name} | 風格：{s.style}",
            f"最終數值：{core._render_state(s)}",
            "",
            *flags,
            "",
            f"結局：{core._ending_name(s)}",
            "",
            "按 [R] 重新開始，或按 [Q] 離開。",
        ]
    )


def _start_session(seed: Optional[int]) -> _Session:
    # Default values; will be overwritten by start screen picks
    state = core._initial_stats(city="洛杉磯", style="Pop Idol", seed=seed)
    return _Session(state=state, current="ch1_intro")


def _pick_city_style(stdscr: curses.window, seed: Optional[int]) -> _Session:
    cities = [("洛杉磯", "洛杉磯（競爭激烈）"), ("倫敦", "倫敦（藝術氣息）"), ("紐約", "紐約（媒體中心）")]
    styles = [("Rebel", "叛逆流派（Rebel）"), ("Pop Idol", "商業流行（Pop Idol）"), ("Indie", "藝術地下（Indie）")]

    city_idx = 0
    style_idx = 1

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        title = "GLOBAL STAR：成名之路（Text UI）"
        stdscr.addstr(1, max(0, (w - len(title)) // 2), title, curses.A_BOLD)
        stdscr.addstr(3, 2, "用 ↑↓ 選城市、用 ←→ 選風格，按 Enter 開始。按 Q 離開。")

        stdscr.addstr(5, 2, "出道城市：", curses.A_BOLD)
        for i, (_, label) in enumerate(cities):
            attr = curses.A_REVERSE if i == city_idx else curses.A_NORMAL
            stdscr.addstr(6 + i, 4, label[: w - 6], attr)

        stdscr.addstr(10, 2, "出道風格：", curses.A_BOLD)
        for i, (_, label) in enumerate(styles):
            attr = curses.A_REVERSE if i == style_idx else curses.A_NORMAL
            stdscr.addstr(11 + i, 4, label[: w - 6], attr)

        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            raise SystemExit(0)
        if key == curses.KEY_UP:
            city_idx = (city_idx - 1) % len(cities)
        elif key == curses.KEY_DOWN:
            city_idx = (city_idx + 1) % len(cities)
        elif key == curses.KEY_LEFT:
            style_idx = (style_idx - 1) % len(styles)
        elif key == curses.KEY_RIGHT:
            style_idx = (style_idx + 1) % len(styles)
        elif key in (curses.KEY_ENTER, 10, 13):
            city = cities[city_idx][0]
            style = styles[style_idx][0]
            state = core._initial_stats(city=city, style=style, seed=seed)
            return _Session(state=state, current="ch1_intro")


def _main(stdscr: curses.window, seed: Optional[int]) -> None:
    curses.curs_set(0)
    stdscr.keypad(True)

    session = _pick_city_style(stdscr, seed=seed)
    nodes = core.build_nodes()

    while True:
        s = session.state
        current = session.current

        # Auto transitions like the CLI
        if current == "ch1_route":
            session.ch1_bucket = core._chapter1_result_bucket(s)
        if current == "ch2_enter":
            if session.ch1_bucket is None:
                session.ch1_bucket = core._chapter1_result_bucket(s)
            session.current = core._dispatch_ch2(s)
            s.clamp()
            session.scroll = 0
            continue

        # Compose screen text
        if current == "end":
            body = _render_end(session)
            choices: list[core.Choice] = []
        else:
            node = nodes[current]
            body = core._format_text(node.text, s) if node.text else ""
            if current == "ch1_route":
                b = session.ch1_bucket
                if b == "爆紅":
                    body += "\n\n結果：📈 爆紅！你的名字在社群與排行榜上快速擴散。"
                elif b == "普通成功":
                    body += "\n\n結果：⚖️ 普通成功。你被看見了，但還沒被定義。"
                else:
                    body += "\n\n結果：💥 失敗。你感到市場的冷淡與公司的不耐。"
            choices = node.choices

        # Draw layout
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        # Header/stats
        header = f"城市：{s.city_name} | 風格：{s.style} | {core._render_state(s)}"
        stdscr.addstr(0, 0, header[: w - 1], curses.A_BOLD)

        # Flags line
        flags = []
        if s.has_mystery_producer:
            flags.append("MysteryProducer")
        if session.ch1_bucket is not None:
            flags.append(f"CH1={session.ch1_bucket}")
        flags_line = "Flags: " + (", ".join(flags) if flags else "（無）")
        stdscr.addstr(1, 0, flags_line[: w - 1])

        # Story panel
        story_top = 3
        story_bottom = h - 6
        story_height = max(3, story_bottom - story_top + 1)
        lines = _wrap(body, width=max(20, w - 2))
        max_scroll = max(0, len(lines) - story_height)
        session.scroll = max(0, min(session.scroll, max_scroll))
        view = lines[session.scroll : session.scroll + story_height]
        for i, line in enumerate(view):
            stdscr.addstr(story_top + i, 1, line[: w - 2])

        # Footer help
        stdscr.addstr(h - 2, 0, "↑↓ 捲動劇情 | 1-9 選擇選項 | Q 離開", curses.A_DIM)

        # Choices panel
        if current == "end":
            stdscr.addstr(h - 4, 0, "[R] 重新開始    [Q] 離開", curses.A_BOLD)
        else:
            stdscr.addstr(h - 4, 0, "選項：", curses.A_BOLD)
            for i, c in enumerate(choices[:9], start=1):
                stdscr.addstr(h - 4 + (i // 5), 6 + ((i - 1) % 4) * (w // 4), f"{i}.{c.label}"[: w - 1])

        stdscr.refresh()

        # Input handling
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            return
        if current == "end" and key in (ord("r"), ord("R")):
            session = _pick_city_style(stdscr, seed=seed)
            continue
        if key == curses.KEY_UP:
            session.scroll -= 1
            continue
        if key == curses.KEY_DOWN:
            session.scroll += 1
            continue

        # Choice selection 1..9
        if current != "end" and ord("1") <= key <= ord("9"):
            idx = key - ord("1")
            if 0 <= idx < len(choices):
                ch = choices[idx]
                if ch.apply is not None:
                    ch.apply(s)
                    s.clamp()
                session.current = ch.next_node
                session.scroll = 0


def run(seed: Optional[int] = None) -> None:
    """Run the text UI game.

    Notes:
        - This is a pure-text GUI (terminal UI) using curses.
        - Works without images and without external dependencies.
    """
    curses.wrapper(lambda stdscr: _main(stdscr, seed=seed))


if __name__ == "__main__":
    run(seed=None)

