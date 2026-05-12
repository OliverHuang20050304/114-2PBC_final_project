"""GLOBAL STAR visual front-end using pygame (no Tk required).

Install dependencies::

    pip install -r requirements.txt

If ``pygame.font`` fails on your Python build (e.g. some 3.14 wheels), this
program falls back to **Pillow** plus common system font paths for CJK text.

Run from project root (same folder as ``global_star_cli.py``)::

    python global_star_pygame.py
"""

from __future__ import annotations

import os
import platform
import textwrap
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Protocol

import pygame

import global_star_cli as core

_FONT_FAMILY_NAMES: tuple[str, ...] = (
    "PingFang TC",
    "Heiti TC",
    "Microsoft JhengHei",
    "Noto Sans CJK TC",
    "Arial Unicode MS",
)


class _UiTextFont(Protocol):
    """Subset of ``pygame.font.Font`` used by this module."""

    def render(self, text: str, antialias: bool, color: tuple[int, int, int]) -> pygame.Surface: ...

    def get_linesize(self) -> int: ...


class _PygameFontModuleWrapper:
    """Wraps ``pygame.font.Font`` for a stable ``_UiTextFont`` implementation."""

    def __init__(self, inner: pygame.font.Font) -> None:
        self._inner = inner

    def render(self, text: str, antialias: bool, color: tuple[int, int, int]) -> pygame.Surface:
        return self._inner.render(text, antialias, color)

    def get_linesize(self) -> int:
        return int(self._inner.get_linesize())


def _system_font_file_paths() -> list[str]:
    """Return likely paths to fonts with good CJK coverage (best-effort per OS)."""
    system = platform.system()
    if system == "Darwin":
        return [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Songti.ttc",
        ]
    if system == "Windows":
        fonts_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
        return [
            os.path.join(fonts_dir, "msjh.ttc"),
            os.path.join(fonts_dir, "msjhbd.ttc"),
            os.path.join(fonts_dir, "mingliu.ttc"),
            os.path.join(fonts_dir, "arialuni.ttf"),
        ]
    return [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]


def _pil_image_to_surface(image: "Image.Image") -> pygame.Surface:
    """Convert a Pillow RGBA image to a pygame surface."""
    from PIL import Image

    if image.mode != "RGBA":
        image = image.convert("RGBA")
    return pygame.image.frombytes(image.tobytes(), image.size, "RGBA").convert_alpha()


class _PillowFontWrapper:
    """Render text with Pillow when ``pygame.font`` is broken (e.g. Python 3.14 + pygame 2.6.x)."""

    def __init__(self, pil_font: "ImageFont.FreeTypeFont") -> None:
        from PIL import ImageFont

        self._pil_font: ImageFont.FreeTypeFont = pil_font

    def render(self, text: str, antialias: bool, color: tuple[int, int, int]) -> pygame.Surface:
        from PIL import Image, ImageDraw

        _ = antialias  # Pillow uses FreeType hinting; flag kept for API parity.
        if text == "":
            im = Image.new("RGBA", (2, max(2, self.get_linesize())), (0, 0, 0, 0))
            return _pil_image_to_surface(im)

        probe = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        draw_probe = ImageDraw.Draw(probe)
        bbox = draw_probe.textbbox((0, 0), text, font=self._pil_font)
        w = max(1, bbox[2] - bbox[0])
        h = max(1, bbox[3] - bbox[1])
        pad = 4
        im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.text(
            (pad - bbox[0], pad - bbox[1]),
            text,
            font=self._pil_font,
            fill=(*color, 255),
        )
        return _pil_image_to_surface(im)

    def get_linesize(self) -> int:
        from PIL import Image, ImageDraw

        draw = ImageDraw.Draw(Image.new("RGBA", (16, 16), (0, 0, 0, 0)))
        bbox = draw.textbbox((0, 0), "Ay測Qpq", font=self._pil_font)
        return max(16, bbox[3] - bbox[1] + 6)


def _try_font_module_font(size: int) -> Optional[_UiTextFont]:
    """Build a font via ``pygame.font`` if the module initializes correctly."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        try:
            if not pygame.font.get_init():
                pygame.font.init()
        except Exception:
            return None

        for name in _FONT_FAMILY_NAMES:
            try:
                candidate = pygame.font.SysFont(name, size)
            except Exception:
                continue
            try:
                probe = candidate.render("測", True, (255, 255, 255))
            except Exception:
                continue
            if probe.get_width() > 0:
                return _PygameFontModuleWrapper(candidate)

        try:
            fallback = pygame.font.SysFont("sans-serif", size)
        except Exception:
            return None
        return _PygameFontModuleWrapper(fallback)


def _try_pillow_font(size: int) -> Optional[_UiTextFont]:
    """Load a system TTF/TTC via Pillow when ``pygame.font`` is unavailable."""
    try:
        from PIL import ImageFont
    except ImportError:
        return None

    for path in _system_font_file_paths():
        if not Path(path).is_file():
            continue
        try:
            pil_font = ImageFont.truetype(path, size)
        except OSError:
            continue
        try:
            wrapper = _PillowFontWrapper(pil_font)
            probe = wrapper.render("測", True, (255, 255, 255))
        except Exception:
            continue
        if probe.get_width() > 0:
            return wrapper

    return None


def _create_ui_font(size: int) -> _UiTextFont:
    """Return a UI font: prefer ``pygame.font``, else Pillow + system font files."""
    font_mod = _try_font_module_font(size)
    if font_mod is not None:
        return font_mod
    pillow_font = _try_pillow_font(size)
    if pillow_font is not None:
        return pillow_font
    raise RuntimeError(
        "無法建立 UI 字型：pygame.font 無法使用，且 Pillow 找不到可用的中文字型檔。"
        "請執行：pip install -U Pillow pygame；"
        "若仍失敗，請改用 Python 3.12 建立虛擬環境，或安裝系統字型（如 Noto CJK）。"
    )


@dataclass(slots=True)
class _Session:
    """Holds runtime session state (mirrors the Tkinter GUI)."""

    state: core.GameState
    current: core.NodeId
    ch1_bucket: Optional[str] = None


def _wrap_story(text: str, width_chars: int) -> list[str]:
    """Wrap story text into lines."""
    lines: list[str] = []
    for para in text.splitlines():
        if not para.strip():
            lines.append("")
            continue
        lines.extend(
            textwrap.wrap(
                para,
                width=width_chars,
                break_long_words=False,
                replace_whitespace=False,
            )
        )
    return lines


class GlobalStarPygameApp:
    """Pygame window: story panel, sidebar, and choice buttons."""

    WIDTH = 900
    HEIGHT = 700
    STORY_RECT = pygame.Rect(16, 52, 598, 380)
    SIDE_RECT = pygame.Rect(626, 52, 258, 380)
    CHOICE_TOP = 448

    CITIES: list[tuple[str, str]] = [
        ("洛杉磯", "洛杉磯（競爭激烈）"),
        ("倫敦", "倫敦（藝術氣息）"),
        ("紐約", "紐約（媒體中心）"),
    ]
    STYLES: list[tuple[str, str]] = [
        ("Rebel", "叛逆流派（Rebel）"),
        ("Pop Idol", "商業流行（Pop Idol）"),
        ("Indie", "藝術地下（Indie）"),
    ]

    def __init__(self, seed: Optional[int] = None) -> None:
        self._seed = seed
        self._nodes = core.build_nodes()
        self._session: Optional[_Session] = None
        self._start_city_idx = 0
        self._start_style_idx = 1
        self._story_scroll = 0
        self._story_lines: list[str] = []
        self._choice_handlers: list[tuple[pygame.Rect, str, Callable[[], None]]] = []

        pygame.init()
        pygame.display.set_caption("GLOBAL STAR：成名之路（Pygame）")
        self._screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self._clock = pygame.time.Clock()
        self._font_title = _create_ui_font(22)
        self._font_body = _create_ui_font(18)
        self._font_small = _create_ui_font(15)
        self._font_btn = _create_ui_font(15)

        self._colors = {
            "bg": (28, 32, 40),
            "panel": (40, 46, 58),
            "text": (230, 235, 245),
            "muted": (150, 160, 180),
            "accent": (100, 180, 255),
            "btn": (55, 65, 85),
            "btn_hover": (72, 88, 115),
            "btn_border": (120, 140, 170),
        }

        self._show_start_screen()

    def _set_story_text(self, text: str) -> None:
        """Build wrapped lines for the story panel."""
        approx_chars = max(18, self.STORY_RECT.width // 16)
        self._story_lines = _wrap_story(text, approx_chars)
        self._story_scroll = 0

    def _show_start_screen(self) -> None:
        self._session = None
        self._set_story_text(
            "\n".join(
                [
                    "《GLOBAL STAR：成名之路》Pygame 版",
                    "",
                    "你是一個來自普通家庭的新人。",
                    "下方選擇出道城市與風格，再按「開始遊戲」。",
                ]
            )
        )
        self._rebuild_start_choices()

    def _rebuild_start_choices(self) -> None:
        """Build clickable rects for city, style, and start (start menu)."""
        self._choice_handlers.clear()
        y = self.CHOICE_TOP
        col_w = (self.WIDTH - 32 - 16) // 3

        for i, (_, disp) in enumerate(self.CITIES):
            r = pygame.Rect(16 + i * (col_w + 8), y, col_w, 38)

            def pick_city(idx: int = i) -> None:
                self._start_city_idx = idx
                self._rebuild_start_choices()

            self._choice_handlers.append((r, disp, pick_city))
        y += 48

        for i, (_, disp) in enumerate(self.STYLES):
            r = pygame.Rect(16 + i * (col_w + 8), y, col_w, 38)

            def pick_style(idx: int = i) -> None:
                self._start_style_idx = idx
                self._rebuild_start_choices()

            self._choice_handlers.append((r, disp, pick_style))
        y += 52

        start_r = pygame.Rect(16, y, 280, 44)

        def start_game() -> None:
            city = self.CITIES[self._start_city_idx][0]
            style = self.STYLES[self._start_style_idx][0]
            state = core._initial_stats(city=city, style=style, seed=self._seed)
            self._session = _Session(state=state, current="ch1_intro")
            self._render_current_node()

        self._choice_handlers.append((start_r, "開始遊戲", start_game))

    def _render_current_node(self) -> None:
        if self._session is None:
            self._show_start_screen()
            return

        s = self._session.state
        current = self._session.current

        if current == "ch1_route":
            self._session.ch1_bucket = core._chapter1_result_bucket(s)
        if current == "ch2_enter":
            self._session.current = core._dispatch_ch2(s)
            s.clamp()
            self._render_current_node()
            return

        if current == "end":
            flags: list[str] = []
            if s.has_mystery_producer:
                flags.append("伏筆：你曾與神祕製作人合作（星辰議會的影子仍在）。")
            if core._maybe_force_controversy(s):
                flags.append("提示：你的 image 偏低，較容易走向爭議巨星型態。")
            self._set_story_text(
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
            self._choice_handlers.clear()
            y = self.CHOICE_TOP
            r1 = pygame.Rect(16, y, 400, 44)
            r2 = pygame.Rect(430, y, 200, 44)

            def back() -> None:
                self._show_start_screen()

            def quit_app() -> None:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

            self._choice_handlers.append((r1, "回到主選單（重新開始）", back))
            self._choice_handlers.append((r2, "離開", quit_app))
            return

        node = self._nodes[current]
        text = core._format_text(node.text, s) if node.text else ""
        if current == "ch1_route":
            b = self._session.ch1_bucket
            if b == "爆紅":
                text += "\n\n結果：📈 爆紅！你的名字在社群與排行榜上快速擴散。"
            elif b == "普通成功":
                text += "\n\n結果：⚖️ 普通成功。你被看見了，但還沒被定義。"
            else:
                text += "\n\n結果：💥 失敗。你感到市場的冷淡與公司的不耐。"
        self._set_story_text(text)

        self._choice_handlers.clear()
        y = self.CHOICE_TOP
        btn_h = 40
        gap = 6
        for ch in node.choices:
            label = f"[{ch.key}] {ch.label}"
            r = pygame.Rect(16, y, self.WIDTH - 32, btn_h)
            y += btn_h + gap

            def make_handler(choice: core.Choice) -> Callable[[], None]:
                def _handler() -> None:
                    if choice.apply is not None:
                        choice.apply(s)
                        s.clamp()
                    assert self._session is not None
                    self._session.current = choice.next_node
                    self._render_current_node()

                return _handler

            self._choice_handlers.append((r, label, make_handler(ch)))

    def _visible_story_line_count(self) -> int:
        line_h = self._font_body.get_linesize()
        inner_h = self.STORY_RECT.height - 28
        return max(1, inner_h // line_h)

    def _draw(self, mouse_pos: tuple[int, int]) -> None:
        c = self._colors
        self._screen.fill(c["bg"])

        title = self._font_title.render("GLOBAL STAR：成名之路", True, c["text"])
        self._screen.blit(title, (16, 10))

        pygame.draw.rect(self._screen, c["panel"], self.STORY_RECT, border_radius=8)
        pygame.draw.rect(self._screen, c["btn_border"], self.STORY_RECT, width=1, border_radius=8)

        line_h = self._font_body.get_linesize()
        max_lines = self._visible_story_line_count()
        max_scroll = max(0, len(self._story_lines) - max_lines)
        self._story_scroll = max(0, min(self._story_scroll, max_scroll))

        y = self.STORY_RECT.y + 8
        for line in self._story_lines[self._story_scroll : self._story_scroll + max_lines]:
            surf = self._font_body.render(line, True, c["text"])
            self._screen.blit(surf, (self.STORY_RECT.x + 10, y))
            y += line_h

        hint = self._font_small.render("滑鼠滾輪／↑↓ 捲動劇情", True, c["muted"])
        self._screen.blit(hint, (self.STORY_RECT.x + 10, self.STORY_RECT.bottom - 22))

        pygame.draw.rect(self._screen, c["panel"], self.SIDE_RECT, border_radius=8)
        pygame.draw.rect(self._screen, c["btn_border"], self.SIDE_RECT, width=1, border_radius=8)

        if self._session is None:
            sy = self.SIDE_RECT.y + 10
            self._screen.blit(self._font_small.render("狀態", True, c["accent"]), (self.SIDE_RECT.x + 10, sy))
            sy += self._font_small.get_linesize() + 6
            self._screen.blit(
                self._font_small.render("尚未開始遊戲", True, c["muted"]),
                (self.SIDE_RECT.x + 10, sy),
            )
        else:
            s = self._session.state
            sy = self.SIDE_RECT.y + 10
            for t in (
                "狀態",
                f"城市：{s.city_name}",
                f"風格：{s.style}",
                "",
                f"fame：{s.fame}",
                f"image：{s.image}",
                f"health：{s.health}",
                f"money：{s.money}",
            ):
                color = c["accent"] if t == "狀態" else c["text"]
                self._screen.blit(self._font_small.render(t, True, color), (self.SIDE_RECT.x + 10, sy))
                sy += self._font_small.get_linesize() + (4 if t == "狀態" else 2)

            sy += 8
            self._screen.blit(self._font_small.render("旗標", True, c["accent"]), (self.SIDE_RECT.x + 10, sy))
            sy += self._font_small.get_linesize() + 4
            flags: list[str] = []
            if s.has_mystery_producer:
                flags.append("神祕製作人")
            if self._session.ch1_bucket is not None:
                flags.append(f"CH1={self._session.ch1_bucket}")
            flag_text = "、".join(flags) if flags else "（無）"
            for wrapped in textwrap.wrap(flag_text, width=14):
                self._screen.blit(self._font_small.render(wrapped, True, c["text"]), (self.SIDE_RECT.x + 10, sy))
                sy += self._font_small.get_linesize()

        if self._session is None:
            lab_y = self.CHOICE_TOP - 44
            self._screen.blit(self._font_small.render("出道城市", True, c["muted"]), (16, lab_y))
            self._screen.blit(self._font_small.render("出道風格", True, c["muted"]), (16, lab_y + 86))

        for rect, label, _cb in self._choice_handlers:
            hover = rect.collidepoint(mouse_pos)
            bg = c["btn_hover"] if hover else c["btn"]
            pygame.draw.rect(self._screen, bg, rect, border_radius=6)
            pygame.draw.rect(self._screen, c["btn_border"], rect, width=1, border_radius=6)

            selected = False
            if self._session is None:
                city_labels = {d for _, d in self.CITIES}
                style_labels = {d for _, d in self.STYLES}
                if label in city_labels:
                    idx = next(i for i, (_, d) in enumerate(self.CITIES) if d == label)
                    selected = idx == self._start_city_idx
                elif label in style_labels:
                    idx = next(i for i, (_, d) in enumerate(self.STYLES) if d == label)
                    selected = idx == self._start_style_idx
            if selected:
                pygame.draw.rect(self._screen, c["accent"], rect, width=2, border_radius=6)

            display = label if len(label) <= 40 else label[:37] + "…"
            txt = self._font_btn.render(display, True, c["text"])
            tx = rect.x + 10
            ty = rect.y + (rect.height - txt.get_height()) // 2
            self._screen.blit(txt, (tx, ty))

        pygame.display.flip()

    def _handle_click(self, pos: tuple[int, int]) -> None:
        for rect, _label, cb in self._choice_handlers:
            if rect.collidepoint(pos):
                cb()
                break

    def run(self) -> None:
        """Run the main loop until the window is closed."""
        running = True
        while running:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)
                elif event.type == pygame.MOUSEWHEEL:
                    self._story_scroll -= event.y
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self._story_scroll -= 1
                    elif event.key == pygame.K_DOWN:
                        self._story_scroll += 1

            self._draw(mouse)
            self._clock.tick(60)

        pygame.quit()


def main() -> None:
    """Entry point for the pygame GUI."""
    GlobalStarPygameApp(seed=None).run()


if __name__ == "__main__":
    main()
