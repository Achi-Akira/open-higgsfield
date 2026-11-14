import subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1]
CREAM = (250, 245, 232); GREEN = (31, 92, 64); LGREEN = (214, 232, 218)
INK = (34, 40, 36); MUTED = (110, 118, 112); RED = (196, 72, 60); WHITE = (255, 255, 255)
F = "/usr/share/fonts/truetype/dejavu/"
def font(sz, bold=True): return ImageFont.truetype(F + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)

# (duration seconds, scene id, spoken caption)
SCENES = [
    (5.0, 1, "Tired of paying for credit repair month after month—and still wondering what's actually changing?"),
    (3.5, 2, "What if you had a game plan to tackle it yourself?"),
    (7.0, 3, "The FTC says anything a credit repair company can legally do, you can do yourself for little or no cost."),
    (8.0, 4, "That's why I put together The Credit Comeback Blueprint—a self-guided digital guide with checklists, letter templates, and a ninety-day action plan."),
    (3.5, 5, "No magic promises. Just a clearer place to start."),
    (5.5, 6, "Let's get it done! Comment 'Let's Go' and I'll send you the link to check it out."),
]

def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3
def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def center(d, y, text, f, fill, maxw=920, gap=12):
    for ln in wrap(d, text, f, maxw):
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=fill)
        y += f.size + gap
    return y
def headline(d, text, t, y=230):
    a = ease(t / 0.5)
    col = tuple(int(CREAM[i] + (GREEN[i] - CREAM[i]) * a) for i in range(3))
    center(d, y + (1 - a) * 40, text, font(78), col)
def caption(d, text):
    f = font(38, False); lines = wrap(d, text, f, 900)
    h = len(lines) * 50 + 40; y0 = 1560
    d.rounded_rectangle((60, y0, W - 60, y0 + h), 28, fill=(255, 255, 255))
    y = y0 + 20
    for ln in lines:
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=INK); y += 50
def small(d, text, y, size=28):
    center(d, y, text, font(size, False), MUTED, maxw=960, gap=6)

def card(d, box, fill=WHITE, r=36):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), r, fill=(232, 225, 208))
    d.rounded_rectangle(box, r, fill=fill)

def s1(d, t):  # recurring charges
    headline(d, "Still paying every month?", t)
    card(d, (120, 520, 960, 1380))
    d.text((170, 570), "Recurring payments", font=font(44), fill=INK)
    for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun"]):
        a = ease((t - 0.4 - i * 0.35) / 0.4)
        if a <= 0: continue
        y = 680 + i * 110 + (1 - a) * 30
        d.line((170, y - 20, 910, y - 20), fill=(236, 232, 222), width=3)
        d.text((170, y), f"{m} — Credit service", font=font(38, False), fill=INK)
        d.text((790, y), "-$ ••", font=font(38), fill=RED)
def s2(d, t):  # checklist
    headline(d, "What if you had a plan?", t)
    card(d, (120, 520, 960, 1330))
    d.text((170, 570), "My game plan", font=font(44), fill=INK)
    for i, it in enumerate(["Pull all 3 reports", "Mark what looks wrong", "Send dispute letters", "Track every response"]):
        y = 690 + i * 150
        d.rounded_rectangle((170, y, 240, y + 70), 14, outline=GREEN, width=6)
        d.text((280, y + 8), it, font=font(42, False), fill=INK)
        a = ease((t - 0.5 - i * 0.55) / 0.3)
        if a > 0:
            d.line([(185, y + 36), (200 + 0 * a, y + 36 + 18 * a)], fill=GREEN, width=10)
            if a > 0.5:
                b = (a - 0.5) * 2
                d.line([(200, y + 54), (200 + 30 * b, y + 54 - 42 * b)], fill=GREEN, width=10)
def s3(d, t):  # FTC source card
    headline(d, "You can do it yourself.", t)
    a = ease((t - 0.3) / 0.6)
    off = (1 - a) * 120
    card(d, (100, 560 + off, 980, 1300 + off), fill=LGREEN)
    d.text((160, 640 + off), "FTC guidance, in short:", font=font(36), fill=GREEN)
    y = 730 + off
    for ln in wrap(d, "Anything a credit repair company can legally do, you can do yourself for little or no cost.", font(48, False), 760):
        d.text((160, y), ln, font=font(48, False), fill=INK); y += 64
    d.text((160, y + 30), "Source: FTC — Fixing Your Credit FAQs", font=font(32), fill=GREEN)
    d.text((160, y + 80), "FTC does not endorse this product.", font=font(30, False), fill=MUTED)
def book(d, x, y, w, h):
    d.rounded_rectangle((x + 14, y + 18, x + w + 14, y + h + 18), 18, fill=(200, 192, 172))
    d.rounded_rectangle((x, y, x + w, y + h), 18, fill=GREEN)
    d.rectangle((x, y, x + 26, y + h), fill=(22, 70, 48))
    yy = y + 110
    for ln in ["THE", "CREDIT", "COMEBACK", "BLUEPRINT"]:
        f = font(64 if ln != "THE" else 40)
        d.text((x + (w - d.textlength(ln, font=f)) / 2 + 10, yy), ln, font=f, fill=CREAM); yy += f.size + 18
    d.line((x + 110, yy + 20, x + w - 90, yy + 20), fill=CREAM, width=4)
    f = font(30, False)
    for ln in ["Checklists • Letter templates", "90-day action plan"]:
        d.text((x + (w - d.textlength(ln, font=f)) / 2 + 10, yy + 50), ln, font=f, fill=LGREEN); yy += 44
def s4(d, t):  # product reveal + page previews
    headline(d, "The Credit Comeback Blueprint", t, y=200)
    a = ease((t - 0.2) / 0.7); s = 0.85 + 0.15 * a
    w, h = int(560 * s), int(760 * s)
    book(d, (W - w) // 2, 430 + (760 - h) // 2, w, h)
    for i, lab in enumerate(["Checklist", "Letter", "90-day plan"]):
        b = ease((t - 2.5 - i * 0.9) / 0.5)
        if b <= 0: continue
        x = 110 + i * 300; y = 1240 + (1 - b) * 60
        d.rounded_rectangle((x, y, x + 260, y + 230), 16, fill=WHITE, outline=(222, 214, 196), width=3)
        d.text((x + 24, y + 22), lab, font=font(30), fill=GREEN)
        for k in range(4): d.line((x + 24, y + 80 + k * 34, x + 236 - (k % 2) * 50, y + 80 + k * 34), fill=(220, 220, 214), width=8)
    small(d, "Paid educational guide. DIY disputes are free.", 1480)
def s5(d, t):  # trackers
    headline(d, "Clear steps. Practical tools.", t)
    card(d, (120, 540, 960, 1300))
    d.text((170, 590), "90-day tracker", font=font(44), fill=INK)
    for i, lab in enumerate(["Days 1–30", "Days 31–60", "Days 61–90"]):
        y = 720 + i * 180
        d.text((170, y), lab, font=font(36, False), fill=INK)
        d.rounded_rectangle((170, y + 60, 910, y + 100), 20, fill=(236, 232, 222))
        a = ease((t - 0.4 - i * 0.6) / 0.8)
        if a > 0: d.rounded_rectangle((170, y + 60, 170 + max(40, int(740 * a * [1, .7, .45][i])), y + 100), 20, fill=GREEN)
def s6(d, t):  # CTA
    book(d, 310, 260, 460, 620)
    a = ease((t - 0.6) / 0.5); p = 1 + 0.04 * math.sin(t * 6) * (a >= 1)
    bw, bh = int(720 * a * p), int(220 * a * p)
    if bw > 10:
        x0, y0 = (W - bw) // 2, 1000 + (220 - bh) // 2
        d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 60, fill=GREEN)
        d.polygon([(x0 + 120, y0 + bh - 2), (x0 + 200, y0 + bh - 2), (x0 + 110, y0 + bh + 70 * a)], fill=GREEN)
        if a > 0.8:
            f = font(80); txt = "Comment LET'S GO"
            while d.textlength(txt, font=f) > bw - 120: f = font(f.size - 4)
            d.text(((W - d.textlength(txt, font=f)) / 2, y0 + (bh - f.size) / 2 - 6), txt, font=f, fill=CREAM)
    small(d, "Educational resource. Results vary. No score increase or deletion guaranteed.", 1350, 30)

FUNCS = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6}
total = sum(s[0] for s in SCENES)
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", str(total),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for dur, sid, cap in SCENES:
    for n in range(int(dur * FPS)):
        t = n / FPS
        img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
        FUNCS[sid](d, t)
        caption(d, cap)
        fade = min(1, t / 0.2, (dur - t) / 0.2)  # quick dip between scenes
        if fade < 1: img = Image.blend(Image.new("RGB", (W, H), CREAM), img, max(0, fade))
        proc.stdin.write(img.tobytes())
proc.stdin.close(); sys.exit(proc.wait())
