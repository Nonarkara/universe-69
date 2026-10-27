"""Capture the viewer at the three widths the design law requires.

    python3 tools/shoot.py [url] [--out DIR] [--tag NAME]

Reports what the page actually did — console errors, whether the canvases
contain pixels, and whether the document was considered hidden — alongside
the screenshots. A screenshot of a black canvas is not evidence of a render.
"""
import argparse
import os
import sys
import time

from playwright.sync_api import sync_playwright

WIDTHS = [(390, 844), (1024, 768), (1440, 900)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default="http://127.0.0.1:6971/")
    ap.add_argument("--out", default="/tmp/u69shots")
    ap.add_argument("--tag", default="viewer")
    ap.add_argument("--wait", type=float, default=6.0)
    ap.add_argument("--interact", action="store_true",
                    help="also drive the viewer: click a person, zoom, escape")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    errors = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            args=["--disable-dev-shm-usage", "--no-sandbox",
                  "--disable-background-timer-throttling",
                  "--disable-renderer-backgrounding"])
        try:
            for (w, h) in WIDTHS:
                ctx = browser.new_context(viewport={"width": w, "height": h},
                                          device_scale_factor=1)
                page = ctx.new_page()
                page.on("console", lambda m: errors.append(
                    f"[console.{m.type}] {m.text}") if m.type in ("error", "warning")
                    else None)
                page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))
                page.goto(args.url, wait_until="load", timeout=30000)
                page.wait_for_timeout(int(args.wait * 1000))

                info = page.evaluate("""() => {
                  var out = {hidden: document.hidden, canvases: []};
                  ['c6','c9'].forEach(function(id){
                    var cv=document.getElementById(id);
                    if(!cv){ out.canvases.push({id:id, missing:true}); return; }
                    var g=cv.getContext('2d');
                    var d=g.getImageData(0,0,cv.width,cv.height).data;
                    var nonblack=0, lit=0;
                    for(var i=0;i<d.length;i+=4*97){
                      if(d[i+3]>0 && (d[i]>8||d[i+1]>8||d[i+2]>8)) nonblack++;
                      lit++;
                    }
                    out.canvases.push({id:id, w:cv.width, h:cv.height,
                                       sampled:lit, nonblack:nonblack});
                  });
                  out.hud = (document.getElementById('hud6')||{}).innerHTML||'';
                  out.records = ((document.getElementById('reclines')||{}).innerHTML||'').length;
                  out.legend = ((document.getElementById('legend')||{}).innerHTML||'').length;
                  return out;
                }""")
                name = f"{args.tag}-{w}x{h}.png"
                path = os.path.join(args.out, name)
                page.screenshot(path=path)
                print(f"\n=== {w}x{h} -> {path}")
                print(f"    document.hidden = {info['hidden']}")
                for c in info["canvases"]:
                    if c.get("missing"):
                        print(f"    canvas {c['id']}: MISSING")
                    else:
                        pct = (100.0 * c["nonblack"] / max(1, c["sampled"]))
                        print(f"    canvas {c['id']}: {c['w']}x{c['h']} "
                              f"nonblack {pct:.1f}% of samples")
                print(f"    hud: {info['hud'][:120]}")
                print(f"    console rows: {info['records']}, legend chars: {info['legend']}")
                ctx.close()
        finally:
            browser.close()

    if errors:
        print("\n--- page errors ---")
        for e in errors[:30]:
            print("  " + e)
    else:
        print("\n--- no page errors ---")


def interact(url, out):
    """Prove the viewer answers to the hand: click a person, follow them."""
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome",
                                     args=["--disable-dev-shm-usage", "--no-sandbox"])
        try:
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(url, wait_until="load", timeout=30000)
            page.wait_for_timeout(5000)

            target = page.evaluate("""() => {
              var v=view.e; if(!v) return null;
              var cv=document.getElementById('c6');
              var r=cv.getBoundingClientRect();
              var dpr=cv.width/cv.clientWidth;
              var ids=Object.keys(actors6);
              for (var i=0;i<ids.length;i++){
                var a=actors6[ids[i]];
                // aim at the middle of the body, not at the feet
                var px=(a.x-v.sx)*v.ts+ v.ts/2, py=(a.y-0.7-v.sy)*v.ts;
                if (px<20||py<20||px>cv.width-20||py>cv.height-20) continue;
                return {id:a.id, x:r.left+px/dpr, y:r.top+py/dpr,
                        name:(state.u.eden.detail[String(a.id)]||[])[0],
                        act:a.act};
              }
              return null;
            }""")
            if not target:
                print("no person found to click")
                return
            print(f"\nclicking {target['name']} (id {target['id']}) at "
                  f"{target['x']:.0f},{target['y']:.0f}")
            page.mouse.click(target["x"], target["y"])
            page.wait_for_timeout(900)

            card = page.evaluate("""() => {
              var c=document.getElementById('card6');
              return {on: c.className.indexOf('on')>=0, text: c.innerText,
                      hud: document.getElementById('hud6').innerText,
                      mode: cam.e.mode, follow: cam.e.follow};
            }""")
            print(f"  camera mode : {card['mode']}  following id {card['follow']}")
            print(f"  card shown  : {card['on']}")
            print(f"  card text   : {card['text']!r}")
            print(f"  hud         : {card['hud']}")
            page.screenshot(path=os.path.join(out, "interact-follow.png"))

            # zoom with the wheel, then read the scale back
            before = page.evaluate("() => cam.e.h")
            page.mouse.move(700, 250)
            page.mouse.wheel(0, -600)
            page.wait_for_timeout(700)
            after = page.evaluate("() => cam.e.h")
            print(f"  wheel zoom  : half-height {before:.2f} -> {after:.2f}")
            page.screenshot(path=os.path.join(out, "interact-zoom.png"))

            # escape returns the eye to the documentary camera
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            mode = page.evaluate("() => cam.e.mode")
            print(f"  escape      : camera mode {mode}")
            if errors:
                print("  page errors: " + "; ".join(errors[:5]))
        finally:
            browser.close()


if __name__ == "__main__":
    import argparse as _a
    _p = _a.ArgumentParser(add_help=False)
    _p.add_argument("--interact", action="store_true")
    _p.add_argument("url", nargs="?", default="http://127.0.0.1:6971/")
    _known, _rest = _p.parse_known_args()
    if _known.interact:
        interact(_known.url, "/tmp/u69shots")
    main()
