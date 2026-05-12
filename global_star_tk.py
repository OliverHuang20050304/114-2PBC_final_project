from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Optional

import global_star_cli as core


@dataclass(slots=True)
class _Session:
    """Holds runtime session state for the GUI."""

    state: core.GameState
    current: core.NodeId
    ch1_bucket: Optional[str] = None


class GlobalStarTkApp:
    """A pure-text GUI for GLOBAL STAR using Tkinter."""

    def __init__(self, root: tk.Tk, seed: Optional[int] = None) -> None:
        self._root = root
        self._seed = seed
        self._nodes = core.build_nodes()
        self._session: Optional[_Session] = None

        self._root.title("GLOBAL STAR：成名之路（純文字 GUI）")
        self._root.geometry("900x650")

        self._build_ui()
        self._show_start_screen()

    def _build_ui(self) -> None:
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        self._container = ttk.Frame(self._root, padding=12)
        self._container.grid(row=0, column=0, sticky="nsew")
        self._container.columnconfigure(0, weight=3)
        self._container.columnconfigure(1, weight=1)
        self._container.rowconfigure(0, weight=1)
        self._container.rowconfigure(1, weight=0)

        # Main story area (scrollable)
        self._story_frame = ttk.Frame(self._container)
        self._story_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._story_frame.columnconfigure(0, weight=1)
        self._story_frame.rowconfigure(0, weight=1)

        self._story_text = tk.Text(
            self._story_frame,
            wrap="word",
            height=20,
            padx=10,
            pady=10,
            state="disabled",
            font=("Helvetica", 14),
        )
        self._story_text.grid(row=0, column=0, sticky="nsew")

        self._story_scroll = ttk.Scrollbar(self._story_frame, orient="vertical", command=self._story_text.yview)
        self._story_scroll.grid(row=0, column=1, sticky="ns")
        self._story_text.configure(yscrollcommand=self._story_scroll.set)

        # Sidebar (stats and flags)
        self._side = ttk.Frame(self._container)
        self._side.grid(row=0, column=1, sticky="nsew")
        self._side.columnconfigure(0, weight=1)

        self._stats_title = ttk.Label(self._side, text="狀態", font=("Helvetica", 14, "bold"))
        self._stats_title.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self._stats_var = tk.StringVar(value="")
        self._stats_label = ttk.Label(self._side, textvariable=self._stats_var, justify="left")
        self._stats_label.grid(row=1, column=0, sticky="w")

        self._flags_title = ttk.Label(self._side, text="旗標", font=("Helvetica", 14, "bold"))
        self._flags_title.grid(row=2, column=0, sticky="w", pady=(16, 6))

        self._flags_var = tk.StringVar(value="")
        self._flags_label = ttk.Label(self._side, textvariable=self._flags_var, justify="left", wraplength=220)
        self._flags_label.grid(row=3, column=0, sticky="w")

        # Choices area (buttons)
        self._choices = ttk.Frame(self._container)
        self._choices.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self._choices.columnconfigure(0, weight=1)

        self._choices_title = ttk.Label(self._choices, text="選項", font=("Helvetica", 14, "bold"))
        self._choices_title.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self._choices_buttons = ttk.Frame(self._choices)
        self._choices_buttons.grid(row=1, column=0, sticky="ew")
        self._choices_buttons.columnconfigure(0, weight=1)

    def _set_story(self, text: str) -> None:
        self._story_text.configure(state="normal")
        self._story_text.delete("1.0", "end")
        self._story_text.insert("1.0", text)
        self._story_text.configure(state="disabled")
        self._story_text.see("1.0")

    def _clear_choices(self) -> None:
        for child in self._choices_buttons.winfo_children():
            child.destroy()

    def _set_choices(self, labels: list[str], handlers: list[callable]) -> None:
        self._clear_choices()
        for idx, (label, handler) in enumerate(zip(labels, handlers, strict=True), start=1):
            btn = ttk.Button(self._choices_buttons, text=label, command=handler)
            btn.grid(row=idx, column=0, sticky="ew", pady=4)

    def _update_sidebar(self) -> None:
        if self._session is None:
            self._stats_var.set("")
            self._flags_var.set("")
            return

        s = self._session.state
        self._stats_var.set(
            "\n".join(
                [
                    f"城市：{s.city_name}",
                    f"風格：{s.style}",
                    "",
                    f"fame：{s.fame}",
                    f"image：{s.image}",
                    f"health：{s.health}",
                    f"money：{s.money}",
                ]
            )
        )

        flags: list[str] = []
        if s.has_mystery_producer:
            flags.append("與神祕製作人合作（伏筆）")
        if self._session.ch1_bucket is not None:
            flags.append(f"Chapter 1 結果：{self._session.ch1_bucket}")
        self._flags_var.set("\n".join(flags) if flags else "（無）")

    def _show_start_screen(self) -> None:
        self._session = None
        self._update_sidebar()

        self._set_story(
            "\n".join(
                [
                    "《GLOBAL STAR：成名之路》純文字 GUI",
                    "",
                    "你是一個來自普通家庭的新人。",
                    "請先選擇出道城市與出道風格。",
                ]
            )
        )

        def pick_city_and_style(city: str, style: str) -> None:
            state = core._initial_stats(city=city, style=style, seed=self._seed)
            self._session = _Session(state=state, current="ch1_intro")
            self._render_current_node()

        cities = [
            ("洛杉磯", "洛杉磯（競爭激烈）"),
            ("倫敦", "倫敦（藝術氣息）"),
            ("紐約", "紐約（媒體中心）"),
        ]
        styles = [
            ("Rebel", "叛逆流派（Rebel）"),
            ("Pop Idol", "商業流行（Pop Idol）"),
            ("Indie", "藝術地下（Indie）"),
        ]

        # Two-step selection UI: pick city then style
        selected_city = tk.StringVar(value=cities[0][0])
        selected_style = tk.StringVar(value=styles[1][0])

        def start_game() -> None:
            pick_city_and_style(selected_city.get(), selected_style.get())

        self._clear_choices()

        city_box = ttk.LabelFrame(self._choices_buttons, text="出道城市")
        city_box.grid(row=1, column=0, sticky="ew", pady=6)
        for idx, (val, label) in enumerate(cities):
            ttk.Radiobutton(city_box, text=label, variable=selected_city, value=val).grid(
                row=idx, column=0, sticky="w", padx=8, pady=2
            )

        style_box = ttk.LabelFrame(self._choices_buttons, text="出道風格")
        style_box.grid(row=2, column=0, sticky="ew", pady=6)
        for idx, (val, label) in enumerate(styles):
            ttk.Radiobutton(style_box, text=label, variable=selected_style, value=val).grid(
                row=idx, column=0, sticky="w", padx=8, pady=2
            )

        ttk.Button(self._choices_buttons, text="開始遊戲", command=start_game).grid(
            row=3, column=0, sticky="ew", pady=(10, 0)
        )

    def _render_current_node(self) -> None:
        if self._session is None:
            self._show_start_screen()
            return

        s = self._session.state
        current = self._session.current

        # Special transitions mirroring CLI behavior
        if current == "ch1_route":
            self._session.ch1_bucket = core._chapter1_result_bucket(s)
        if current == "ch2_enter":
            # dispatch immediately without user action
            self._session.current = core._dispatch_ch2(s)
            s.clamp()
            self._render_current_node()
            return

        if current == "end":
            flags = []
            if s.has_mystery_producer:
                flags.append("伏筆：你曾與神祕製作人合作（星辰議會的影子仍在）。")
            if core._maybe_force_controversy(s):
                flags.append("提示：你的 image 偏低，較容易走向爭議巨星型態。")

            self._set_story(
                "\n".join(
                    [
                        "（完）",
                        "",
                        f"城市：{s.city_name} | 風格：{s.style}",
                        f"最終數值：{core._render_state(s)}",
                        "",
                        *flags,
                        "",
                        f"結局：{core._ending_name(s)}",
                    ]
                )
            )
            self._set_choices(
                labels=["回到主選單（重新開始）", "離開"],
                handlers=[self._show_start_screen, self._root.destroy],
            )
            self._update_sidebar()
            return

        node = self._nodes[current]
        text = core._format_text(node.text, s) if node.text else ""

        # If ch1_route, append the bucket result text like the CLI does
        if current == "ch1_route":
            b = self._session.ch1_bucket
            if b == "爆紅":
                text += "\n\n結果：📈 爆紅！你的名字在社群與排行榜上快速擴散。"
            elif b == "普通成功":
                text += "\n\n結果：⚖️ 普通成功。你被看見了，但還沒被定義。"
            else:
                text += "\n\n結果：💥 失敗。你感到市場的冷淡與公司的不耐。"

        self._set_story(text)

        labels: list[str] = []
        handlers: list[callable] = []

        for ch in node.choices:
            labels.append(f"[{ch.key}] {ch.label}")

            def _make_handler(choice: core.Choice) -> callable:
                def _handler() -> None:
                    if choice.apply is not None:
                        choice.apply(s)
                        s.clamp()
                    self._session.current = choice.next_node
                    self._render_current_node()

                return _handler

            handlers.append(_make_handler(ch))

        self._set_choices(labels=labels, handlers=handlers)
        self._update_sidebar()


def main() -> None:
    """Entry point for the Tkinter GUI."""
    root = tk.Tk()

    # ttk theme (best effort; falls back gracefully)
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass

    GlobalStarTkApp(root=root, seed=None)
    root.mainloop()


if __name__ == "__main__":
    main()

