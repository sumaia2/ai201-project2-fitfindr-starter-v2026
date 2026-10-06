# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---


## What This Does

FitFindr takes a plain-language thrifting request such as "a vintage graphic tee under $30, size M". It searches a file of 40 secondhand listings, picks the best match, suggests outfits that combine it with items the user already owns, and writes a short caption the user could post. If nothing matches, it stops and tells the user what to change instead of guessing.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:**
Finds listings that match a description, optionally limited by size and a price ceiling.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None).
- **Returns:**
A list of full listing dicts (id, title, description, category, style_tags, size, condition, price, colors, brand, platform), best match first, at most config.SEARCH_RESULT_LIMIT items. A listing's score is the number of words from `description` that appear in its title, description, style_tags, category, colors or brand. Words that appear in a listing's title count double. Listings scoring zero are dropped. A size matches when the requested size, uppercased, equals one of the listing's size tokens, where the size string is split on spaces, slashes and parentheses. So "M" matches "S/M" and "M", but "L" does not match "XL (oversized)", and "S" does not match "US 9". `max_price` is inclusive. A size or price of None skips that filter.
- **When it has nothing:**
An empty list `[]`, never None and never an exception.

### `suggest_outfit`

- **What it does:** Suggests one or two outfits that combine the thrifted item with pieces the user already owns.
- **Inputs:** `new_item` (dict, one listing), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts).
- **Returns:** A non-empty string of outfit suggestions that name specific wardrobe pieces by their `name`.
- **When it has nothing:** If `wardrobe["items"]` is empty, it returns a non-empty string of general styling advice for the item. It does not raise and does not return an empty string.

### `create_fit_card`

-**What it does:** Writes a short caption someone would post about the find.
- **Inputs:** `outfit` (str, the output of suggest_outfit), `new_item` (dict, one listing).
- **Returns:** A string of two to four sentences that mentions the item, its price and its platform once each. It leaves the brand out when `brand` is None. Wording differs between runs because it calls the model.
- **When it has nothing:** If `outfit` is empty or only whitespace, it returns a descriptive message saying no outfit was provided. It does not raise.

---

## Planning Loop



**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that names what the user could change (raise the price, drop the size, or use different words), leave `session["fit_card"]` as None, and return without calling `suggest_outfit`. Otherwise, set `session["selected_item"]` to the first result and continue to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex. It pulls the price and the size out of the request, and treats the rest as the search words.

**What moves through the session:** `query`, then `parsed` (description, size, max_price), then `search_results`, then `selected_item`, then `outfit_suggestion`, then `fit_card`. `error` is set only when the run ends early.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Hey babe! That Y2K butterfly baby tee is a total steal. Here are two cute ways to style it with your closet:

**Outfit 1: Casual Y2K Streetwear**
Pair the baby tee with your *Baggy straight-leg jeans, dark wash*. Layer the *Black cropped zip hoodie* over top, leaving it unzipped. Slip on the *Chunky white sneakers* and finish with the *Black crossbody bag*. 

**Outfit 2: Sweet Cottagecore Contrast**
Tuck the baby tee into your *Wide-leg khaki trousers*, and cinch the waist with the *Brown leather belt*. Throw on the *Vintage black denim jacket* and ground the look with your *Black combat boots* for an effortless mix of sweet and edgy!

  Fit card: Found this cute little Y2K butterfly baby tee scrolling on depop and I am obsessed. It was only $18.00 and gives off major 2000s pop star off-duty energy. Can't wait to pair it withbaggy denim and chunky sneakers for running errands.

0 model calls this session, 2 served from cache

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
python -c "from tools import search_listings; r = search_listings('graphic tee', max_price=30); print([(x['title'], x['price'], x['size']) for x in r])"
[('Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('Vintage Band Tee — Faded Grey', 19.0, 'L'), ('Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('Vintage Graphic Hoodie — Faded Black', 26.0, 'L'), ('Low-Rise Cargo Pants — Khaki', 27.0, 'W29')]

```

```
python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Hey friend! These vintage Levi's are a thrift-store holy grail. Since they’re a classic medium wash, they'll bring a great casual contrast to your existing dark-wash denim. Here are two ways tostyle them:

**Look 1: Effortless Streetwear**
Tuck your **White ribbed tank top** into the Levi's, add the **Brown leather belt**, and layer the **Vintage black denim jacket** on top. Finish with your **Chunky white sneakers** and the **Black crossbody bag** for an easy, timeless weekend vibe.

**Look 2: Cozy Grunge**
Pair the jeans with your **Oversized grey crewneck sweatshirt** half-tucked in. Cinch the waist with the **Brown leather belt**, lace up your **Black combat boots**, and throw on the **Black crossbody bag** for a cool, textured contrast.

```


```
python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Found my absolute dream medium wash 501s on Depop and I'm still not over it. The fading is so perfectly broken in and they honestly fit like a glove. Paid $38.00 for them which feels like a total steal for actual vintage denim. Can’t wait to live in these with a crisp white tee and beat-up sneakers all fall.

```

---

## How I Used AI

**Moment 1**

- *What I asked for:* A search_listings function that filters by price and size and ranks listings by keyword matches.
- *What came back:* It ran, but every matching listing got the same score, so results came out in price order. A mesh top ranked above the graphic tee when I searched "graphic tee."
- *What I changed:* I made words that appear in a listing's title count double. After that the Graphic Tee ranked first. I also tested that size "M" returns the S/M listings and not the XL flannel.

**Moment 2**

- *What I asked for:* Code for suggest_outfit, create_fit_card and the planning loop in agent.py.
- *What came back:* Code that gave IndentationError when I pasted it in, and a query parser that left the word "under" in the no-results message.
- *What I changed:* I fixed the spacing by hand and corrected the price pattern in _parse_query. I then ran both paths and checked that the id in session["selected_item"] matched the id suggest_outfit received. For criteria.md, I chose the targets and Claude wrote the wording and the reasons.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
