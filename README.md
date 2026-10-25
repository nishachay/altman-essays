# Sam Altman: The Essays

[![build](https://github.com/nishachay/altman-essays/actions/workflows/build.yml/badge.svg)](https://github.com/nishachay/altman-essays/actions/workflows/build.yml)

<img src="cover.jpg" alt="Sam Altman: The Essays" width="280" align="right">

Since 2013, Sam Altman has written about startups, ambition, and the arrival of AI. His best essays are as useful today as when he published them, but they are scattered among blog posts on other topics. This project collects them in one place, newest first, as a book you can read anywhere.

**[EPUB]** · **[PDF]** · **[Markdown]**

- **EPUB** for Kindle, Kobo, Apple Books and phone reading apps
- **PDF** for printing or reading on a laptop
- **Markdown** if you want the plain text, one file per essay

All charts and images from the original posts are included.

<br clear="right">

## What's in it

The essays that still hold up, including *How To Be Successful*, *Productivity*, *The Days Are Long But The Decades Are Short*, *How to Hire*, *Startup Advice* and *The Gentle Singularity*. It also includes *The Intelligence Age* and *Moore's Law for Everything*, which Sam published on their own sites rather than his blog.

Looking for *Startup Playbook*? It isn't in the book, because its drawings and layout only work on the original site: [playbook.samaltman.com](https://playbook.samaltman.com/).

## What's left out, and why

His blog has more than a hundred posts, and many of them are not essays. Product launches, investment announcements, political posts, COVID-era notes, market takes and personal news are left out.

Nothing is hidden:

- [`posts.txt`](./posts.txt) lists every essay in the book
- [`skipped.txt`](./skipped.txt) lists every post that was left out

If you think a post belongs in the book, or doesn't, open a pull request that moves its link from one file to the other.

## When Sam publishes something new

Every Monday, a GitHub Action checks his blog. If there is a new post, it opens an issue, and a person decides whether it goes in. This keeps announcements out of the book.

Every change to the list rebuilds the EPUB, PDF and Markdown automatically. The download links above always point to the latest version.

## Build it yourself

You need Python 3 and [pandoc].

```bash
pip install -r requirements.txt
python make_cover.py   # draws cover.jpg
python build.py        # writes the EPUB, PDF and Markdown to dist/
```

To read on a Kindle, send the EPUB with [Send to Kindle].

## Credits

All writing © Sam Altman. Every essay links to the original. The cover art is from his essay [The Intelligence Age]. This project only collects writing he has published publicly, to make it easier to read.

Inspired by [ofou/graham-essays], which does the same for Paul Graham.

[EPUB]: https://github.com/nishachay/altman-essays/releases/download/latest/altman.epub
[PDF]: https://github.com/nishachay/altman-essays/releases/download/latest/altman.pdf
[Markdown]: https://github.com/nishachay/altman-essays/releases/download/latest/altman-markdown.zip
[pandoc]: https://pandoc.org/installing.html
[Send to Kindle]: https://www.amazon.com/sendtokindle
[The Intelligence Age]: https://ia.samaltman.com/
[ofou/graham-essays]: https://github.com/ofou/graham-essays
