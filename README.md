# Account intelligence for sellers

A proof of concept and a slide deck. The proof of concept joins a sample customer file with two call transcripts. The slides are in `slides.md`. The Components slide uses `showpad.svg`.

## What you need

- Python, with `pip`
- Node.js, with `npm`
- [Ollama](https://ollama.com/), running on this machine, with the model `gemma4:e2b`

```powershell
ollama pull gemma4:e2b
```

Ollama listens on `127.0.0.1:11434`. The proof of concept does not start it.

## Proof of concept

From the `POC` folder:

```powershell
.\run.ps1
```

The script installs `fastapi`, `uvicorn`, and `pydantic` from `requirements.txt`, then serves the page and the API together at [http://127.0.0.1:8000](http://127.0.0.1:8000).

The same start without the script, still from `POC`:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

The sample customer file is `backend/crm/data/mock_crm.json`. The two transcripts are `backend/calls/data/acme.txt` and `backend/calls/data/sam.txt`. Records stay in memory. Restarting the process clears them. On the page, sync the customer file, then process a call.

## Slides

`package.json` and `package-lock.json` list the Slidev packages. From the project root:

```powershell
npm install
npx slidev slides.md
```

The deck opens at [http://localhost:3030](http://localhost:3030). `showpad.svg` must stay next to `slides.md`. The Components slide loads it from there.
