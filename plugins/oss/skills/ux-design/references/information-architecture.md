# Information Architecture

Answers one question: how should content be inventoried, grouped, hierarchically shaped, labelled, and classified so people can find it? Read this before choosing navigation patterns or page layouts, and before defending a category name in review. The visible navigation layer — menus, breadcrumbs, location cues — lives in `navigation-and-wayfinding.md`; this file stops at the structure and vocabulary that navigation exposes.

## What IA decides, and what it does not

- Treat IA as two decisions: which content and functionality exist, and the organisation, structure, and nomenclature that define relationships between them [1].
- Keep IA out of the visual layer. It is documented in spreadsheets and diagrams and _informs_ the UI rather than appearing in it [1].
- Treat navigation as a partial, frontstage view of the full IA: one menu shows a slice of a much larger tree [1].
- Settle the IA before committing to a navigation layout. An inverted-L pattern (top bar plus left rail) accommodates roughly four tiers; discovering five-tier sections later forces either a new navigation design or a crammed tree [1].
- When a section goes unvisited, split the diagnosis: users reject the label (IA cause) or never notice the link (UI cause). Run one IA-focused and one UI-focused method before redesigning either [8].
- Do not accept "users will just search". Search logs record the vocabulary users bring, including terms the navigation and category names never use [7].
- Derive the URL scheme from the IA before wireframes: one stable plain-English segment per object type, plural so the path walks back to an index, and a permanent identifier rather than the title or the current parent [11].

## Model the user's vocabulary, not the org chart

- Take category names from the words users type. Search logs expose the mismatch directly: users query _dark chocolate_ while the site says _noir_ [7].
- Card sorting is the generative method for grouping. Participants place labelled cards into groups that make sense to them, then name those groups [4].
- Do not promote card-sort labels straight into the menu. Group names are evidence about concepts, not finished interface copy [4].
- Avoid cards sharing a leading word (_Toyota Camry_, _Toyota Matrix_). Participants group on the shared token instead of on meaning [4].
- Distrust internal classification schemes. Rental-car classes such as _economy_, _intermediate_, and _full-size_ fail where users sort by size, seats, and price [4].
- Mirror existing domain vocabulary where it is stable, and describe content where no shared term exists; an invented abstraction costs more than a plain description [inference].
- Check every label against the org chart: department names (_Office of the Vice Chancellor of Finance_) mean nothing to users who do not already know where the content lives [2].
- Build the card list from user questions, objections, and tasks, not from the sections the organisation wants to promote; merge duplicates into 30–60 plain-language cards [9].

## Choose breadth and depth deliberately

- Compare a flat tree (about eight top categories, three layers) with a deep one (four categories, five levels). The deep tree buries the same content under more intervening layers and is harder to use [3].
- Spend the budget on breadth while labels stay specific and non-overlapping; depth forces generic labels at every level, and generic siblings are the main source of confusion [3].
- Cap single-level lists by grouping items visually rather than by adding tiers. A 32-item medical-services menu stays scannable only when related items are chunked [3].
- Add shortcuts for anything deeper than three levels: alphabetical indexes, "most viewed" lists, and direct links from the top-level menu [3].
- Accept depth when intermediate category pages do real work; showing specific topics too early confuses users who do not yet know the offering [3].
- Record the intended maximum depth and items-per-level in the IA document and reject new content that breaks it [inference].

| Shape | Typical dimensions              | Strength                              | Failure mode                               |
| ----- | ------------------------------- | ------------------------------------- | ------------------------------------------ |
| Flat  | 6–10 top categories, 2–3 levels | Specific labels, few clicks           | Overlapping categories, overwhelming menus |
| Deep  | 3–5 categories, 4–6 levels      | Small menus, clear parent-child logic | Generic labels, lost users, buried content |

Both shapes describe the same content; the trade is between label specificity and click depth [3].

## Validate with card sorting, then tree testing

- Size a card sort at 30–50 cards. Past 50, participants create a _Miscellaneous_ pile and the groupings stop being interpretable [4].
- Recruit at least 15 participants for a qualitative sort (why people group things) and 30–50 for a quantitative one (how often) [4].
- Run open sorts to discover groupings. Use closed sorts only to check names, and run a tree test when the question is "can people find X?" [4].
- In a tree test, participants see only the hierarchy as nested accordions plus the task text — no layout, styling, or content [5].
- Write tasks as scenarios that omit the target label. "Find information about starting a business" leaks the answer; describe the situation instead [5].
- Compare alternative labels with two trees and a between-subjects design; compare alternative locations within a single tree [5].
- Judge results on directness and first click, not success alone. A high success rate with heavy backtracking still indicates a bad hierarchy [5].
- Account for the tool limit: most tree-testing software scores only leaf nodes, so an intermediate category landing page cannot be the correct answer [5].
- Always tree-test the hierarchy produced by a card sort. Sorts generate options, never a validated structure [5].
- Follow the standard sequence: usability test the current site for findability failures, card sort to generate options, tree test to choose one [5].
- Treat cards filed under several sections — or dropped into an added _I don't know_ bucket — as cross-linking targets: link the page from every section users filed it under, not only its canonical parent [9].

## Label for information scent

- Treat every label as a scent signal made of the label text, accompanying content, surrounding page context, and the user's prior knowledge [2].
- Make labels self-sufficient. On small screens the surrounding context disappears, so _Christmas_ has to become _Christmas gifts_ [2].
- Add scent with summary text that says what the destination contains. A summary repeating the label adds nothing [2].
- Choose representative images for categories. Decorative or generic thumbnails contribute no cues, and atypical category members slow recognition [2].
- Strip internal jargon and product code names from labels. Unfamiliar acronyms (a firewall product labelled _NGFW_) read as noise [2].
- Keep granularity consistent across siblings: do not mix an object (_Invoices_), a task (_Pay a bill_), and a slogan (_Get paid faster_) at one level [inference].

## Classify content for search and catalogues

- Keep four artifacts distinct: navigation (frontstage), IA structure or sitemap, taxonomy, and content model [6].
- Define a taxonomy as a closed list of terms arranged hierarchically and applied to content: authors attach terms but do not invent them [6].
- Use a faceted taxonomy when one hierarchy cannot carry every attribute; facets let users combine filters instead of descending a deep tree [6].
- Model synonyms explicitly. Where _RFP_, _Proposal_, _Statement of Work_, and _Pitch_ are used interchangeably, pick a preferred term and link the rest as non-preferred or related [6].
- Choose the user-facing term as the preferred term even backstage, because taxonomy terms leak into topic links and search suggestions [6].
- Reuse an industry taxonomy before building one; check registries such as BARTOC for open and licensed options [6].
- Assign an owner and a review cycle: merge, rename, and retire terms, and spot-check how new content was tagged [6].

## Measure findability cheaply

- Separate the two failures. Findability is locating something you assume exists; discoverability is encountering something you did not know existed [8].
- Read search logs before commissioning research: pull the top 1000 queries over 3–6 months and inspect roughly the top 300 by frequency [7].
- Treat no-result queries as a content-gap and misspelling list; high-volume no-result terms are the cheapest IA fix available [7].
- Order queries by user identifier and timestamp to expose failed query chains (dog → canine → dog toys → bones) that name the missing category [7].
- Run a click test on a static screenshot to learn which navigation components are noticed, ignored, or avoided [8].
- Combine one IA method with one UI method. If a closed sort passes while a click test fails, the labels are fine and the layout is the problem [8].
- Strip IP addresses and identifiers before sharing logs, and destroy raw logs after analysis [7].
- Review semiannually, and ask for search logging to be switched on if it is off [7].

## Keep artifacts only if someone uses them

- Produce a content inventory (what exists) before a content audit (what is accurate, useful, on-voice) [1].
- Keep a sitemap showing every node and its parent, coded by tier, as the reference for navigation, redirects, and ownership [1].
- Maintain the taxonomy in a tool that stores preferred and non-preferred terms, not in prose documents [6].
- Skip the full inventory on a small, fully authored site; insist on it for migrations, mergers, and any site whose content ownership is unclear [inference].
- Version the tree with a date and an owner. A hierarchy that changes silently makes old tree-test results unreadable [inference].
- Number nodes decimally in the sitemap (1.0, 1.1, 1.2.1) and reuse those IDs in audits, wireframes, and tickets so the team cites the same page [10].

## Sources

[1] [The Difference Between Information Architecture (IA) and Navigation](https://www.nngroup.com/articles/ia-vs-navigation/) — Nielsen Norman Group, Jen Cardello — accessed 2026-11-27 — supports: what IA decides, content inventory/audit, sitemap, four-tier navigation limit, artifacts.

[2] [Information Scent: How Users Decide Where to Go Next](https://www.nngroup.com/articles/information-scent/) — Nielsen Norman Group, Raluca Budiu — accessed 2026-11-27 — supports: scent components, label self-sufficiency on mobile, summaries and images, jargon.

[3] [Flat vs. Deep Website Hierarchies](https://www.nngroup.com/articles/flat-vs-deep-hierarchy/) — Nielsen Norman Group, Kathryn Whitenton — accessed 2026-11-27 — supports: breadth/depth trade-off, label specificity, long-list grouping, deep-structure shortcuts.

[4] [Card Sorting: Uncover Users' Mental Models for Better Information Architecture](https://www.nngroup.com/articles/card-sorting-definition/) — Nielsen Norman Group, Samhita Tankala and Katie Sherwin — accessed 2026-11-27 — supports: card counts, participant counts, open vs. closed, terminology matching, domain vocabulary.

[5] [Tree Testing: Evaluate Menu Labels and Categories](https://www.nngroup.com/articles/tree-testing/) — Nielsen Norman Group, Page Laubheimer — accessed 2026-11-27 — supports: tree-test setup, task phrasing, between-subjects label comparison, directness, leaf-only limitation, research sequence.

[6] [Taxonomy 101: Definition, Best Practices, and How It Complements Other IA Work](https://www.nngroup.com/articles/taxonomy-101/) — Nielsen Norman Group, Page Laubheimer — accessed 2026-11-27 — supports: controlled vocabulary, four IA artifacts, facets, thesaurus relations, preferred terms, BARTOC, governance.

[7] [Search-Log Analysis: The Most Overlooked Opportunity in Web UX Research](https://www.nngroup.com/articles/search-log-analysis/) — Nielsen Norman Group, Susan Farrell — accessed 2026-11-27 — supports: query volumes and windows, no-result analysis, session chains, vocabulary mismatch, privacy, review cadence.

[8] [Low Findability and Discoverability: Four Testing Methods to Identify the Causes](https://www.nngroup.com/articles/navigation-ia-tests/) — Nielsen Norman Group, Jen Cardello — accessed 2026-11-27 — supports: findability vs. discoverability, IA-vs-UI diagnosis, click tests, method combination.

[9] [How To Create An Information Architecture That Is Easy To Use](https://www.smashingmagazine.com/2022/03/easy-information-architecture/) — Smashing Magazine, Paul Boag — accessed 2026-11-27 — supports: questions/objections/tasks as the card source, the added "I don't know" bucket, cross-linking cards filed under several sections.

[10] [Everyday Information Architecture: Auditing for Structure](https://alistapart.com/article/everyday-information-architecture-excerpt/) — A List Apart, Lisa Maria Martin — accessed 2026-11-27 — supports: decimal page IDs reused across audits, sitemap, and wireframes; structural audit columns.

[11] [Responsive Design Begins With The URL](https://www.smashingmagazine.com/2014/05/responsive-design-begins-with-the-url/) — Smashing Magazine, David Marland — accessed 2026-11-27 — supports: URL scheme derived from the IA, permanent object identifiers over titles and parents, canonical home per object.
