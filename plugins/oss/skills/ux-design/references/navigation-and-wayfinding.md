# Navigation and Wayfinding

Answers how users learn where they are, where they can go, and how they got here, and which navigation pattern fits a given structure. Read this after the IA is settled, or when reviewing a menu, breadcrumb trail, mobile drawer, or footer. Grouping, labelling, hierarchy shape, and classification live in `information-architecture.md`; this file assumes those decisions exist and covers how they are exposed.

## Answer three questions on every screen

- "Navigation should not only show where you can go but also where you are now" [1].
- Assume any page is an entry page: search engines drop users deep into the site, so each page must orient a first-time visitor with no history [1].
- Stack at least four location signals per page: a linked logo, the current section marked in the menu, a descriptive heading, and a unique page title with a readable URL [1].
- Reinforce with breadcrumbs on hierarchical sites, visible dates or tags, and named/numbered steps in any checkout or wizard [1].
- Never rely on one cue. Designers over-trust subtle highlighting because they already know the structure; visitors overlook changes they did not expect [1].
- Test location signalling by showing a page cold and asking "where are you on this site?", then "how can you tell?", then "what would you expect to see here?" [1].
- Treat heavy pogo-sticking, backtracking, and wandering in analytics as an IA or signposting failure, not a content failure [1].

## Separate global, local, utility, and footer layers

- Put primary navigation in the header on websites and on the left in applications; users look there first [3].
- Place utility navigation (account, cart, sign-in, language) above the primary navigation and search, near the top of the screen [3].
- Put local navigation on the left rail on desktop; it answers "what else is in this section?" and lets users move laterally [3].
- Keep a local menu wherever users compare sibling items or complete several tasks in one section; without it they pogo-stick up and down the tree [3].
- Reserve the footer for non-primary audiences and obligations — investor information, jobs, legal, contact — not for duplicating primary destinations [3].
- Let global navigation advertise scope. Hiding it removes the cues that tell users what the organisation offers, not just where to click [3].
- Keep utility and local layers visually quieter than global navigation so the three do not read as one undifferentiated list [inference].

## Mark the current location unambiguously

- Mark the active section in the menu. Failing to indicate current location is the most common menu mistake observed in testing [3].
- Combine colour with a second differentiator (weight, underline, offset, or a left border); colour alone fails WCAG and colour-blind users [8].
- Do not make the current page a link in the breadcrumb or the menu; a link that does nothing costs trust [2].
- Expose the current node to assistive technology, not only visually — mark the active item programmatically rather than with styling alone [inference].
- Repeat the signal in the page title and URL, which persist in tabs, history, bookmarks, and search results [1].

## Decide between search and browse

- Keep visible navigation even when search exists. Users who cannot name what they want need the structure to partition the space [6].
- Prefer browse for recognition: forming a query costs more than recognising a link, and users are unreliable at phrasing queries [6].
- Expect site search to underperform web search; do not let a weak internal engine justify removing navigation [6].
- Keep the search box continuously visible on the page. Do not hide it inside a mega menu or behind an icon [5].
- Make search primary when most sessions are known-item lookups — model numbers, order IDs, names — which search logs will show as long, specific, repeated queries [inference].
- Pair every search results page with navigation and scoped categories so a failed query can fall back to browsing [inference].

## Match the menu pattern to the content

- Use a top bar for a small, stable set of destinations; it stops working when items crowd below usable touch-target size [6].
- Never hide desktop navigation behind a hamburger. On desktop, hidden menus were used in 27% of tasks versus 48% (visible) and 50% (mixed), cut content discoverability by more than 20%, raised difficulty ratings 21%, and made tasks 39% slower [4].
- On mobile, show up to four top-level links; above four, hiding some is the only workable trade, and the penalty is smaller than on desktop [4].
- Use a persistent tab bar for app-like products with four or five destinations, and label the icons [6].
- Use a mega menu when the structure is broad and users routinely drill two or three levels; a two-dimensional panel shows several tiers at once instead of forcing recall [5].
- Delay hover-opened mega menus by 0.5 seconds, render within 0.1 seconds, keep them open until the pointer has been outside for 0.5 seconds, and tolerate diagonal pointer paths [5].
- Never let an open mega menu cover the whole large screen; users read it as a page change and lose their place [3].
- Avoid cascading submenus beyond two tiers. They cause wrong selections and users fall out of the menu entirely [3].
- Open submenus on click, not hover; hover is unavailable to keyboard and touch users and misfires for everyone else [3].
- Mark items that open a submenu with a caret so users can tell them from items that navigate [3].
- Use a homepage-as-hub only for task-based products where users complete one job per session; otherwise it wastes the homepage and adds a step to every navigation action [6].

| Pattern             | Fits                         | Characteristic failure                           |
| ------------------- | ---------------------------- | ------------------------------------------------ |
| Top bar             | Few, stable destinations     | Crowding, unreadable at small widths             |
| Sidebar / left rail | Broad structures, apps       | Eats horizontal space, collapses badly on mobile |
| Mega menu           | Broad catalogues, 2–3 tiers  | Covers the screen, unscannable label groups      |
| Hamburger / drawer  | Mobile, browse-heavy content | Destinations go unnoticed; 27% desktop usage     |
| Hub-and-spoke       | Single-task tools            | Every move routes through the homepage           |

Pattern descriptions and failure modes per [3], [4], [5], [6].

## Use breadcrumbs only where a hierarchy exists

- Treat breadcrumbs as a supplement to global and local navigation, never a replacement [2].
- Show the page's position in the site hierarchy, not the session history; history trails grow long, repeat, and mislead users who arrived from a search result [2].
- Include only nodes that are real pages; omit logical subcategories that have no page of their own [2].
- End the trail with the current page and do not link it [2].
- Start the trail at Home, unless the global navigation already carries a Home link — one of the two is enough [2].
- Omit breadcrumbs on sites one or two levels deep and on linear, non-hierarchical experiences [2].
- Pick one canonical path for polyhierarchical content and show only that trail; multiple trails confuse users and search engines [2].
- On mobile, forbid wrapping, keep tap targets at least 1 cm × 1 cm, and consider truncating the trail to the immediate parent [2].

## Keep back, history, and deep links predictable

- Do not hijack browser Back. Users rely on it to return to known territory, and breaking it strands them [1].
- Support deep arrivals on every page with three elements: organisation name or logo top-left, a one-click link home, and search top-right [7].
- Do not assume a drill-down path. A visitor landing on a product page may never have seen the category page that explains the offering [7].
- Put filters, sort order, pagination, and selected tabs in the URL so a copied link reproduces the view [inference].
- Only block indexing for pages that genuinely must not be seen first; deep links are how motivated users arrive [7].
- Remember the measured cost of bad paths: difficulty getting from homepage to the right product page accounted for 27% of e-commerce task failures across 20 sites [7].

## Make navigation operable without a mouse

- Provide a skip link and other bypass mechanisms so keyboard users are not forced through the whole menu on every page (WCAG 2.4.1) [8].
- Keep focus order logical and matching the visual order (WCAG 2.4.3) [8].
- Make focus visible on every menu item and control (WCAG 2.4.7) [8].
- Mark menus as lists or labelled landmarks with correct name, role, and value so screen readers can enumerate them (WCAG 4.1.2) [8].
- Make fly-out menus fully keyboard operable, and do not dismiss a submenu the instant the pointer leaves the trigger area [8].
- Size targets for touch and motor-impaired users; small, tightly packed items cause selection errors [8].
- Ensure the current-page state is conveyed in text or semantics, not by colour alone (WCAG technique G128) [8].
- Recognise that a correctly coded mega menu still fails screen-magnifier users when only part of the panel fits the viewport; give menus a visible boundary and make top-level items navigate to a plain page [5].

## Sources

[1] [Navigation: You Are Here](https://www.nngroup.com/articles/navigation-you-are-here/) — Nielsen Norman Group, Susan Farrell — accessed 2026-11-27 — supports: location signalling, entry pages, signal inventory, location test protocol, browser Back.

[2] [Breadcrumbs: 11 Design Guidelines for Desktop and Mobile](https://www.nngroup.com/articles/breadcrumbs/) — Nielsen Norman Group, Page Laubheimer — accessed 2026-11-27 — supports: hierarchy vs. history, page-only nodes, current page not linked, canonical polyhierarchy path, mobile wrapping and tap targets.

[3] [Menu-Design Checklist: 17 UX Guidelines](https://www.nngroup.com/articles/menu-design/) — Nielsen Norman Group, Page Laubheimer — accessed 2026-11-27 — supports: expected layer placement, current-location marking, desktop hiding, full-screen mega menus, cascading menus, hover activation, footers and utility navigation.

[4] [Hamburger Menus and Hidden Navigation Hurt UX Metrics](https://www.nngroup.com/articles/hamburger-menus/) — Nielsen Norman Group, Kara Pernice and Raluca Budiu — accessed 2026-11-27 — supports: usage rates, discoverability drop, difficulty increase, task time, mobile four-item threshold.

[5] [Mega Menus Work Well for Site Navigation](https://www.nngroup.com/articles/mega-menus-work-well/) — Nielsen Norman Group, Jakob Nielsen and Angie Li — accessed 2026-11-27 — supports: two-dimensional panels, hover timing and diagonal problem, search box visibility, screen-magnifier limits.

[6] [Basic Patterns for Mobile Navigation: A Primer](https://www.nngroup.com/articles/mobile-navigation-patterns/) — Nielsen Norman Group, Raluca Budiu — accessed 2026-11-27 — supports: navigation complementing search, top bars and tab bars, item limits, hamburger trade-offs, navigation hub.

[7] [Deep Linking is Good Linking](https://www.nngroup.com/articles/deep-linking-is-good-linking/) — Nielsen Norman Group, Jakob Nielsen — accessed 2026-11-27 — supports: three required elements on interior pages, drill-down assumption, 27% failure share, indexing exceptions.

[8] [Menus Tutorial](https://www.w3.org/WAI/tutorials/menus/) — W3C Web Accessibility Initiative — accessed 2026-11-27 — supports: bypass blocks, focus order, focus visible, name/role/value, fly-out dismissal, target size, colour-only state, current-location technique G128.
