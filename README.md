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

- **What it does:** Writes a short caption someone would post about the find.
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

```
$ python app.py ask 'vintage graphic tee under $30, size M'

Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Hey babe! That Y2K butterfly baby tee is a total steal. Here are two cute ways to style it with your closet:

**Outfit 1: Casual Y2K Streetwear**
Pair the baby tee with your *Baggy straight-leg jeans, dark wash*. Layer the *Black cropped zip hoodie* over top, leaving it unzipped. Slip on the *Chunky white sneakers* and finish with the *Black crossbody bag*. 

**Outfit 2: Sweet Cottagecore Contrast**
Tuck the baby tee into your *Wide-leg khaki trousers*, and cinch the waist with the *Brown leather belt*. Throw on the *Vintage black denim jacket* and ground the look with your *Black combat boots* for an effortless mix of sweet and edgy!

  Fit card: Found this cute little Y2K butterfly baby tee scrolling on depop and I am obsessed. It was only $18.00 and gives off major 2000s pop star off-duty energy. Can't wait to pair it withbaggy denim and chunky sneakers for running errands.

0 model calls this session, 2 served from cache
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

**Unit 4**

- *What I asked for:* Help moving `search_listings` onto MCP, adding a loop trace, running the five-try test, and fixing the one miss.
- *What came back:* Step-by-step edits for `mcp_server.py`, `agent.py` and the `create_fit_card` prompt, plus small scripts (`check_criteria.py`, `check_cards.py`) to score criteria the run log doesn't record.
- *What I changed:* I ran every command and checked each result myself. I read the fit cards to count criterion 4, and I swapped the `dress under $25` scenario for `hoodie under $40` when it returned nothing and so tested nothing.

---

## Run Log — Before

Produced by `run_eval.py::main` (results/run_2026-10-07_2015_before.md), cache off, 5 tries each. Criteria 3 and 5 were scored with `check_criteria.py`, because the run log does not record the id that `suggest_outfit` received or every returned price. Criterion 4 was scored with `check_cards.py`. Rule for criterion 4(a): the price counts only if `$19` appears as a number, so "nineteen bucks" fails.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. selected_item id matches id suggest_outfit received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card has price, platform, no "None", 2-4 sentences | 4 of 5 | FAIL | FAIL | FAIL | FAIL | PASS | MISSED (1/5) |
| 5. Price ceiling respected (5 queries) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Real output (`tools.py::create_fit_card`, results/run_2026-10-07_2015_before.md, fit card scenario, try 1):

```
Scored this faded grey vintage band tee on depop for nineteen dollars and honestly, I'm never taking it off. The cotton is butter-soft and has that perfect 90s grunge fade you just can't fake. Can't wait to beat it up with combat boots and oversized denim all fall.
```

Real output (`check_criteria.py`, criterion 3, try 1): `lst_033 vs lst_033 -> PASS`

One note on criterion 5: in the before run, the scenario `dress under $25` returned no listings, so it tested nothing. The criterion 5 row above uses `check_criteria.py`, where all five queries returned results.



## Verdicts and Diagnoses

Verdicts are read against the targets in `criteria.md`, written in Unit 3. Counts come from the before run (`results/run_2026-10-07_2015_before.md`). Rule for criterion 4(a): the price counts only if `$19` appears as a number.

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five tries ran all three tools and returned a fit card. |
| 2 | Impossible query stops before suggest_outfit | 5 of 5 | MET (5/5) | All five tries stopped at the branch; the trace shows suggest_outfit never ran. |
| 3 | selected_item id matches id suggest_outfit received | 5 of 5 | MET (5/5) | `check_criteria.py` printed `lst_033 vs lst_033` in all five tries. |
| 4 | Fit card has price, platform, no "None", 2-4 sentences | 4 of 5 | MISSED (1/5) | `check_cards.py` found the price as a number in only 1 of 5 cards; the other three checks passed in all five. |
| 5 | Price ceiling respected across 5 queries | 5 of 5 | MET (5/5) | All five queries returned results and none had a price over its ceiling. |

**Diagnoses**

**Criterion 4 (the only miss).** The failing place is the model's output in `tools.py::create_fit_card`. In tries 1 to 4 the card wrote the price in words ("nineteen dollars", "nineteen bucks"), so part (a) failed. Platform, no "None" and 2-4 sentences passed in every try. The search and the loop worked: the right item reached the tool each time. The cause is the prompt: it said to mention the price but never said to write it as digits, so the model chose words or digits at random across runs. With only one miss there is no pattern across tools. This is one prompt problem, which is what the improvement below fixes.

No criteria were revised. `criteria.md` is unchanged.


---

## Loop Trace

Command: `python app.py ask 'vintage graphic tee under $30' --trace`

```
[1] parse query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print … +7 more
[3] select item
      out: Vintage Band Tee — Faded Grey ($19.0, depop)
      →    first result chosen
[4] suggest_outfit
      in:  Vintage Band Tee — Faded Grey ($19.0, depop)
      out: Hey friend! That faded band tee is an absolute score. Here are two ways to style it using what’s already in yo…
[5] create_fit_card
      in:  Vintage Band Tee — Faded Grey ($19.0, depop)
      out: Scored this perfectly faded vintage band tee on depop for $19 and I am so obsessed with how soft it is. Ithas…
```


---



## What's Still Broken

All five criteria met their targets in the after run, so nothing is left to diagnose. These are the things I would still tighten or fix:

- **Criterion 1's target was too easy.** It passed 5 of 5 in both runs, so I would raise it from 4 of 5 to 5 of 5.
- **Keyword search is brittle.** `dress under $25` returned nothing even though dresses may exist under other wording, and "t-shirt" can miss a listing that says "tee". I would add simple synonyms.
- **`suggest_outfit` sometimes writes prices in words.** One before-run outfit text said "nineteen bucks", and the fit card could copy that. I did not fix it because the unit allows one improvement.
- **The fit card check is narrow.** It only accepts `$19`, so a card that says "19 dollars" would fail even though the price is there. I kept the rule fixed so the before and after runs could be compared.




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
## Failure modes triggered on purpose

- **Empty search** (`designer ballgown size XXS under $5`): `No listings matched 'designer ballgown'. You could raise your price limit above $5, or drop the size filter (XXS), or try different or fewer keywords.`
- **Empty wardrobe** (`--empty-wardrobe`): the agent returned general styling advice using basics the user likely owns, and a normal fit card. No crash and no blank.
- **Model unavailable** (one character of the key removed): `ModelUnavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.` No stack trace and no hang. The key was restored afterwards and `test.py` passed again.

## The MCP move

I moved `search_listings` onto MCP. In `mcp_server.py` it is registered with typed inputs and a description that states the empty case. In `agent.py::run_agent` the direct call became `call_tool("search_listings", {...})`. Behavior was unchanged: the same queries returned the same items, and the empty case still returned `[]`. The only visible difference is that each call is slower, because the server starts on every call.

## The Improvement

**Change:** one sentence added to the `create_fit_card` prompt in `tools.py`: "Write the price as a number with a dollar sign, like $19 or $19.00, and never spell it out in words (not 'nineteen bucks')."

**Why:** it targets the one diagnosed failure, criterion 4(a), where the model spelled out the price in 4 of 5 tries. Nothing else in the agent changed. I also swapped the criterion 5 scenario `dress under $25` for `hoodie under $40`, because the dress search returned nothing and an empty result cannot test a price ceiling. That swap does not affect criterion 4.

## Run Log — After

Produced by `run_eval.py::main` (results/run_2026-10-07_2112_after.md), same settings. Criteria 3 and 5 re-run with `check_criteria.py`.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. selected_item id matches id suggest_outfit received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card has price, platform, no "None", 2-4 sentences | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Price ceiling respected (5 queries) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help?** Yes. Criterion 4 went from 1 of 5 to 5 of 5 (`check_cards.py` on both files), and the other four criteria were unchanged. This is one run of five tries, so it is evidence rather than proof, since a model can still ignore an instruction occasionally.
