# Language flashcards

Website: **https://lostasock.github.io/languages/**

One folder per language, each with its own `index.html` and a password-locked deck (`.apkg.enc`):

- `eastern-central-arrernte/`: https://lostasock.github.io/languages/eastern-central-arrernte/

The page asks for the password and unlocks the deck in the browser. This folder sits next to the
(private) Arrernte project, `AndroidStudioProjects/Arrernte`. To update the deck, run from there:

    python scripts/encrypt_deck.py decks/<deck>.apkg ../languages/eastern-central-arrernte

then set the page's `data-file` to the new `.enc` file's name, delete the old one, and push.
The page text can be edited by hand: keep the tags, change the words.
