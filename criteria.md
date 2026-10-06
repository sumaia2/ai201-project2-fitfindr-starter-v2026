# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
My search is a plain keyword match, so a phrasing like "t-shirt" can miss a
listing that says "tee", and the mixed size formats in my data (S/M,
W30 L30, XL (oversized)) can make the size filter drop a listing the user
would want. Two of the three tools also call the model, which can be rate
limited or fail. 4 of 5 leaves room for one of those without making the
target too easy to hit.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This decision is a plain code check on whether search_listings returned an
empty list, so the model is not involved and the same query behaves the
same way every time. If it ever fails, that's a bug in my branch, not
randomness, so anything below 5 of 5 would hide a real problem.

---

## 3. Something about state

In 5 of 5 tries on a query that matches at least one listing, the `id` in
`session["selected_item"]` is the same as the `id` of the `new_item` that
`suggest_outfit` received.



**Why this target:**
The selected item moves through a plain Python dict (the session), and no
model touches that step. The only way for the ids to differ is a coding
bug, such as picking the wrong list position or overwriting the item, so I
expect every try to match.


---

## 4. Something about the fit card

In at least 4 of 5 tries on a matching query, the fit card (a) contains the
selected item's price, (b) contains its platform name, (c) does not contain
the text "None", and (d) is between 2 and 4 sentences long.



**Why this target:**

The model writes the caption, so wording changes between runs. It might
write "24 bucks" instead of "$24", or run past four sentences even when my
prompt asks for fewer. 4 of 5 allows one off-run from that without making
the target so loose that I can't miss it.

---

## 5. Your choice

For 5 queries that each include a price ceiling, 5 of 5 return only listings
whose `price` is at or below that ceiling.


**Why this target:**

The price filter is a plain comparison (price <= max_price) on a float
field, so the model is not involved. A $45 jacket showing up on a $30
search is an error a user spots at once, and a deterministic filter should
never let it through.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
