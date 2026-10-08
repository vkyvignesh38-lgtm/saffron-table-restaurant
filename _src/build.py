"""
Static site builder for the Saffron Table demo.

Shared pieces (header, drawer, footer, icons, dish data) live here once and are
stamped into every page, so the six pages stay identical in chrome.

    python _src/build.py

Writes the finished HTML pages to the project root.
"""
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGES = Path(__file__).resolve().parent / "pages"
IMG = ROOT / "assets" / "img"

# --------------------------------------------------------------------------
# Icons (24px line icons, stroke = currentColor)
# --------------------------------------------------------------------------
ICONS = {
    "leaf": '<path d="M5 19c0-8 5-14 15-15-1 10-7 15-15 15Z"/><path d="M5 19 14 10"/>',
    "book": '<path d="M6 4h10a2 2 0 0 1 2 2v14H8a2 2 0 0 1-2-2V4Z"/><path d="M6 18a2 2 0 0 1 2-2h10"/><path d="M10 8h5M10 11h4"/>',
    "pot": '<path d="M4 10h16v2.5a7.5 7.5 0 0 1-7.5 7.5h-1A7.5 7.5 0 0 1 4 12.5V10Z"/><path d="M2 10h20"/><path d="M9 6.5c0-1.2 1-1.6 1-3M13.5 6.5c0-1.2 1-1.6 1-3"/>',
    "lamp": '<path d="M4 12.5h16c-1 3.6-4 5.5-8 5.5s-7-1.9-8-5.5Z"/><path d="M12 18v3M9 21h6"/><path d="M12 3.5c1.7 1.9 2.1 3.4 1.3 4.8a1.5 1.5 0 0 1-2.6 0C9.9 6.9 10.3 5.4 12 3.5Z"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.2a4.3 4.3 0 0 1 7.5 2.6C19.5 15.4 12 20 12 20Z"/>',
    "family": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.2"/><path d="M15.6 14.2A4.5 4.5 0 0 1 21 18.6V20"/>',
    "phone": '<path d="M5 4h3l1.5 4-2 1.3a11 11 0 0 0 7.2 7.2l1.3-2L20 16v3a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1Z"/>',
    "chat": '<path d="M4 20l1.3-3.9A8 8 0 1 1 8 19Z"/><path d="M9 9.2c.2 2.9 2.9 5.6 5.8 5.8"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h10"/>',
    "prev": '<path d="m15 6-6 6 6 6"/>',
    "next": '<path d="m9 6 6 6-6 6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "map": '<path d="m9 4-5 2v14l5-2 6 2 5-2V4l-5 2-6-2Z"/><path d="M9 4v14M15 6v14"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r=".9" fill="currentColor" stroke="none"/>',
    "facebook": '<path d="M14.5 8H17V4.5h-2.5A3.5 3.5 0 0 0 11 8v2.5H8.5V14H11v6.5h3.5V14H17l.5-3.5h-3V8.5a.5.5 0 0 1 .5-.5Z"/>',
    "youtube": '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10.5 9.5 4 2.5-4 2.5v-5Z" fill="currentColor"/>',
}


def icon(name):
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
    )


# Kolam-inspired logo mark: a diamond of dots threaded by loops.
MARK = (
    '<svg class="brand__mark" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.4" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M24 6 42 24 24 42 6 24Z"/>'
    '<circle cx="24" cy="16.5" r="3.4"/><circle cx="31.5" cy="24" r="3.4"/>'
    '<circle cx="24" cy="31.5" r="3.4"/><circle cx="16.5" cy="24" r="3.4"/>'
    '<g fill="currentColor" stroke="none"><circle cx="24" cy="24" r="2"/>'
    '<circle cx="24" cy="2.5" r="1.3"/><circle cx="45.5" cy="24" r="1.3"/>'
    '<circle cx="24" cy="45.5" r="1.3"/><circle cx="2.5" cy="24" r="1.3"/></g></svg>'
)

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E"
    "%3Crect width='48' height='48' rx='12' fill='%2315120e'/%3E"
    "%3Cg fill='none' stroke='%23c9a24c' stroke-width='2'%3E%3Cpath d='M24 9 39 24 24 39 9 24Z'/%3E"
    "%3Ccircle cx='24' cy='17.5' r='3'/%3E%3Ccircle cx='30.5' cy='24' r='3'/%3E"
    "%3Ccircle cx='24' cy='30.5' r='3'/%3E%3Ccircle cx='17.5' cy='24' r='3'/%3E%3C/g%3E"
    "%3Ccircle cx='24' cy='24' r='2' fill='%23c9a24c'/%3E%3C/svg%3E"
)

NAV = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("menu.html", "Menu"),
    ("gallery.html", "Gallery"),
    ("reservation.html", "Reservation"),
    ("contact.html", "Contact"),
]

PHONE_DISPLAY = "+91 98765 43210"
PHONE_TEL = "tel:+919876543210"
WHATSAPP = "https://wa.me/919876543210"
EMAIL = "info@saffrontable.demo"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=Chennai%2C+Tamil+Nadu"

# --------------------------------------------------------------------------
# Dishes
# --------------------------------------------------------------------------
CATEGORIES = [
    ("starters", "Starters"),
    ("south-indian", "South Indian"),
    ("main-course", "Main Course"),
    ("biryani", "Biryani"),
    ("desserts", "Desserts"),
    ("beverages", "Beverages"),
]
CAT_NAME = dict(CATEGORIES)

DISHES = {
    "idli-sambar": dict(name="Idli Sambar", price=90, cat="south-indian", veg=True, spice=1,
        desc="Steamed rice and urad dal cakes, soft as cotton, with lentil sambar and fresh coconut chutney."),
    "medu-vada": dict(name="Medu Vada", price=90, cat="starters", veg=True, spice=1,
        desc="Crisp golden urad dal fritters with a fluffy centre, served with sambar and two chutneys."),
    "paneer-tikka": dict(name="Paneer Tikka", price=240, cat="starters", veg=True, spice=2,
        desc="Cottage cheese marinated in hung curd and spices, charred over high heat with peppers and onion."),
    "chettinad-chicken": dict(name="Chettinad Chicken", price=320, cat="main-course", veg=False, spice=3,
        desc="Slow-cooked in a freshly roasted masala of kalpasi, star anise and black pepper, Karaikudi style."),
    "mutton-biryani": dict(name="Mutton Biryani", price=360, cat="biryani", veg=False, spice=2,
        desc="Seeraga samba rice layered with tender mutton, mint and whole spices, sealed and dum-cooked."),
    "ghee-roast-dosa": dict(name="Ghee Roast Dosa", price=180, cat="south-indian", veg=True, spice=1,
        desc="A paper-thin dosa roasted crisp in pure ghee, with sambar and three house chutneys."),
    "rava-dosa": dict(name="Rava Dosa", price=160, cat="south-indian", veg=True, spice=1,
        desc="Lacy semolina crêpe with cumin, cracked pepper and curry leaves, crisp at every edge."),
    "gulab-jamun": dict(name="Gulab Jamun", price=90, cat="desserts", veg=True, spice=0,
        desc="Warm milk-solid dumplings soaked in cardamom and rose syrup. Two pieces per serving."),
    "filter-coffee": dict(name="Filter Coffee", price=60, cat="beverages", veg=True, spice=0,
        desc="Chicory-blend decoction with frothed hot milk, poured tall between dabara and tumbler."),
}
MENU_ORDER = ["idli-sambar", "medu-vada", "paneer-tikka", "chettinad-chicken", "mutton-biryani",
              "ghee-roast-dosa", "rava-dosa", "gulab-jamun", "filter-coffee"]
FEATURED = ["chettinad-chicken", "ghee-roast-dosa", "mutton-biryani", "filter-coffee"]


def size(img):
    with Image.open(IMG / f"{img}.jpg") as im:
        return im.size


def img_tag(name, alt, cls="", loading="lazy", sizes=None):
    w, h = size(name)
    c = f' class="{cls}"' if cls else ""
    s = f' sizes="{sizes}"' if sizes else ""
    return (f'<img{c} src="assets/img/{name}.jpg" alt="{alt}" width="{w}" height="{h}" '
            f'loading="{loading}" decoding="async"{s}>')


def diet(veg):
    if veg:
        return '<span class="diet diet--veg"><span class="diet__mark" aria-hidden="true"></span>Veg</span>'
    return '<span class="diet diet--nonveg"><span class="diet__mark" aria-hidden="true"></span>Non-Veg</span>'


def spice(level, cat):
    if level == 0:
        label = "Sweet" if cat == "desserts" else "Served hot"
        return f'<span>{label}</span>'
    dots = "".join('<i class="on"></i>' if i < level else "<i></i>" for i in range(3))
    words = {1: "Mild", 2: "Medium", 3: "Hot"}[level]
    return f'<span class="spice" title="Spice: {words}"><span class="sr-only">Spice level: {words}</span>{dots}</span>'


def dish_card(key):
    d = DISHES[key]
    return f"""
      <article class="dish" data-category="{d['cat']}">
        <div class="dish__media">
          {img_tag(key, d['name'])}
          <span class="dish__cat">{CAT_NAME[d['cat']]}</span>
        </div>
        <div class="dish__body">
          <div class="dish__top">
            <h3 class="dish__name">{d['name']}</h3>
            <span class="dish__price">₹{d['price']}</span>
          </div>
          <p class="dish__desc">{d['desc']}</p>
          <div class="dish__meta">{diet(d['veg'])}{spice(d['spice'], d['cat'])}</div>
        </div>
      </article>"""


def menu_filters():
    counts = {c: sum(1 for k in MENU_ORDER if DISHES[k]["cat"] == c) for c, _ in CATEGORIES}
    out = [f'<button class="chip" type="button" data-filter="all" aria-pressed="true">All<span class="count">{len(MENU_ORDER)}</span></button>']
    for slug, label in CATEGORIES:
        out.append(f'<button class="chip" type="button" data-filter="{slug}" aria-pressed="false">{label}<span class="count">{counts[slug]}</span></button>')
    return "\n        ".join(out)


# --------------------------------------------------------------------------
# Gallery
# --------------------------------------------------------------------------
GALLERY = [
    ("interior-main", "restaurant", "The main dining room", "Restaurant"),
    ("hero-dosa", "food", "Ghee roast dosa with chutneys", "Food"),
    ("chef-flame", "chef", "Tempering on a high flame", "Chef"),
    ("biryani-pot", "food", "Mutton biryani, dum-cooked", "Food"),
    ("dining-table", "dining", "An evening table, set and waiting", "Dining"),
    ("filter-coffee", "food", "Filter coffee in dabara and tumbler", "Food"),
    ("interior-warm", "restaurant", "Daylight through the front room", "Restaurant"),
    ("meals-thali", "dining", "South Indian meals, served together", "Dining"),
    ("chef-plating", "chef", "Finishing each plate by hand", "Chef"),
    ("idli-sambar", "food", "Idli on a fresh banana leaf", "Food"),
    ("interior-moody", "restaurant", "Lamp-lit evening service", "Restaurant"),
    ("curry-spread", "dining", "Curries and rice for the table", "Dining"),
]


def gallery_filters():
    cats = [("all", "All"), ("food", "Food"), ("restaurant", "Restaurant"), ("chef", "Chef"), ("dining", "Dining")]
    out = []
    for slug, label in cats:
        n = len(GALLERY) if slug == "all" else sum(1 for g in GALLERY if g[1] == slug)
        pressed = "true" if slug == "all" else "false"
        out.append(f'<button class="chip" type="button" data-filter="{slug}" aria-pressed="{pressed}">{label}<span class="count">{n}</span></button>')
    return "\n        ".join(out)


def gallery_tiles():
    out = []
    for i, (img, cat, cap, label) in enumerate(GALLERY):
        out.append(f"""
        <button class="tile" type="button" data-category="{cat}" data-index="{i}" data-src="assets/img/{img}.jpg" data-caption="{cap}" data-label="{label}" aria-label="Open photo: {cap}">
          {img_tag(img, cap)}
          <span class="tile__cap"><strong>{cap}</strong><span>{label}</span></span>
        </button>""")
    return "".join(out)


# --------------------------------------------------------------------------
# Chrome
# --------------------------------------------------------------------------
def header(active):
    links = "\n          ".join(
        f'<a class="nav__link" href="{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for href, label in NAV
    )
    drawer_links = "\n      ".join(
        f'<a class="drawer__link" href="{href}"{" aria-current=\"page\"" if href == active else ""}>{label}<span>0{i + 1}</span></a>'
        for i, (href, label) in enumerate(NAV)
    )
    return f"""<a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header" data-header>
    <div class="container site-header__inner">
      <a class="brand" href="index.html" aria-label="Saffron Table — home">
        {MARK}
        <span class="brand__text"><span class="brand__name">SAFFRON TABLE</span><span class="brand__tag">Authentic South Indian Cuisine</span></span>
      </a>
      <nav class="nav" aria-label="Primary">
          {links}
      </nav>
      <div class="header-actions">
        <a class="btn btn--gold btn--sm" href="reservation.html">Reserve a Table</a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu" data-drawer-open>{icon('menu')}</button>
      </div>
    </div>
  </header>

  <div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Site menu" inert>
    <div class="drawer__top">
      <a class="brand" href="index.html" aria-label="Saffron Table — home">
        {MARK}
        <span class="brand__text"><span class="brand__name">SAFFRON TABLE</span><span class="brand__tag">Authentic South Indian Cuisine</span></span>
      </a>
      <button class="icon-btn" type="button" aria-label="Close menu" data-drawer-close>{icon('close')}</button>
    </div>
    <nav class="drawer__nav" aria-label="Mobile">
      {drawer_links}
    </nav>
    <div class="drawer__foot">
      <a class="btn btn--gold btn--block" href="reservation.html">Reserve a Table</a>
      <div class="drawer__contact">
        <strong>{PHONE_DISPLAY}</strong>
        <span>24 Food Street, Chennai</span>
        <span>Mon–Fri 11:00 AM – 10:30 PM · Sat–Sun 10:00 AM – 11:00 PM</span>
      </div>
    </div>
  </div>"""


def footer(mobile_cta=True):
    quick = "\n            ".join(f'<li><a href="{h}">{l}</a></li>' for h, l in NAV)
    menu_links = "\n            ".join(
        f'<li><a href="menu.html#{slug}">{label}</a></li>'
        for slug, label in CATEGORIES if slug != "starters"
    )
    cta = ""
    if mobile_cta:
        cta = f"""
  <div class="mobile-cta">
    <a class="btn btn--ghost" href="{PHONE_TEL}" aria-label="Call Saffron Table">{icon('phone')}Call</a>
    <a class="btn btn--gold" href="reservation.html">Reserve a Table</a>
  </div>"""
    return f"""<footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a class="brand" href="index.html" aria-label="Saffron Table — home">
            {MARK}
            <span class="brand__text"><span class="brand__name">SAFFRON TABLE</span><span class="brand__tag">Authentic South Indian Cuisine</span></span>
          </a>
          <p>Tiffin, meals and slow-cooked curries from Tamil Nadu, Karnataka and Kerala, cooked fresh every day in Chennai.</p>
          <div class="socials">
            <a href="#" aria-label="Instagram (demo link)">{icon('instagram')}</a>
            <a href="#" aria-label="Facebook (demo link)">{icon('facebook')}</a>
            <a href="#" aria-label="YouTube (demo link)">{icon('youtube')}</a>
          </div>
        </div>
        <div>
          <h2 class="footer-title">Quick Links</h2>
          <ul class="footer-links">
            {quick}
          </ul>
        </div>
        <div>
          <h2 class="footer-title">Our Menu</h2>
          <ul class="footer-links">
            {menu_links}
          </ul>
        </div>
        <div class="newsletter">
          <h2 class="footer-title">Newsletter</h2>
          <p>Get updates on special menus and events.</p>
          <form class="newsletter__form" data-newsletter novalidate>
            <label class="sr-only" for="newsletter-email">Email address</label>
            <div class="newsletter__row">
              <input id="newsletter-email" name="email" type="email" placeholder="Your email address" autocomplete="email" required>
              <button class="btn btn--gold btn--sm" type="submit">Subscribe</button>
            </div>
            <p class="newsletter__msg" role="status" aria-live="polite"></p>
          </form>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2026 Saffron Table. Demo website created by Vignesh M.</p>
        <nav aria-label="Legal">
          <a href="legal.html#privacy">Privacy Policy</a>
          <a href="legal.html#terms">Terms of Service</a>
          <a href="legal.html#credits">Photo Credits</a>
        </nav>
      </div>
    </div>
  </footer>{cta}"""


def page(filename, title, description, body, active=None, mobile_cta=True):
    body_class = ' class="has-mobile-cta"' if mobile_cta else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#15120e">
  <link rel="icon" href="{FAVICON}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Manrope:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body{body_class}>
  {header(active or filename)}

  <main id="main">
{body}
  </main>

  {footer(mobile_cta)}

  <script src="assets/js/main.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Token replacement for page bodies
# --------------------------------------------------------------------------
def render(src):
    def sub(m):
        kind, _, arg = m.group(1).partition(":")
        if kind == "icon":
            return icon(arg)
        if kind == "dish":
            return dish_card(arg)
        if kind == "featured":
            return "".join(dish_card(k) for k in FEATURED)
        if kind == "menu":
            return "".join(dish_card(k) for k in MENU_ORDER)
        if kind == "menu-filters":
            return menu_filters()
        if kind == "gallery-filters":
            return gallery_filters()
        if kind == "gallery":
            return gallery_tiles()
        if kind == "img":
            name, alt, cls, *rest = arg.split("|")
            return img_tag(name, alt, cls, loading=rest[0] if rest else "lazy")
        if kind == "phone":
            return PHONE_DISPLAY
        if kind == "tel":
            return PHONE_TEL
        if kind == "whatsapp":
            return WHATSAPP
        if kind == "email":
            return EMAIL
        if kind == "mapurl":
            return MAP_URL
        raise KeyError(m.group(1))
    return re.sub(r"\[\[(.+?)\]\]", sub, src)


SITE = [
    # file, <title>, meta description, mobile sticky CTA?
    ("index.html", "Saffron Table — Authentic South Indian Cuisine in Chennai",
     "Saffron Table serves traditional South Indian food in Chennai: dosa, idli, Chettinad curries, biryani and filter coffee, made fresh daily.", True),
    ("about.html", "About Us — Saffron Table",
     "The story behind Saffron Table: family recipes, fresh ingredients and warm South Indian hospitality since 2009.", True),
    ("menu.html", "Menu — Saffron Table",
     "Explore the Saffron Table menu: starters, dosas, Chettinad curries, biryani, desserts and filter coffee.", True),
    ("gallery.html", "Gallery — Saffron Table",
     "A glimpse of the food, ambience and dining experience at Saffron Table.", True),
    ("reservation.html", "Reserve a Table — Saffron Table",
     "Request a table at Saffron Table in Chennai.", False),
    ("contact.html", "Contact — Saffron Table",
     "Call, WhatsApp, email or visit Saffron Table at 24 Food Street, Chennai.", True),
    ("legal.html", "Privacy, Terms & Credits — Saffron Table",
     "Privacy policy, terms of service and photo credits for the Saffron Table demo website.", True),
]


def main():
    for filename, title, desc, cta in SITE:
        body = render((PAGES / filename).read_text(encoding="utf-8"))
        active = None if filename == "legal.html" else filename
        html = page(filename, title, desc, body, active=active or "", mobile_cta=cta)
        (ROOT / filename).write_text(html, encoding="utf-8")
        print("built", filename)


if __name__ == "__main__":
    main()
