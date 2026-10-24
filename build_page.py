"""Turn each page.md into the index.html next to it.

Edit the text in page.md (Markdown: # heading, ## smaller heading, - list item, **bold**,
*italic*, [link text](address), --- for a line across). Then run, from this folder:

    python build_page.py

and reload the page. index.html is written by this script: edit page.md, not index.html.

{download} in page.md is where the download link and password box go. Text on the same line
after it is shown in grey: {download} *(29 cards for now)*. The link fetches the one
locked deck (.apkg.enc) in the same folder, whatever its name.

Pages are found one or two folders down (eastern-central-arrernte/page.md,
eastern-central-arrernte/unpublished/page.md). A page in a folder named "unpublished" is for the
deck owner only: nothing links to it, and it asks search engines not to list it.

Needs the markdown package: python -m pip install markdown
"""
import glob
import html
import os
import re
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{title}">{robots}
<!-- Written by build_page.py from page.md: edit page.md, then run python build_page.py -->
<style>
  :root {{
    color-scheme: dark;
    --bg: #0d1117;
    --text: #f0f6fc;
    --muted: #9198a1;
    --border: #3d444d;
    --link: #4493f8;
  }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
  }}
  main {{ max-width: 830px; margin: 0 auto; padding: 32px 16px 48px; }}
  h1, h2 {{ font-weight: 600; line-height: 1.25; padding-bottom: 0.3em; border-bottom: 1px solid var(--border); }}
  h1 {{ font-size: 2em; margin: 0 0 16px; }}
  h2 {{ font-size: 1.5em; margin: 24px 0 16px; }}
  h3 {{ font-size: 1.25em; font-weight: 600; margin: 24px 0 16px; }}
  p, ol, ul {{ margin: 0 0 16px; }}
  ol, ul {{ padding-left: 2em; }}
  li + li {{ margin-top: 0.25em; }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  hr {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}
  .muted, .download em {{ color: var(--muted); font-style: normal; }}
  form {{ margin: 0 0 16px; }}
  label {{ display: block; margin-bottom: 4px; }}
  input, button {{ font: inherit; color: var(--text); background: #151b23; border: 1px solid var(--border); border-radius: 6px; padding: 5px 12px; }}
  input {{ width: 100%; max-width: 280px; box-sizing: border-box; margin-bottom: 8px; }}
  button {{ background: #212830; cursor: pointer; }}
  button:hover {{ background: #262c36; }}
  #msg {{ margin: 8px 0 0; }}
</style>
</head>
<body>
<main>
"""

FORM = """<form id="unlock" hidden>
  <label for="pw">Password</label>
  <input id="pw" type="password" autocomplete="current-password" required>
  <button type="submit">Download</button>
  <p id="msg" class="muted" aria-live="polite"></p>
</form>
"""

SCRIPT = """<script>
// The deck is locked (PBKDF2-SHA256 -> AES-256-GCM, made by the Arrernte project's
// scripts/encrypt_deck.py): "ECA1" | iterations (4 bytes) | salt (16) | iv (12) | ciphertext.
// Unlocked here, in the browser.
const link = document.getElementById("get-deck");
const form = document.getElementById("unlock");
const msg = document.getElementById("msg");
link.addEventListener("click", e => {
  e.preventDefault();
  form.hidden = false;
  document.getElementById("pw").focus();
});
form.addEventListener("submit", async e => {
  e.preventDefault();
  const button = form.querySelector("button");
  button.disabled = true;
  msg.textContent = "Unlocking...";
  try {
    const file = link.dataset.file;
    const res = await fetch(file, { cache: "no-store" });
    if (!res.ok) throw new Error("download");
    const blob = new Uint8Array(await res.arrayBuffer());
    const view = new DataView(blob.buffer);
    const iterations = view.getUint32(4);
    const salt = blob.slice(8, 24), iv = blob.slice(24, 36), data = blob.slice(36);
    const base = await crypto.subtle.importKey("raw",
      new TextEncoder().encode(document.getElementById("pw").value), "PBKDF2", false, ["deriveKey"]);
    const key = await crypto.subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt, iterations },
      base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
    let deck;
    try {
      deck = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, key, data);
    } catch {
      throw new Error("password");
    }
    const url = URL.createObjectURL(new Blob([deck], { type: "application/octet-stream" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = file.replace(/\\.enc$/, "");
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    msg.textContent = "Done. Now open the downloaded file with Anki.";
  } catch (err) {
    msg.textContent = err.message === "password"
      ? "That password didn't work. Please try again."
      : "Something went wrong with the download. Please try again.";
  } finally {
    button.disabled = false;
  }
});
</script>
"""

TAIL = """</main>
{script}</body>
</html>
"""


def build(md_path):
    folder = os.path.dirname(md_path)
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    title = re.search(r"^#\s+(.+)$", text, re.M)
    if not title:
        sys.exit(f"{md_path}: the page needs a # heading on its first line")
    title = re.sub(r"[*_`]", "", title.group(1)).strip()
    body = markdown.markdown(text)
    script = ""
    if "{download}" in body:
        decks = sorted(glob.glob(os.path.join(folder, "*.apkg.enc")))
        if len(decks) != 1:
            sys.exit(f"{folder}: needs exactly one locked deck (.apkg.enc), found {len(decks)}")
        name = html.escape(os.path.basename(decks[0]))
        link = (f'<b><a href="#" id="get-deck" data-file="{name}">Download the deck (.apkg)</a></b>')
        para = re.search(r"<p>([^\n]*?)\{download\}([^\n]*?)</p>", body)
        if not para:
            sys.exit(f"{md_path}: put {{download}} on a line of its own")
        body = (body[:para.start()] + f'<p class="download">{para.group(1)}{link}{para.group(2)}</p>\n'
                + FORM + body[para.end():])
        script = SCRIPT
    out = os.path.join(folder, "index.html")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        robots = ('\n<meta name="robots" content="noindex, nofollow">'
                  if os.path.basename(folder) == "unpublished" else "")
        f.write(HEAD.format(title=html.escape(title), robots=robots) + body + "\n" + TAIL.format(script=script))
    print("wrote", os.path.relpath(out, HERE))


def main():
    pages = ([os.path.join(HERE, "page.md")] + sorted(glob.glob(os.path.join(HERE, "*", "page.md")))
             + sorted(glob.glob(os.path.join(HERE, "*", "*", "page.md"))))
    for p in pages:
        if os.path.exists(p):
            build(p)


if __name__ == "__main__":
    main()
