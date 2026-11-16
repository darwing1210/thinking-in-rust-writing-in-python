#!/usr/bin/env python3
"""Build a 16:9 PPTX with 34 slides that Google Slides can import cleanly."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

BG = RGBColor.from_string("101012")
INK = RGBColor.from_string("F4F1EA")
MUTED = RGBColor.from_string("B7AEA6")
RUST = RGBColor.from_string("E85C36")
CODE_BG = RGBColor.from_string("0C0C0E")
CODE_INK = RGBColor.from_string("F0E6DC")
OK = RGBColor.from_string("FFDC48")
BAD = RGBColor.from_string("FF8A70")
LINE = RGBColor.from_string("3A2A26")

DISPLAY = "Georgia"
SANS = "Arial"
MONO = "Consolas"

W = Inches(13.333)
H = Inches(7.5)
ML = Inches(0.7)


def rgb(shape, color: RGBColor) -> None:
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color


def no_line(shape) -> None:
    shape.line.fill.background()


def set_run(
    run,
    text: str,
    *,
    size: int,
    color: RGBColor,
    bold: bool = False,
    font: str = SANS,
    italic: bool = False,
) -> None:
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font


def add_text(slide, left, top, width, height) -> object:
    return slide.shapes.add_textbox(left, top, width, height)


def write_lines(tf, lines: list[tuple[str, dict]]):
    started = False
    for text, kw in lines:
        space = kw.pop("space_after", 8)
        align = kw.pop("align", None)
        if not started:
            p = tf.paragraphs[0]
            started = True
        else:
            p = tf.add_paragraph()
        p.space_after = Pt(space)
        if align is not None:
            p.alignment = align
        run = p.add_run()
        set_run(run, text, **kw)


def notes(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text


def chrome(
    slide, footer: str = "Alamo Python  ·  Stealing good ideas from Rust"
) -> None:
    bar = slide.shapes.add_shape(1, Inches(0), Inches(7.42), W, Inches(0.08))
    rgb(bar, RUST)
    no_line(bar)
    box = add_text(slide, ML, Inches(7.12), Inches(10.5), Inches(0.28))
    write_lines(
        box.text_frame,
        [(footer, {"size": 11, "color": MUTED, "bold": True, "space_after": 0})],
    )


def kicker_title(
    slide, kicker: str, title: str, *, title_size: int = 30
) -> float:
    k = add_text(slide, ML, Inches(0.32), Inches(12), Inches(0.35))
    write_lines(
        k.text_frame,
        [
            (
                kicker.upper(),
                {"size": 13, "color": RUST, "bold": True, "space_after": 0},
            )
        ],
    )
    t = add_text(slide, ML, Inches(0.68), Inches(12), Inches(1.15))
    write_lines(
        t.text_frame,
        [
            (
                title,
                {
                    "size": title_size,
                    "color": INK,
                    "font": DISPLAY,
                    "space_after": 0,
                },
            )
        ],
    )
    return 1.95


def code_block(
    slide, left, top, width, height, text: str, *, size: int = 14
) -> None:
    bg = slide.shapes.add_shape(1, left, top, width, height)
    rgb(bg, CODE_BG)
    bg.line.color.rgb = LINE
    bg.line.width = Pt(1)
    box = add_text(
        slide,
        left + Inches(0.18),
        top + Inches(0.12),
        width - Inches(0.3),
        height - Inches(0.2),
    )
    tf = box.text_frame
    tf.word_wrap = True
    first = True
    for line in text.split("\n"):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(2)
        run = p.add_run()
        color = CODE_INK
        if (
            line.startswith("returned:")
            or line.startswith("error:")
            or "Cannot access attribute" in line
            or "include transportation" in line
            and "do not" not in line
        ):
            color = BAD
        if (
            line.startswith("retryable:")
            or line.startswith("second topics do not")
            or line.startswith("case Ok")
        ):
            color = OK
        if line.startswith("note:") or line.startswith("#"):
            color = MUTED
        set_run(run, line if line else " ", size=size, color=color, font=MONO)


def bullets(
    slide, left, top, width, height, items: list[str], *, size: int = 20
) -> None:
    box = add_text(slide, left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = 0
        p.space_after = Pt(10)
        run = p.add_run()
        set_run(run, item, size=size, color=INK)


def caption(slide, top: float, text: str) -> None:
    box = add_text(slide, ML, Inches(top), Inches(12), Inches(0.4))
    write_lines(
        box.text_frame, [(text, {"size": 14, "color": MUTED, "space_after": 0})]
    )


def two_col_header(
    slide, left, top, width, title: str, muted: bool = False
) -> None:
    box = add_text(slide, left, top, width, Inches(0.4))
    write_lines(
        box.text_frame,
        [
            (
                title,
                {
                    "size": 18,
                    "color": MUTED if muted else RUST,
                    "bold": True,
                    "space_after": 0,
                },
            )
        ],
    )


def new_slide(prs) -> object:
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG
    return slide


def build(path: Path) -> None:
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H

    # 1 title
    s = new_slide(prs)
    brand = add_text(s, ML, Inches(1.55), Inches(12), Inches(0.35))
    write_lines(
        brand.text_frame,
        [("ALAMO PYTHON", {"size": 14, "color": INK, "bold": True, "space_after": 0})],
    )
    title = add_text(s, ML, Inches(2.0), Inches(12), Inches(1.7))
    write_lines(
        title.text_frame,
        [
            (
                "Stealing good ideas from Rust",
                {"size": 44, "color": INK, "font": DISPLAY, "space_after": 0},
            )
        ],
    )
    lede = add_text(s, ML, Inches(3.7), Inches(12), Inches(0.45))
    write_lines(
        lede.text_frame,
        [("Python patterns for reliability", {"size": 22, "color": INK, "space_after": 0})],
    )
    desc = add_text(s, ML, Inches(4.2), Inches(11), Inches(0.8))
    write_lines(
        desc.text_frame,
        [(
            "Fewer runtime surprises, clearer error handling, and more confidence"
            " changing production code — without rewriting your app in Rust.",
            {"size": 15, "color": MUTED, "space_after": 0},
        )],
    )
    metas = [
        ("WHEN", "November 16\nMonday · 6:00–8:30 PM"),
        ("WHERE", "Geekdom\n110 E Houston St, 3rd Floor"),
        ("PARKING", "City Tower Garage\n60 N. Flores St"),
    ]
    for i, (lab, val) in enumerate(metas):
        left = ML + Inches(i * 3.9)
        lb = add_text(s, left, Inches(5.2), Inches(3.6), Inches(0.28))
        write_lines(
            lb.text_frame,
            [(lab, {"size": 12, "color": RUST, "bold": True, "space_after": 0})],
        )
        vb = add_text(s, left, Inches(5.48), Inches(3.6), Inches(0.9))
        first = True
        tf = vb.text_frame
        for line in val.split("\n"):
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(2)
            run = p.add_run()
            set_run(run, line, size=14, color=INK)
    chrome(s)
    notes(
        s,
        "Pause on the title. Promise: no Rust required. Steal ideas, not syntax.",
    )

    # 1a about me
    s = new_slide(prs)
    photo = path.parent / "speaker.jpg"
    s.shapes.add_picture(str(photo), ML, Inches(1.6), Inches(3.6), Inches(3.6))
    left = Inches(4.9)
    k = add_text(s, left, Inches(1.5), Inches(7.8), Inches(0.35))
    write_lines(k.text_frame, [("ABOUT ME", {"size": 13, "color": RUST, "bold": True, "space_after": 0})])
    t = add_text(s, left, Inches(1.9), Inches(7.8), Inches(0.8))
    write_lines(
        t.text_frame,
        [("Hi, I’m Darwing Medina.", {"size": 32, "color": INK, "font": DISPLAY, "space_after": 0})],
    )
    bullets(
        s,
        left,
        Inches(2.9),
        Inches(7.8),
        Inches(3.0),
        [
            (
                "Python Software Engineer at Handraise, based in Austin. We track"
                " what the news, social media, and AI models say about a brand."
            ),
            "Writing Python for work since 2016: Django, FastAPI, data pipelines, and AI.",
            "These days I review a lot of Python that an AI wrote. That’s how this talk started.",
            "Some of my work is written in Rust. You’ll hear why at the end.",
        ],
        size=18,
    )
    links = add_text(s, left, Inches(6.1), Inches(7.8), Inches(0.4))
    write_lines(
        links.text_frame,
        [("handraise.com  ·  github.com/darwing1210  ·  linkedin.com/in/dmedina93", {"size": 14, "color": MUTED, "space_after": 0})],
    )
    chrome(s)
    notes(s, "30–40 seconds. Keep it light. You'll talk about the Rust package at the end.")

    # 1b get the code (QR)
    s = new_slide(prs)
    kicker_title(s, "Follow along", "Get the code before we start.")
    bullets(
        s,
        ML,
        Inches(2.1),
        Inches(7.6),
        Inches(2.6),
        [
            "Slides, the full script, and every demo.",
            "Five agent skills you can copy.",
            "No cloud. No network. MIT.",
        ],
    )
    repo = add_text(s, ML, Inches(4.9), Inches(8.0), Inches(0.4))
    write_lines(
        repo.text_frame,
        [(
            "github.com/darwing1210/thinking-in-rust-writing-in-python",
            {"size": 15, "color": RUST, "font": MONO, "space_after": 0},
        )],
    )
    qr_img = path.parent / "repo-qr.png"
    s.shapes.add_picture(str(qr_img), Inches(8.9), Inches(1.7), Inches(3.8), Inches(3.8))
    qlab = add_text(s, Inches(8.9), Inches(5.6), Inches(3.8), Inches(0.4))
    write_lines(
        qlab.text_frame,
        [("SCAN FOR SLIDES, CODE & SKILLS", {"size": 12, "color": MUTED, "bold": True, "align": 2, "space_after": 0})],
    )
    chrome(s)
    notes(s, "20 seconds. Let people scan. Everything tonight is in the repo.")

    # 2 audience
    s = new_slide(prs)
    kicker_title(s, "Who this is for", "Python people. Not a Rust course.")
    bullets(
        s,
        ML,
        Inches(2.1),
        Inches(12),
        Inches(3.8),
        [
            "You write Python at work — APIs, jobs, pipelines.",
            "You have returned None and hoped the next person would know why.",
            (
                "You have watched an AI write code that ran… and still felt"
                " weird about it."
            ),
        ],
    )
    chrome(s)
    notes(
        s,
        "Hands: who shipped Python an agent wrote part of in six months? Nod."
        " Do not count.",
    )

    # 3 agenda
    s = new_slide(prs)
    kicker_title(
        s, "40 minutes", "Four habits. Then we teach them to AI."
    )
    rows = [
        ("5 min", "A short story: Rust’s playroom rules"),
        ("5 min", "1 · Errors — hand the failure back as a value"),
        ("5 min", "2 · Typestates — methods only exist when they make sense"),
        ("5 min", "3 · Contracts — NewType, assert_never, check data at the edge"),
        ("6 min", "4 · Ownership — one writer or many readers"),
        ("10 min", "AI agents, the type checker, and when I really write Rust"),
    ]
    for i, (t, d) in enumerate(rows):
        y = Inches(2.05) + Inches(i * 0.72)
        tb = add_text(s, ML, y, Inches(1.4), Inches(0.55))
        write_lines(
            tb.text_frame,
            [(t.upper(), {"size": 14, "color": RUST, "bold": True, "space_after": 0})],
        )
        db = add_text(s, Inches(2.3), y, Inches(10), Inches(0.55))
        write_lines(db.text_frame, [(d, {"size": 20, "color": INK, "space_after": 0})])
        line = s.shapes.add_shape(1, ML, y + Inches(0.52), Inches(11.8), Pt(1))
        rgb(line, LINE)
        no_line(line)
    chrome(s)
    notes(
        s,
        "Map the 40 minutes. Rust basics, four habits, then the AI part and a"
        " real story.",
    )

    # 4 quote
    s = new_slide(prs)
    kicker_title(s, "Central message", "")
    q = add_text(s, ML, Inches(2.1), Inches(11.5), Inches(3.5))
    write_lines(
        q.text_frame,
        [(
            "You don’t need to write Rust. You can still steal the good parts."
            " And if AI is writing your Python, you can teach it those parts"
            " too.",
            {"size": 28, "color": INK, "font": DISPLAY, "space_after": 0},
        )],
    )
    chrome(s)
    notes(
        s,
        "Read the quote, then paraphrase. Python will not stop you. This is"
        " design.",
    )

    # 5 disclaimer
    s = new_slide(prs)
    kicker_title(s, "Disclaimer", "These are not “Rust patterns.”")
    bullets(
        s,
        ML,
        Inches(2.1),
        Inches(12),
        Inches(4.2),
        [
            "They’re old design habits. Any language can use them.",
            (
                "Rust just makes them hard to ignore. That’s why we’re"
                " borrowing it tonight."
            ),
            "You are not being asked to rewrite anything in Rust.",
            (
                "And this matters for AI: models copy the repo. Clear habits"
                " in the code → better generated code. Messy habits → more"
                " mess."
            ),
        ],
        size=20,
    )
    chrome(s)
    notes(
        s,
        "Forty seconds, then move. Smile. Rust is the teacher, not the"
        " religion.",
    )

    # 5b storybook: Rust's playroom rules (full-slide pictures)
    story = [
        ("01-cover", "Set up the story. 30 seconds. Smile."),
        ("02-ownership", "One owner. Giving it away is a move. No copies, no secret remote control."),
        ("03-borrowing", "Looking = & borrow. Coloring = &mut borrow. This is the rule behind our weather bug later."),
        ("04-boxes", "Option and Result. Both come back in habit 1."),
        ("05-traits", "[cut] Traits. Optional page. Python's version is typing.Protocol."),
        ("06-door", "Bridge to the talk: Pyright is our babysitter. Next: habit 1."),
    ]
    from PIL import Image

    for img, note in story:
        s = new_slide(prs)
        pic = path.parent / "storybook" / f"{img}.jpg"
        with Image.open(pic) as im:
            ratio = im.width / im.height
        slide_ratio = W / H
        if ratio >= slide_ratio:
            pw, ph = W, int(W / ratio)
        else:
            pw, ph = int(H * ratio), H
        s.shapes.add_picture(str(pic), int((W - pw) / 2), int((H - ph) / 2), pw, ph)
        notes(s, note)

    # 6 p1 problem
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 1  ·  Python problem",
        "None means two things. An exception means a third.",
        title_size=28,
    )
    code_block(
        s,
        ML,
        Inches(2.05),
        Inches(12),
        Inches(3.85),
        "def ingest(url: str) -> dict | None:\n"
        "    try:\n"
        "        raw = fetch_raw(url)\n"
        "    except SourceTimeout:\n"
        "        return None\n"
        "    if raw is None:\n"
        "        return None\n"
        "    if not article[\"title\"]:\n"
        "        raise ValueError(\"title is required\")\n"
        "    return article",
    )
    caption(
        s,
        6.05,
        "Missing article and timeout both come back as None. You cannot tell"
        " them apart.",
    )
    chrome(s)
    notes(
        s,
        "Let them read the code. Count to four. Three outcomes, two channels.",
    )

    # 7 rust
    s = new_slide(prs)
    kicker_title(
        s, "Pattern 1  ·  Rust inspiration", "Don’t hide a failure. Hand it back."
    )
    code_block(
        s,
        ML,
        Inches(2.05),
        Inches(12),
        Inches(1.15),
        "fn ingest(url: &str) -> Result<Article, IngestError> { ... }",
    )
    bullets(
        s,
        ML,
        Inches(3.45),
        Inches(12),
        Inches(3),
        [
            (
                "It worked? That’s Ok. It didn’t? That’s Err. Both are normal"
                " return values."
            ),
            "The next function has to look at which one it got.",
            "Rust makes you. Python won’t. We can still do it.",
            (
                "Good news: with strict Pyright, Article | None already works"
                " like Rust’s Option. The problem is not None. It’s None meaning"
                " two things."
            ),
        ],
        size=19,
    )
    chrome(s)
    notes(
        s,
        "Four lines of Rust. Do not teach lifetimes. Failure comes back as a"
        " value.",
    )

    # 8 python solution two cols
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 1  ·  Python solution",
        "Two little classes, then match.",
        title_size=28,
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(5.8),
        Inches(4.4),
        "@dataclass(frozen=True)\n"
        "class Ok[T]:\n"
        "    value: T\n"
        "\n"
        "@dataclass(frozen=True)\n"
        "class Err[E]:\n"
        "    error: E\n"
        "\n"
        "type Result[T, E] = Ok[T] | Err[E]",
        size=13,
    )
    code_block(
        s,
        Inches(6.8),
        Inches(2.0),
        Inches(5.9),
        Inches(4.4),
        "match ingest(url):\n"
        "    case Ok(article):\n"
        "        save(article)\n"
        "    case Err(NotFound()):\n"
        "        record_miss()\n"
        "    case Err(ValidationFailed(f)):\n"
        "        record_invalid(f)\n"
        "    case Err(Retryable()):\n"
        "        schedule_retry()",
        size=13,
    )
    chrome(s)
    notes(
        s,
        "This is the whole framework. Named errors. match is the operations"
        " team in the source.",
    )

    # 9 demo
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 1  ·  Demo",
        "Same timeout. Now you can tell them apart.",
        title_size=28,
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(12),
        Inches(4.5),
        "uv run python -m ingest demo --mode before \\\n"
        "  --url https://news.example/timeout\n"
        "\n"
        "returned: None\n"
        "note: None means missing OR timeout.\n"
        "\n"
        "uv run python -m ingest demo --mode after \\\n"
        "  --url https://news.example/timeout\n"
        "\n"
        "retryable: timed out fetching https://news.example/timeout",
        size=15,
    )
    chrome(s)
    notes(
        s, "Run both commands. If demo fails, read the expected lines and move."
    )

    # 10 tradeoffs
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 1  ·  Trade-offs",
        "When this is worth it — and when it isn’t.",
        title_size=28,
    )
    two_col_header(s, ML, Inches(2.05), Inches(5.8), "Use it")
    bullets(
        s,
        ML,
        Inches(2.5),
        Inches(5.8),
        Inches(3.8),
        [
            "When “it failed” is not enough",
            "When someone has to retry, skip, or give up",
            "When you talk to the network",
        ],
    )
    two_col_header(
        s, Inches(7.1), Inches(2.05), Inches(5.5), "Skip it", muted=True
    )
    bullets(
        s,
        Inches(7.1),
        Inches(2.5),
        Inches(5.5),
        Inches(3.8),
        [
            "When you actually have a bug — just raise",
            "When the team already has one clear exception style",
            "A script you will delete on Friday",
        ],
    )
    caption(
        s,
        6.2,
        "Honest cost: Rust has ? to pass an error up in one character. Python"
        " doesn’t. Every layer needs its own match.",
    )
    chrome(s)
    notes(
        s, "Two dataclasses, not a Result library. Python still will not stop you."
    )

    # 11 p2 problem
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 2  ·  Python problem",
        "The form with extra boxes — and out-of-order methods.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(2.05),
        Inches(12),
        Inches(3.5),
        "@dataclass\n"
        "class Job:\n"
        "    status: str = \"pending\"\n"
        "    result: dict | None = None\n"
        "    error: str | None = None\n"
        "\n"
        "    def complete(self, result): ...  # Legal to call before start()!\n"
        "    def fail(self, error): ...",
    )
    caption(
        s,
        5.75,
        "You can complete a job before starting it. And you can complete it"
        " with no result.",
    )
    chrome(s)
    notes(
        s,
        "complete(None) is legal. Calling complete before start is legal."
        " Runtime bugs.",
    )

    # 12 p2 rust
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 2  ·  Rust inspiration",
        "The Typestate pattern: methods only exist when valid.",
        title_size=26,
    )
    bullets(
        s,
        ML,
        Inches(2.15),
        Inches(12),
        Inches(3.4),
        [
            (
                "In Rust, fn start(self) -> Processing uses up the old job. You"
                " can’t touch it again."
            ),
            (
                "You cannot call .finish() on a Pending job. The method does"
                " not exist."
            ),
            (
                "No runtime checks like if self.status != 'running': raise. It"
                " fails to compile."
            ),
        ],
    )
    caption(
        s,
        5.8,
        "Find the bug in your editor, not in a 3 AM alert.",
    )
    chrome(s)
    notes(
        s,
        "Typestates: methods only exist where valid. Rust uses up the old"
        " state; Python cannot. We gate methods, not moves.",
    )

    # 13 p2 solution
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 2  ·  Python solution",
        "Typestates: Pending has .start(), Processing has .finish().",
        title_size=24,
    )
    code_block(
        s,
        ML,
        Inches(1.95),
        Inches(5.8),
        Inches(4.7),
        "@dataclass(frozen=True)\n"
        "class Pending:\n"
        "    job_id: JobId\n"
        "    url: Url\n"
        "\n"
        "    def start(self) -> Processing:\n"
        "        return Processing(self.job_id, self.url)",
        size=12,
    )
    code_block(
        s,
        Inches(6.8),
        Inches(1.95),
        Inches(5.9),
        Inches(4.7),
        "@dataclass(frozen=True)\n"
        "class Processing:\n"
        "    job_id: JobId\n"
        "    url: Url\n"
        "\n"
        "    def finish(self, res) -> Completed | Failed:\n"
        "        match res:\n"
        "            case Ok(val):\n"
        "                return Completed(self.job_id, val)\n"
        "            case Err(err):\n"
        "                return Failed(self.job_id, err)",
        size=12,
    )
    chrome(s)
    notes(
        s,
        "Pending has no .finish() method. Calling it is a compile-time Pyright"
        " error.",
    )

    # 14 p2 demo
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 2  ·  Demo",
        "Pyright catches lifecycle errors before runtime.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(2.05),
        Inches(12),
        Inches(4.4),
        "job = Pending(job_id=JobId(\"j1\"), url=Url(\"https://news.example/ok\"))\n"
        "\n"
        "# Bug: trying to finish a pending job before starting it!\n"
        "job.finish(Err(NotFound(url=\"https://news.example/ok\")))\n"
        "\n"
        "error: Cannot access attribute \"finish\" for class \"Pending\"\n"
        "  Attribute \"finish\" is unknown",
        size=14,
    )
    caption(
        s,
        6.1,
        "An AI agent or coworker cannot call the wrong method. The compiler"
        " blocks it.",
    )
    chrome(s)
    notes(
        s,
        "Show Pyright catching cannot_finish_pending_job.py at compile time!",
    )

    # 15 p3 problem
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 3  ·  Python problem",
        "Swapped arguments and silent match fallthrough.",
        title_size=26,
    )
    two_col_header(s, ML, Inches(2.05), Inches(5.8), "1. Swapped string IDs")
    code_block(
        s,
        ML,
        Inches(2.55),
        Inches(5.8),
        Inches(2.8),
        "def fetch(url: str, job_id: str): ...\n"
        "\n"
        "# Bug: swapped arguments!\n"
        "fetch(my_job_id, my_url)",
        size=13,
    )
    caption(
        s,
        5.55,
        "Tests pass because both are str. Production silently corrupts.",
    )

    two_col_header(
        s, Inches(7.1), Inches(2.05), Inches(5.5), "2. Silent match fallthrough"
    )
    code_block(
        s,
        Inches(7.1),
        Inches(2.55),
        Inches(5.5),
        Inches(2.8),
        "match job:\n"
        "    case Pending(): ...\n"
        "    case Completed(): ...\n"
        "    # Forgot Processing & Failed!",
        size=13,
    )
    chrome(s)
    notes(
        s,
        "Primitive obsession & silent match fallthrough. Swapped strings and"
        " unhandled states.",
    )

    # 16 p3 solution
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 3  ·  Rust & Python solution",
        "Zero-cost NewType & compile-time assert_never.",
        title_size=24,
    )
    two_col_header(s, ML, Inches(2.05), Inches(5.8), "Zero-cost NewType")
    code_block(
        s,
        ML,
        Inches(2.55),
        Inches(5.8),
        Inches(3.3),
        "JobId = NewType(\"JobId\", str)\n"
        "Url = NewType(\"Url\", str)\n"
        "\n"
        "def fetch(url: Url, id: JobId): ...\n"
        "fetch(my_id, my_url)  # Pyright ERROR!",
        size=12,
    )

    two_col_header(
        s, Inches(7.1), Inches(2.05), Inches(5.5), "Exhaustive assert_never"
    )
    code_block(
        s,
        Inches(7.1),
        Inches(2.55),
        Inches(5.5),
        Inches(3.3),
        "match job:\n"
        "    case Pending(): ...\n"
        "    case Processing(): ...\n"
        "    case Completed(): ...\n"
        "    case Failed(): ...\n"
        "    case _ as unreachable:\n"
        "        assert_never(unreachable)",
        size=12,
    )
    caption(
        s,
        6.1,
        "Add Cancelled to Job union? Pyright breaks across CI until handled!",
    )
    chrome(s)
    notes(
        s,
        "NewType is zero-cost at runtime. assert_never breaks CI if a union"
        " case is missing.",
    )

    # 16b check at the edge
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 3  ·  The catch",
        "A type is a label. It does not check your data.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(5.0),
        Inches(3.9),
        "Url(\"not a url\")     # Pyright: fine.\n"
        "JobId(some_url)      # Pyright: fine.\n"
        "\n"
        "# Types trust you.\n"
        "# Data from outside\n"
        "# should not be trusted.",
        size=13,
    )
    code_block(
        s,
        Inches(5.9),
        Inches(2.0),
        Inches(6.8),
        Inches(3.9),
        "def parse_url(raw: str) -> Result[\n"
        "    Url, ValidationFailed\n"
        "]:\n"
        "    parts = urlsplit(raw.strip())\n"
        "    if parts.scheme not in (\"http\", \"https\"):\n"
        "        return Err(ValidationFailed((\"url\",)))\n"
        "    if not parts.netloc:\n"
        "        return Err(ValidationFailed((\"url\",)))\n"
        "    return Ok(Url(raw.strip()))",
        size=13,
    )
    caption(
        s,
        6.1,
        "Check once at the edge (HTTP, files, queues — Pydantic is great"
        " here). Inside the app, trust the type.",
    )
    chrome(s)
    notes(
        s,
        "NewType is a label, not a check. Check once at the edge, trust inside.",
    )

    # 17 p4 problem
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 4  ·  Python problem",
        "We tagged the weather story as transportation.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(12),
        Inches(3.6),
        "SHARED_TOPICS: list[str] = [\"news\"]\n"
        "\n"
        "def enrich(article: dict) -> dict:\n"
        "    topics = article.setdefault(\"topics\", SHARED_TOPICS)\n"
        "    if \"bike\" in body:\n"
        "        topics.append(\"transportation\")\n"
        "    topics.append(\"ingested\")\n"
        "    return article",
    )
    caption(
        s,
        5.85,
        "Two articles shared one list. The second one inherited the first"
        " one’s tags.",
    )
    chrome(s)
    notes(
        s,
        "setdefault aliases SHARED_TOPICS. Weather story tagged"
        " transportation. Aliasing XOR Mutability.",
    )

    # 17b ownership & borrowing
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 4  ·  Back to the playroom",
        "What the babysitter really says.",
        title_size=26,
    )
    two_col_header(s, ML, Inches(1.95), Inches(5.8), "1 · Leo drives the truck he gave away")
    code_block(
        s,
        ML,
        Inches(2.4),
        Inches(5.8),
        Inches(3.3),
        "let topics = vec![\"news\"];\n"
        "let a = topics;   // owner is now `a`\n"
        "println!(\"{:?}\", topics);\n"
        "\n"
        "error[E0382]: borrow of moved\n"
        "value: `topics`",
        size=13,
    )
    two_col_header(
        s, Inches(6.8), Inches(1.95), Inches(5.9), "2 · Someone colors while others look"
    )
    code_block(
        s,
        Inches(6.8),
        Inches(2.4),
        Inches(5.9),
        Inches(3.3),
        "let mut topics = vec![\"news\"];\n"
        "let reader = &topics;   // borrow to read\n"
        "topics.push(\"transportation\");\n"
        "println!(\"{:?}\", reader);\n"
        "\n"
        "error[E0502]: cannot borrow `topics`\n"
        "as mutable because it is also\n"
        "borrowed as immutable",
        size=13,
    )
    caption(
        s,
        5.9,
        "& = borrow to read (many at once). &mut = borrow to write (only one)."
        " Lifetimes: a borrow can’t live longer than the owner — like a"
        " Python with block.",
    )
    chrome(s)
    notes(
        s,
        "Two tiny compile errors. Move, then borrow. Lifetimes get one"
        " sentence only.",
    )

    # 18 p4 rust
    s = new_slide(prs)
    kicker_title(
        s, "Pattern 4  ·  The Ownership Rule", "Aliasing XOR Mutability."
    )
    q = add_text(s, ML, Inches(2.1), Inches(11.8), Inches(1.5))
    write_lines(
        q.text_frame,
        [(
            "You can have many shared readers, OR one exclusive writer. Never"
            " both.",
            {"size": 30, "color": INK, "font": DISPLAY, "space_after": 0},
        )],
    )
    bullets(
        s,
        ML,
        Inches(3.8),
        Inches(12),
        Inches(3.0),
        [
            (
                "Our weather bug is two kids coloring the same page. Rust"
                " refuses to compile it."
            ),
            (
                "If more than one part of your program can see an object, don’t"
                " change it in place."
            ),
            (
                "Private mutation inside a function is fine (no alias exists"
                " yet)."
            ),
            (
                "Fun fact: Python has a tiny runtime borrow check. Resize a"
                " bytearray while a memoryview holds it: BufferError."
            ),
        ],
        size=18,
    )
    chrome(s)
    notes(
        s,
        "Rust's Law: Aliasing XOR Mutability. Python's tiny runtime borrow check"
        " in memoryview (not compile-time).",
    )

    # 19 p4 solution
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 4  ·  Python solution & demo",
        "Don’t edit the original. Return a new copy.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(12),
        Inches(4.6),
        "@dataclass(frozen=True)\n"
        "class Article:\n"
        "    topics: tuple[str, ...] = ()  # Immutable published collection\n"
        "\n"
        "def tag_topics(article: Article) -> Article:\n"
        "    local_tags = [\"news\"]        # Private local mutation: totally fine!\n"
        "    if \"bike\" in article.body.lower():\n"
        "        local_tags.append(\"transportation\")\n"
        "    return replace(article, topics=tuple(local_tags))\n"
        "\n"
        "uv run python -m ingest pipeline --mode before  # leaked tags\n"
        "uv run python -m ingest pipeline --mode after   # isolated",
        size=13,
    )
    chrome(s)
    notes(
        s,
        "Frozen dataclass, tuples, dataclasses.replace. Pipeline before and"
        " after demo.",
    )

    # 20 agents
    s = new_slide(prs)
    kicker_title(
        s,
        "The AI Punchline",
        "The type checker keeps the agent on a leash.",
        title_size=28,
    )
    two_col_header(
        s, ML, Inches(2.05), Inches(5.8), "Sloppy Python (Dicts & None)"
    )
    bullets(
        s,
        ML,
        Inches(2.55),
        Inches(5.8),
        Inches(3.8),
        [
            "AI invents states that should not exist",
            "Swaps string arguments",
            "Forgets match branches",
            "Tests pass; production breaks",
        ],
        size=18,
    )
    two_col_header(
        s, Inches(7.1), Inches(2.05), Inches(5.5), "Rust-Inspired Python"
    )
    bullets(
        s,
        Inches(7.1),
        Inches(2.55),
        Inches(5.5),
        Inches(3.8),
        [
            "Typestates block invalid methods",
            "NewType blocks swapped IDs",
            "assert_never blocks forgotten cases",
            "AI self-corrects against Pyright before PR",
        ],
        size=18,
    )
    caption(
        s,
        6.15,
        "The agent reads the red error lines and fixes its own code.",
    )
    chrome(s)
    notes(
        s,
        "The real punchline: the compiler as the agent's leash. Strict types"
        " turn AI into a self-correcting coder.",
    )

    # 21 turn it on
    s = new_slide(prs)
    kicker_title(
        s, "Monday morning", "Turn the leash on. Three small steps.", title_size=28
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(5.8),
        Inches(4.6),
        "# 1. pyproject.toml\n"
        "[tool.pyright]\n"
        "typeCheckingMode = \"strict\"\n"
        "\n"
        "# 2. CI (or pre-commit)\n"
        "uv run pyright\n"
        "\n"
        "# 3. Agent instructions\n"
        "\"Before you finish, run\n"
        " uv run pyright and fix\n"
        " every error.\"",
        size=14,
    )
    two_col_header(s, Inches(7.1), Inches(2.0), Inches(5.5), "Five skills in the repo")
    bullets(
        s,
        Inches(7.1),
        Inches(2.5),
        Inches(5.5),
        Inches(3.2),
        [
            "explicit-error-handling",
            "model-valid-states",
            "type-driven-contracts",
            "intentional-immutability",
            "python-design-review",
        ],
        size=17,
    )
    caption(
        s,
        6.25,
        "Skills are markdown files the agent reads first. Claude Code, Cursor,"
        " Codex, Hermes.",
    )
    chrome(s)
    notes(
        s,
        "Three steps: strict config, CI, one line for the agent. Skills are in"
        " the repo.",
    )

    # 21b real rust
    s = new_slide(prs)
    kicker_title(
        s, "Real life", "When I do write Rust: the news firehose.", title_size=28
    )
    bullets(
        s,
        ML,
        Inches(2.0),
        Inches(6.4),
        Inches(4.2),
        [
            "A live stream of news articles comes in all day, every day.",
            "hr-firehose is a Rust service: it reads the stream, saves every article to S3, and indexes it for search.",
            "It never stops. So it has to be fast, small, and boring.",
            "Also in Rust: handytools, our URL clean-up package that Python calls through PyO3.",
            "The API, the jobs, the ML? Still Python.",
        ],
        size=15,
    )
    code_block(
        s,
        Inches(7.3),
        Inches(1.95),
        Inches(5.4),
        Inches(4.15),
        "// from hr-firehose (trimmed)\n"
        "async fn call_api(&self)\n"
        "    -> Result<Option<String>>\n"
        "{\n"
        "    let url = self.request_url()?;\n"
        "    let body = self.http.get(url)\n"
        "        .send().await\n"
        "        .context(\"request failed\")?\n"
        "        .text().await\n"
        "        .context(\"bad body\")?;\n"
        "    // ...\n"
        "    if no_articles {\n"
        "        return Ok(None);\n"
        "    }\n"
        "    // ...\n"
        "}",
        size=11,
    )
    caption(
        s,
        6.25,
        "Result of an Option: it can fail, and even when it works, there may be"
        " nothing new. Every ? passes the error up.",
    )
    chrome(s)
    notes(
        s,
        "Real story, 90 seconds. The firehose: a Rust service that never stops."
        " Result<Option<String>> and ? = the playroom rules, in production.",
    )

    # 22 steal
    s = new_slide(prs)
    kicker_title(
        s,
        "Steal this",
        "Six habits. Pick one function this week.",
        title_size=28,
    )
    bullets(
        s,
        ML,
        Inches(2.1),
        Inches(12),
        Inches(4.5),
        [
            "Hand failures back: stop using None for two different problems.",
            "Typestates: put each method only on the state where it makes sense.",
            "Label your IDs: NewType so you can’t swap them.",
            "Close every match: end it with assert_never.",
            "Check data at the edge: then trust the type inside.",
            (
                "One writer or many readers: change local data freely; don’t"
                " change shared data."
            ),
        ],
        size=17,
    )
    chrome(s)
    notes(s, "Six takeaways. Pick one function this week.")

    # 23 close
    s = new_slide(prs)
    k = add_text(s, ML, Inches(1.3), Inches(8), Inches(0.35))
    write_lines(
        k.text_frame,
        [("ALAMO PYTHON", {"size": 13, "color": RUST, "bold": True, "space_after": 0})],
    )
    q = add_text(s, ML, Inches(1.8), Inches(8.0), Inches(2.8))
    write_lines(
        q.text_frame,
        [(
            "Better Python is not more code. It’s clearer decisions — and"
            " giving our AI agents the mechanical guardrails to write safe"
            " software.",
            {"size": 26, "color": INK, "font": DISPLAY, "space_after": 0},
        )],
    )
    repo = add_text(s, ML, Inches(4.8), Inches(8.0), Inches(0.4))
    write_lines(
        repo.text_frame,
        [(
            "github.com/darwing1210/thinking-in-rust-writing-in-python",
            {"size": 15, "color": RUST, "font": MONO, "space_after": 0},
        )],
    )
    cap = add_text(s, ML, Inches(5.35), Inches(8.0), Inches(0.5))
    write_lines(
        cap.text_frame,
        [(
            "Questions. Should you rewrite the whole app tomorrow? No. Pick one"
            " boundary function.",
            {"size": 15, "color": MUTED, "space_after": 0},
        )],
    )
    # Add QR code on right
    qr_img = path.parent / "repo-qr.png"
    if qr_img.exists():
        s.shapes.add_picture(str(qr_img), Inches(9.1), Inches(1.8), Inches(3.4), Inches(3.4))
        qlab = add_text(s, Inches(9.1), Inches(5.35), Inches(3.4), Inches(0.4))
        write_lines(
            qlab.text_frame,
            [("SCAN FOR SLIDES & CODE", {"size": 12, "color": MUTED, "bold": True, "align": 1, "space_after": 0})],
        )
    chrome(s)
    notes(s, "Read the quote. Repo name. MIT. No cloud. Questions.")

    prs.save(path)
    print(f"wrote {path} ({path.stat().st_size} bytes, {len(prs.slides)} slides)")


if __name__ == "__main__":
    out = Path(__file__).with_name("stealing-good-ideas-from-rust.pptx")
    build(out)
