# Tip Calculator

A single-page tip calculator that runs entirely on the phone. No server, no
network, no accounts — all the math happens in the browser.

- **Bill total** — typed in, with a decimal keypad on mobile
- **Tip percentage** — slider, 5–30%
- **Split between** — slider, 1–10 people
- **Results** — bill, tip, total, plus tip each and total each

Bill, tip, split and currency are remembered between visits (`localStorage`).
When per-person amounts can't divide evenly to the cent, a line under the
results says how far off the split lands, rather than quietly hiding the
difference.

## Getting it onto the phone

**Option A — host it (recommended, installs as an app).**
Put `index.html`, `manifest.json`, `sw.js` and the three `icon-*.png` files on
any static host (GitHub Pages, Netlify, iCloud/Dropbox public link, etc.), open
the URL on the phone, then:

- **iOS Safari** — Share → *Add to Home Screen*
- **Android Chrome** — menu → *Install app* / *Add to Home screen*

It then launches full-screen with its own icon, and the service worker keeps it
working with no signal at all after the first load.

**Option B — just the file.** AirDrop or email `index.html` to the phone and
open it. Everything works except home-screen install and the offline cache
(service workers only run over http/https), which don't matter if you're
opening the file locally anyway.

## Running it here

```bash
python3 -m http.server 8123
```

Then open http://localhost:8123. To reach it from a phone on the same Wi-Fi,
use the Mac's LAN address instead of `localhost` — note that iOS only offers
*Add to Home Screen* as a true installed app over https, so Option A above is
the better route for daily use.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole app — markup, styles and logic in one file |
| `manifest.json` | Name, colors and icons for home-screen install |
| `sw.js` | Offline cache (HTML network-first, assets cache-first) |
| `icon-180/192/512.png` | Home-screen and install icons |

## Notes

- Light and dark themes follow the phone's system setting.
- Currency is a display symbol only; there is no conversion.
- To change the tip range, edit the `min`/`max` on the `#tip` range input in
  `index.html`; same for `#split`.
- After editing, bump `CACHE` in `sw.js` (e.g. `tip-app-v3`) so installed
  copies drop their old cached assets.
