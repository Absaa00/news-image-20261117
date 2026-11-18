# The World in One Page — 17 November 2026

A make.fun entry for
[`news-image-20261117`](https://make.fun/bounty/news-image-20261117)
— "Sum up 17 November's world news in one image" ($250, top 50 share).

## What it is

`main.py` draws a 1024×1024 newspaper front page that summarises the
real world news of **Tuesday 17 November 2026**, using only the Python
standard library and Pillow. No network access, no downloaded assets:
every illustration (the Kerch Bridge, the Manila skyline, the tanker,
the bank, the rocket, the chip) is drawn with code, and every headline
is set from reporting published that day.

## The day's news

| Panel | Story |
|---|---|
| Top story | Kerch Bridge span collapses after a Ukrainian strike; Kyiv calls it an "unprecedented operation", Moscow vows to rebuild. |
| Diplomacy | Trump lands in Manila for the ASEAN summit; signs a joint trade statement with Thailand before talks with Xi and Putin. |
| Middle East | Two tankers hit mines in the Strait of Hormuz, Iran's Revolutionary Guards say; a third US carrier arrives in the region. |
| Markets | JPMorgan blames a software bug — not a cyberattack — for Monday's banking outage. |
| Space | ULA's Vulcan rocket fails ten minutes after lift-off; 40 Amazon Leo satellites lost. |
| Tech | Nvidia reports its first earnings since Jensen Huang's resignation. |
| Also today | Pentagon fails its financial audit for a ninth straight year; Gérard Depardieu admits a sexual assault charge; Japan scrambles jets after suspected Russian aircraft enter its airspace. |

Sources: BBC, AP, Reuters, Al Jazeera, ABC News, Just Security.

## Run it

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Requires Python 3.12+ and Pillow. The program is deterministic: two
runs write byte-identical PNGs (verified: same SHA-256). Output is a
1024×1024 PNG, about 110 KB — under the 1 MiB cap.

## License

MIT — see `LICENSE` (`SPDX-License-Identifier: MIT`).
