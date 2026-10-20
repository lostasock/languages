# Language flashcards

Website: **https://lostasock.github.io/languages/**

One folder per language, each with its own page and a password-locked deck (`.apkg.enc`):

- `eastern-central-arrernte/`: https://lostasock.github.io/languages/eastern-central-arrernte/

## Editing the text

Edit `page.md` (in the language's folder, or here for the list of languages): Markdown, so
`# heading`, `## smaller heading`, `- list item`, `**bold**`, `*italic*`, `[link text](address)`,
`---` for a line across. `{download}` is where the download link and password box go. Then run

    python build_page.py

which writes each `index.html` from its `page.md` (don't edit `index.html` itself). It needs the
markdown package once: `python -m pip install markdown`.

## Updating the deck

This folder sits next to the (private) Arrernte project, `AndroidStudioProjects/Arrernte`. From
there, lock the new build:

    python scripts/encrypt_deck.py decks/<deck>.apkg ../languages/eastern-central-arrernte

then delete the old `.enc` file in that folder, run `python build_page.py` here (the page links
to whichever `.enc` file is there), and push.
