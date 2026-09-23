"""Genera los SVG del README de perfil con la estética del portfolio."""
import base64, io, math, os, random
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, '..', 'package', 'dist', 'fonts')
OUT = os.path.join(HERE, '..', 'github-profile', 'assets')
os.makedirs(OUT, exist_ok=True)

CHARS = ''.join(chr(c) for c in range(32, 127)) + '·°′↗—–'

def font_b64(path):
    f = TTFont(path)
    opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['kern']
    s = subset.Subsetter(opts); s.populate(text=CHARS); s.subset(f)
    buf = io.BytesIO(); f.flavor = 'woff2'; f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()

SANS_L = font_b64(os.path.join(PKG, 'geist-sans', 'Geist-Light.woff2'))
SANS_R = font_b64(os.path.join(PKG, 'geist-sans', 'Geist-Regular.woff2'))
MONO = font_b64(os.path.join(PKG, 'geist-mono', 'GeistMono-Regular.woff2'))

def fonts(light=True, regular=True):
    css = []
    if light: css.append(f"@font-face{{font-family:G;font-weight:300;src:url(data:font/woff2;base64,{SANS_L}) format('woff2')}}")
    if regular: css.append(f"@font-face{{font-family:G;font-weight:400;src:url(data:font/woff2;base64,{SANS_R}) format('woff2')}}")
    css.append(f"@font-face{{font-family:GM;src:url(data:font/woff2;base64,{MONO}) format('woff2')}}")
    return '\n'.join(css)

BASE_CSS = """
.sans{font-family:G,system-ui,sans-serif}
.mono{font-family:GM,ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;fill:rgba(233,231,227,.56)}
.dim{fill:rgba(233,231,227,.44)}
.fg{fill:#e9e7e3}
.line{stroke:rgba(233,231,227,.14);fill:none}
.line2{stroke:rgba(233,231,227,.32);fill:none}
.corner{stroke:rgba(233,231,227,.56);fill:none}
"""

def corners(x, y, w, h, s=7, cls='corner'):
    return (f'<path class="{cls} c-tl" d="M{x+.5} {y+s+.5}V{y+.5}H{x+s+.5}"/>'
            f'<path class="{cls} c-br" d="M{x+w-.5} {y+h-s-.5}V{y+h-.5}H{x+w-s-.5}"/>')

def cross(x, y):
    return f'<path class="line2" d="M{x} {y-5.5}v11M{x-5.5} {y}h11"/>'

def esc(t): return t.replace('&', '&amp;').replace('<', '&lt;')

ARROW = '<path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="#e9e7e3" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'

SIGNATURE = [
    ('M382.218273,467.985874c-15.76364,29.80424-37.399993,94.871833-29.012738,105.053658', 0, 1),
    ('M302.404296,495.523376c-2.403052-1.750093-3.194671-7.345106,1.525801-11.290923c28.693217-20.760529,89.998113-39.090413,117.86358-36.008885c29.223569,0,50.316239,28.7063,29.223569,62.493981-15.845142,33.290043-73.495215,71.927855-100.092501,83.677685-31.65106,10.178918-46.994648-7.702476-12.511562-23.802485c25.923524-11.51048,70.801483-29.758481,90.632539-35.093407c17.182692-4.069006,44.902835-24.382438,55.844291-39.975966c10.39009-12.704144,25.531846-36.214321,27.109985-47.299811c4.666282-20.838115-2.26602-26.362547-15.819063-5.798042-23.807227,37.966762-33.682389,103.744724-30.210847,116.876303.26986,19.19766,16.143801,24.498331,31.431487,11.290921l26.243765-30.516006', .2, 2),
    ('M573.102141,477.95477c38.922512-36.062537,33.757783-49.756955-19.901093-20.730306-41.201052,20.730306-69.326914,55.785923-9.535942,69.653827c37.291063,9.638015,46.32741,37.742563,19.901092,55.971823-39.92086,22.287958-78.676187,0-17.828063-30.266246c26.163013-11.720704,60.568733-29.611372,156.306502-23.217942', .4, 2),
]

def orb(cx, cy, r, n=520, seed=7):
    """Orbe de partículas estático (proyección de una esfera de Fibonacci) con leve deriva."""
    random.seed(seed)
    ga = math.pi * (3 - math.sqrt(5))
    front, back = [], []
    for i in range(n):
        y = 1 - 2 * (i + .5) / n
        rr = math.sqrt(1 - y * y)
        th = ga * i
        x, z = math.cos(th) * rr, math.sin(th) * rr
        # inclinación
        t = .35
        y2, z2 = y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t)
        px, py = cx + x * r, cy + y2 * r
        a = .12 + .7 * (z2 + 1) / 2
        rad = .6 + .9 * (z2 + 1) / 2
        dot = f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rad:.2f}" fill-opacity="{a:.2f}"/>'
        (front if z2 > 0 else back).append(dot)
    def layer(dx, color, op):
        return f'<use href="#pts" fill="{color}" opacity="{op}" transform="translate({dx} 0)"/>'
    pts = f'<defs><g id="pts">{"".join(back + front)}</g></defs>'
    return (pts + f'<g class="orb">'
            f'<circle cx="{cx}" cy="{cy}" r="{r*1.25}" fill="url(#glow)"/>'
            + layer(-1.6, '#ff3b2f', .35) + layer(1.6, '#2fd6ff', .35)
            + layer(0, '#e9e7e3', 1) + '</g>')

# ---------------------------------------------------------------- cabecera
def header():
    W, H = 1200, 360
    sig = ''.join(
        f'<path d="{d}" pathLength="1" transform="translate(-264.52,-422.18)" '
        f'style="animation-delay:{.35+s:.2f}s;animation-duration:{dur*1.25:.2f}s"/>'
        for d, s, dur in SIGNATURE)
    css = fonts() + BASE_CSS + """
.sig path{fill:none;stroke:rgba(233,231,227,.86);stroke-width:5.5;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2s cubic-bezier(.65,0,.35,1) forwards}
@keyframes draw{0%{stroke-dashoffset:1;opacity:0}4%{opacity:1}100%{stroke-dashoffset:0;opacity:1}}
.dot{animation:blink 2.4s steps(1) infinite}
@keyframes blink{50%{opacity:.2}}
.orb{transform-origin:935px 150px;animation:breathe 6s ease-in-out infinite}
@keyframes breathe{50%{transform:scale(1.03)}}
.name{font-weight:300;font-size:46px;letter-spacing:-.03em}
.ab{animation:ab 7s steps(1) infinite}
@keyframes ab{0%,92%,100%{opacity:0}93%,96%{opacity:.75}}
.rise{animation:rise 1s cubic-bezier(.2,.8,.2,1) both}
@keyframes rise{from{opacity:0;transform:translateY(8px)}}
"""
    g = 28
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><style>{css}</style>
<radialGradient id="glow"><stop offset="0" stop-color="#e9e7e3" stop-opacity=".07"/><stop offset="1" stop-color="#e9e7e3" stop-opacity="0"/></radialGradient>
<clipPath id="clip"><rect x="0" y="0" width="{W}" height="{H}"/></clipPath></defs>
<rect width="{W}" height="{H}" fill="#0b0b0b"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" class="line"/>{corners(0, 0, W, H, 10)}
<g clip-path="url(#clip)">{orb(935, 150, 104)}</g>
<path class="line" d="M{g} 64H{W-g}M{g} {H-96}H{W-g}"/>
{cross(g, 64)}{cross(W-g, 64)}{cross(g, H-96)}{cross(W-g, H-96)}
<g class="sig" transform="translate({g-8} 2) scale(.26)">{sig}</g>
<text class="mono" x="{W/2}" y="40" text-anchor="middle">N 40°25′ · W 03°42′ — Barcelona</text>
<g class="mono"><circle class="dot" cx="{W-g-150}" cy="36" r="3" fill="#e9e7e3"/><text x="{W-g}" y="40" text-anchor="end">Available · Q4 2026</text></g>
<g class="rise">
<text class="sans name ab" x="{g-1.5}" y="{H-40}" fill="rgba(255,59,47,.9)">Diego Lajusticia</text>
<text class="sans name ab" x="{g+1.5}" y="{H-40}" fill="rgba(47,214,255,.9)">Diego Lajusticia</text>
<text class="sans name fg" x="{g}" y="{H-40}">Diego Lajusticia <tspan class="dim">/ Software Developer</tspan></text>
</g>
<text class="mono" x="{W-g}" y="{H-58}" text-anchor="end">dlsdevstudio@gmail.com</text>
<text class="mono dim" x="{W-g}" y="{H-40}" text-anchor="end">Web · Mobile · CLI · WebGL</text>
</svg>'''

# ---------------------------------------------------------------- tarjetas
def card(i, total, p):
    W, H = 400, 104
    delay = i * 1.3
    css = fonts(light=False) + BASE_CSS + f"""
.t{{font-weight:400;font-size:21px;letter-spacing:-.02em}}
.ab{{opacity:0;animation:ab 8s {delay:.1f}s infinite}}
@keyframes ab{{0%,86%,100%{{opacity:0}}88%,95%{{opacity:.7}}}}
.edge{{opacity:0;animation:ab 8s {delay:.1f}s infinite}}
.c-tl,.c-br{{animation:c 8s {delay:.1f}s infinite}}
.c-tl{{--d:-3px}}.c-br{{--d:3px}}
@keyframes c{{0%,86%,100%{{transform:none;stroke:rgba(233,231,227,.56)}}88%,95%{{transform:translate(var(--d),var(--d));stroke:#e9e7e3}}}}
"""
    x0, y0, w, h = 4, 4, W - 8, H - 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><style>{css}</style></defs>
<rect x="{x0+.5}" y="{y0+.5}" width="{w-1}" height="{h-1}" fill="#0b0b0b" class="line"/>
<path class="edge" stroke="rgba(255,59,47,.55)" d="M{x0-.5} {y0}V{y0+h}"/><path class="edge" stroke="rgba(47,214,255,.55)" d="M{x0+w+.5} {y0}V{y0+h}"/>
{corners(x0, y0, w, h)}
<text class="mono" x="{x0+14}" y="{y0+24}">{i+1:02d} / {total:02d}</text>
<text class="mono" x="{x0+w-14}" y="{y0+24}" text-anchor="end">{p["year"]}</text>
<text class="sans t ab" x="{x0+12.5}" y="{y0+54}" fill="rgba(255,59,47,.8)">{esc(p["title"])}</text>
<text class="sans t ab" x="{x0+15.5}" y="{y0+54}" fill="rgba(47,214,255,.8)">{esc(p["title"])}</text>
<text class="sans t fg" x="{x0+14}" y="{y0+54}">{esc(p["title"])}</text>
<text class="mono dim" x="{x0+14}" y="{y0+h-14}">{esc(p["tags"])}</text>
<g transform="translate({x0+w-28} {y0+h-28})">{ARROW}</g>
</svg>'''

# ---------------------------------------------------------------- botones
def button(label, name, w=None):
    w = w or int(len(label) * 7.9 + 64)
    H = 40
    css = fonts(light=False, regular=False) + BASE_CSS
    return name, f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}">
<defs><style>{css}</style></defs>
<rect x="3.5" y="3.5" width="{w-7}" height="{H-7}" fill="#0b0b0b" class="line2"/>
{corners(3, 3, w-6, H-6, 6, 'corner')}
<text class="mono fg" x="18" y="24.5" style="fill:#e9e7e3">{esc(label)}</text>
<g transform="translate({w-30} 13) scale(.875)">{ARROW}</g>
</svg>'''

def divider(label, count=None, W=808):
    css = fonts(light=False, regular=False) + BASE_CSS
    right = f'<text class="mono" x="{W}" y="16" text-anchor="end">{count}</text>' if count else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="28" viewBox="0 0 {W} 28">
<defs><style>{css}</style></defs>
<text class="mono" x="2" y="16">{esc(label)}</text>{right}
<path class="line" d="M0 26.5H{W}"/>
</svg>'''

PROJECTS = [
    dict(slug='assetly', title='Assetly', year='2024', tags='Asset & Ticket Management'),
    dict(slug='fragmint', title='Fragmint', year='2026', tags='Snippet Manager'),
    dict(slug='kodice', title='Kodice', year='2026', tags='TCG Collection Manager'),
    dict(slug='preflop-labs', title='Preflop Labs', year='2026', tags='Study Poker'),
    dict(slug='lazy-docs', title='Lazy Docs', year='2025', tags='Docs'),
]

def write(name, svg):
    with open(os.path.join(OUT, name), 'w') as f: f.write(svg)
    print(f'{name:28s} {len(svg)/1024:6.1f} KB')

write('header.svg', header())
for i, p in enumerate(PROJECTS):
    write(f'card-{p["slug"]}.svg', card(i, len(PROJECTS), p))
for label, name in [('Portfolio', 'btn-portfolio.svg'), ('Email', 'btn-email.svg'), ('GitHub', 'btn-github.svg')]:
    write(*button(label, name))
write('div-projects.svg', divider('Index — Selected work', f'{len(PROJECTS):02d} projects'))
write('div-stack.svg', divider('Stack'))
