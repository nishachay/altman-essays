# Sam Altman Essays

The best of [Sam Altman's blog](https://blog.samaltman.com) as one EPUB, for e-readers and phones.

**[Download altman.epub](https://github.com/nishachay/altman-essays/releases/download/latest/altman.epub)**

61 essays, about 63,000 words, newest first: How To Be Successful, Productivity, The Days Are Long But The Decades Are Short, The Gentle Singularity, How to Hire, Startup Advice and more, plus Richard Hamming's *You and Your Research*, which Sam republished on his blog.

## What's in it

The blog has 121 posts. This book keeps the ones worth learning from and leaves out product launches, investment announcements, politics, COVID-era notes, market takes and personal posts.

- `posts.txt` — the essays in the book
- `skipped.txt` — posts left out on purpose

Disagree with a pick? Open a PR that moves a URL from one file to the other.

## How it works

`build.py` fetches every essay in `posts.txt`, sorts them by date and builds the EPUB with pandoc. A GitHub Action rebuilds it on every push and every Monday, and publishes it to the `latest` release. When Sam posts something new, `check_new.py` opens an issue so a human decides whether it belongs in the book.

Run it yourself:

```bash
pip install -r requirements.txt   # needs pandoc installed
python build.py                   # writes dist/altman.epub
```

All essays © Sam Altman. This project only collects publicly posted writing for easier reading. Inspired by [ofou/graham-essays](https://github.com/ofou/graham-essays).
