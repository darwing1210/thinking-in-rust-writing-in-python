#!/usr/bin/env python3
"""Build a 16:9 PPTX that Google Slides can import cleanly."""

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
MR = Inches(0.7)


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


def add_box(slide, left, top, width, height, fill: RGBColor | None = None):
    shape = slide.shapes.add_shape(1, left, top, width, height)  # rectangle
    if fill is None:
        shape.fill.background()
    else:
        rgb(shape, fill)
    no_line(shape)
    return shape


def add_text(slide, left, top, width, height) -> object:
    return slide.shapes.add_textbox(left, top, width, height)


def paragraph(
    tf,
    text: str,
    *,
    size: int,
    color: RGBColor,
    bold: bool = False,
    font: str = SANS,
    italic: bool = False,
    space_after: int = 6,
    align=None,
):
    p = (
        tf.paragraphs[0]
        if not tf.paragraphs[0].text
        and len(tf.paragraphs) == 1
        and tf.paragraphs[0].runs == []
        else tf.add_paragraph()
    )
    # First empty paragraph reuse is messy; always add_run on current last empty or new
    if (
        tf.paragraphs[0].text == ""
        and len(tf.paragraphs) == 1
        and not tf.paragraphs[0].runs
    ):
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align
    run = p.add_run()
    set_run(run, text, size=size, color=color, bold=bold, font=font, italic=italic)
    return p


def write_lines(tf, lines: list[tuple[str, dict]], *, first: bool = True):
    """lines: (text, kwargs for set_run + space_after)."""
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


def kicker_title(slide, kicker: str, title: str, *, title_size: int = 32) -> float:
    k = add_text(slide, ML, Inches(0.32), Inches(12), Inches(0.35))
    write_lines(
        k.text_frame,
        [(kicker.upper(), {"size": 13, "color": RUST, "bold": True, "space_after": 0})],
    )
    t = add_text(slide, ML, Inches(0.68), Inches(12), Inches(1.15))
    write_lines(
        t.text_frame,
        [
            (
                title,
                {"size": title_size, "color": INK, "font": DISPLAY, "space_after": 0},
            )
        ],
    )
    return 1.95


def code_block(slide, left, top, width, height, text: str, *, size: int = 14) -> None:
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
            or "include transportation" in line
            and "do not" not in line
        ):
            color = BAD
        if line.startswith("retryable:") or line.startswith("second topics do not"):
            color = OK
        if line.startswith("note:"):
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


def two_col_header(slide, left, top, width, title: str, muted: bool = False) -> None:
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
        [
            (
                "Python patterns for reliability",
                {"size": 22, "color": INK, "space_after": 0},
            )
        ],
    )
    desc = add_text(s, ML, Inches(4.2), Inches(11), Inches(0.8))
    write_lines(
        desc.text_frame,
        [
            (
                "Fewer runtime surprises, clearer error handling, and more confidence changing production code — without rewriting your app in Rust.",
                {"size": 15, "color": MUTED, "space_after": 0},
            )
        ],
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
    notes(s, "Pause on the title. Promise: no Rust required. Steal ideas, not syntax.")

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
            "You write Python at work — APIs, jobs, scripts.",
            "You have returned None and hoped the next person would know why.",
            "You have watched an AI write code that ran… and still felt weird about it.",
        ],
    )
    chrome(s)
    notes(
        s,
        "Hands: who shipped Python an agent wrote part of in six months? Nod. Do not count.",
    )

    # 3 agenda
    s = new_slide(prs)
    kicker_title(s, "40 minutes", "Three habits. Then we teach them to the AI.")
    rows = [
        ("4 min", "Why steal from Rust at all"),
        ("8 min", "Name the failure — don’t shrug with None"),
        ("9 min", "Don’t let a job be “done” and empty"),
        ("6 min", "Stop surprise edits in shared data"),
        ("9 min", "Write those habits down for your coding agent"),
        ("4 min", "What to steal this week, then questions"),
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
        "Map the 40 minutes. Same toy service throughout: article ingest, four fake URLs, no network.",
    )

    # 4 quote
    s = new_slide(prs)
    kicker_title(s, "Central message", "")
    q = add_text(s, ML, Inches(2.1), Inches(11.5), Inches(3.5))
    write_lines(
        q.text_frame,
        [
            (
                "You don’t need to write Rust. You can still steal the good parts. And if AI is writing your Python, you can teach it those parts too.",
                {"size": 28, "color": INK, "font": DISPLAY, "space_after": 0},
            )
        ],
    )
    chrome(s)
    notes(
        s, "Read the quote, then paraphrase. Python will not stop you. This is design."
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
            "Rust just makes them hard to ignore. That’s why we’re borrowing it tonight.",
            "You are not being asked to rewrite anything in Rust.",
            "And this matters for AI: models copy the repo. Clear habits in the code → better generated code. Messy habits → more mess.",
        ],
        size=20,
    )
    chrome(s)
    notes(s, "Forty seconds, then move. Smile. Rust is the teacher, not the religion.")

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
        '    if not article["title"]:\n'
        '        raise ValueError("title is required")\n'
        "    return article",
    )
    caption(
        s,
        6.05,
        "Missing article and timeout both come back as None. You cannot tell them apart.",
    )
    chrome(s)
    notes(s, "Let them read the code. Count to four. Three outcomes, two channels.")

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
            "It worked? That’s Ok. It didn’t? That’s Err. Both are normal return values.",
            "The next function has to look at which one it got.",
            "Rust makes you. Python won’t. We can still do it.",
        ],
        size=20,
    )
    chrome(s)
    notes(
        s, "Four lines of Rust. Do not teach lifetimes. Failure comes back as a value."
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
        "This is the whole framework. Named errors. match is the operations team in the source.",
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
    notes(s, "Run both commands. If demo fails, read the expected lines and move.")

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
    two_col_header(s, Inches(7.1), Inches(2.05), Inches(5.5), "Skip it", muted=True)
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
    chrome(s)
    notes(s, "Two dataclasses, not a Result library. Python still will not stop you.")

    # 11 p2 problem
    s = new_slide(prs)
    kicker_title(s, "Pattern 2  ·  Python problem", "This job can be “done” and empty.")
    code_block(
        s,
        ML,
        Inches(2.05),
        Inches(12),
        Inches(3.5),
        "@dataclass\n"
        "class Job:\n"
        "    job_id: str\n"
        "    url: str\n"
        '    status: str = "pending"\n'
        "    result: dict | None = None\n"
        "    error: str | None = None",
    )
    caption(
        s,
        5.75,
        "Python will let you complete a job with no result. And fail it with no error.",
    )
    chrome(s)
    notes(s, "complete(None) is legal. fail then complete leaves a stale error.")

    # 12 p2 rust
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 2  ·  Rust inspiration",
        "If it shouldn’t happen, don’t let the object exist.",
        title_size=26,
    )
    bullets(
        s,
        ML,
        Inches(2.15),
        Inches(12),
        Inches(3.4),
        [
            "Pending, running, done, failed — each is its own shape.",
            "Done always has the article. Failed always has the reason.",
            "No leftover fields from last week’s retry.",
        ],
    )
    caption(s, 5.8, "You already write int | str. Same idea, for a job.")
    chrome(s)
    notes(s, "Python everyday tools: frozen dataclasses plus a union plus match.")

    # 13 p2 solution
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 2  ·  Python solution",
        "Four shapes. Done always carries the article.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(1.95),
        Inches(5.8),
        Inches(4.7),
        "@dataclass(frozen=True)\n"
        "class Pending:\n"
        "    job_id: str\n"
        "    url: str\n"
        "\n"
        "@dataclass(frozen=True)\n"
        "class Completed:\n"
        "    job_id: str\n"
        "    article: Article\n"
        "\n"
        "@dataclass(frozen=True)\n"
        "class Failed:\n"
        "    job_id: str\n"
        "    error: IngestError\n"
        "\n"
        "type Job = Pending | Processing\n"
        "         | Completed | Failed",
        size=12,
    )
    code_block(
        s,
        Inches(6.8),
        Inches(1.95),
        Inches(5.9),
        Inches(4.7),
        "def finish(job, result):\n"
        "    match result:\n"
        "        case Ok(value):\n"
        "            return Completed(\n"
        "                job_id=job.job_id,\n"
        "                article=value,\n"
        "            )\n"
        "        case Err(error):\n"
        "            return Failed(\n"
        "                job_id=job.job_id,\n"
        "                error=error,\n"
        "            )",
        size=13,
    )
    chrome(s)
    notes(
        s,
        "Demo jobs before/after on missing URL. Before: completed + null. After: Failed NotFound.",
    )

    # 14 p2 tradeoffs
    s = new_slide(prs)
    kicker_title(s, "Pattern 2  ·  Trade-offs", "Life cycles yes. Nicknames no.")
    two_col_header(s, ML, Inches(2.05), Inches(5.8), "Use it")
    bullets(
        s,
        ML,
        Inches(2.5),
        Inches(5.8),
        Inches(3.5),
        [
            "Jobs, orders, payments — anything with a life cycle",
            "When “you shouldn’t read that field yet”",
        ],
    )
    two_col_header(s, Inches(7.1), Inches(2.05), Inches(5.5), "Skip it", muted=True)
    bullets(
        s,
        Inches(7.1),
        Inches(2.5),
        Inches(5.5),
        Inches(3.5),
        [
            "A nickname that really is optional",
            "A one-off parser you’ll throw away",
        ],
    )
    caption(
        s, 6.05, "Python still won’t yell like Rust. Keep the list of shapes small."
    )
    chrome(s)
    notes(s, "Keep the union small. Test each shape.")

    # 15 p3 problem
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 3  ·  Python problem",
        "We tagged the weather story as transportation.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(12),
        Inches(3.6),
        'SHARED_TOPICS: list[str] = ["news"]\n'
        "\n"
        "def enrich(article: dict) -> dict:\n"
        '    topics = article.setdefault("topics", SHARED_TOPICS)\n'
        '    if "bike" in body:\n'
        '        topics.append("transportation")\n'
        '    topics.append("ingested")\n'
        "    return article",
    )
    caption(
        s,
        5.85,
        "Two articles shared one list. The second one inherited the first one’s tags.",
    )
    chrome(s)
    notes(s, "Hands: test passed alone, failed in CI.")

    # 16 p3 rust
    s = new_slide(prs)
    kicker_title(
        s,
        "Pattern 3  ·  Rust inspiration",
        "Don’t edit the original. Return a new copy.",
        title_size=26,
    )
    code_block(
        s,
        ML,
        Inches(2.0),
        Inches(12),
        Inches(4.5),
        "@dataclass(frozen=True)\n"
        "class Article:\n"
        "    ...\n"
        "    topics: tuple[str, ...] = ()\n"
        "\n"
        "def tag_topics(article: Article) -> Article:\n"
        '    topics = ["news"]\n'
        '    if "bike" in article.body.lower():\n'
        '        topics.append("transportation")\n'
        "    return replace(article, topics=tuple(topics))",
        size=15,
    )
    chrome(s)
    notes(s, "Not teaching the borrow checker. Local list mutation is fine.")

    # 17 p3 demo
    s = new_slide(prs)
    kicker_title(s, "Pattern 3  ·  Demo", "Same pipeline. No leaked tags.")
    code_block(
        s,
        ML,
        Inches(2.05),
        Inches(12),
        Inches(3.2),
        "uv run python -m ingest pipeline --mode before\n"
        "second topics include transportation\n"
        "\n"
        "uv run python -m ingest pipeline --mode after\n"
        "second topics do not",
        size=16,
    )
    caption(
        s,
        5.55,
        "Freeze the values you pass around. A local list inside a function is still fine.",
    )
    chrome(s)
    notes(s, "Run pipeline before then after. Do not freeze every int.")

    # 18 agents
    s = new_slide(prs)
    kicker_title(s, "Agents", "The AI copies whatever you already do.")
    two_col_header(s, ML, Inches(2.05), Inches(5.8), "Ask it to “review this”")
    bullets(
        s,
        ML,
        Inches(2.5),
        Inches(5.8),
        Inches(3.8),
        [
            "Add a TypedDict",
            "Log the timeout",
            "Catch Exception",
            "Status Enum",
            "Keep returning None",
        ],
        size=18,
    )
    two_col_header(
        s, Inches(7.1), Inches(2.05), Inches(5.5), "The bugs are still there"
    )
    bullets(
        s,
        Inches(7.1),
        Inches(2.5),
        Inches(5.5),
        Inches(3.8),
        [
            "Timeout still looks like a 404",
            "Completed still needs no result",
            "Shared list still leaks",
        ],
        size=18,
    )
    caption(s, 6.15, "That’s a typical AI review: more types, more logs. Same shrugs.")
    chrome(s)
    notes(
        s, "Prepared demo, not live wifi. Agents complete the pattern in front of them."
    )

    # 19 skills
    s = new_slide(prs)
    kicker_title(
        s,
        "Skills",
        "Write the habit down. Then the agent can follow it.",
        title_size=26,
    )
    bullets(
        s,
        ML,
        Inches(2.15),
        Inches(12),
        Inches(4),
        [
            "skills/explicit-error-handling — name the failure",
            "skills/model-valid-states — don’t allow empty “done”",
            "skills/intentional-immutability — don’t share a list",
            "skills/python-design-review — and don’t gold-plate",
        ],
    )
    caption(s, 6.15, "A markdown file the agent reads first. That’s the whole trick.")
    chrome(s)
    notes(
        s,
        "Four SKILL.md files. Tests are the floor. Ceiling is whether timeout is a value.",
    )

    # 20 steal
    s = new_slide(prs)
    kicker_title(s, "Steal this", "Steal one of these this week.")
    bullets(
        s,
        ML,
        Inches(2.1),
        Inches(12),
        Inches(4.5),
        [
            "Notice a None that means two things.",
            "Give those failures names, if someone has to choose what to do next.",
            "Don’t let a job be “done” with nothing in it.",
            "If you change data, return a new copy.",
            "Write four lines in a SKILL.md so the AI does it too.",
            "Don’t trust “it ran.” Ask if the next person can misuse it.",
        ],
        size=18,
    )
    chrome(s)
    notes(s, "Not next quarter — one function this week.")

    # 21 close
    s = new_slide(prs)
    k = add_text(s, ML, Inches(1.5), Inches(12), Inches(0.35))
    write_lines(
        k.text_frame,
        [("ALAMO PYTHON", {"size": 13, "color": RUST, "bold": True, "space_after": 0})],
    )
    q = add_text(s, ML, Inches(2.1), Inches(11.8), Inches(2.6))
    write_lines(
        q.text_frame,
        [
            (
                "Better Python is not more code. It’s clearer decisions — and teaching the AI to make those with you.",
                {"size": 28, "color": INK, "font": DISPLAY, "space_after": 0},
            )
        ],
    )
    repo = add_text(s, ML, Inches(5.0), Inches(12), Inches(0.4))
    write_lines(
        repo.text_frame,
        [
            (
                "thinking-in-rust-writing-in-python",
                {"size": 16, "color": RUST, "font": MONO, "space_after": 0},
            )
        ],
    )
    cap = add_text(s, ML, Inches(5.5), Inches(12), Inches(0.5))
    write_lines(
        cap.text_frame,
        [
            (
                "Questions. Should you rewrite the whole app tomorrow? No. Pick one function.",
                {"size": 16, "color": MUTED, "space_after": 0},
            )
        ],
    )
    chrome(s)
    notes(s, "Read the quote. Repo name. MIT. No cloud. Pick one function. Questions.")

    prs.save(path)
    print(f"wrote {path} ({path.stat().st_size} bytes, {len(prs.slides)} slides)")


if __name__ == "__main__":
    out = Path(__file__).with_name("stealing-good-ideas-from-rust.pptx")
    build(out)
