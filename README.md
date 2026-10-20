# Language flashcards

Website: **https://lostasock.github.io/languages/**

One folder per language, each with its own `index.html` and a password-locked deck (`.apkg.enc`):

- `eastern-central-arrernte/`: https://lostasock.github.io/languages/eastern-central-arrernte/

The page asks for the password and unlocks the deck in the browser. To update a deck, lock the new build
with `scripts/encrypt_deck.py` in the (private) project, put the `.enc` file here, set the page's
`data-file` to its name, and push.
