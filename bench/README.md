# Bench

`review-lens.js` measures how well each model and effort level finds bugs with the correctness lens from `plugins/toolkit/workflows/adversarial-review.js`. Re-run it when a new model ships to decide which tier the lens should use.

It is a standalone Claude Code Workflow script, not a registered plugin workflow. It reviews the fixture in `fixtures/review-lens/`: `base/` is the code before the change, `src/` is the code after it, and `change.diff` is the diff between them. The change plants five bugs and one decoy, a correct line that looks suspicious.

## Run the bench

Ask Claude Code to run the Workflow with `scriptPath` set to `bench/review-lens.js` and these args:

```js
{ repoDir: "<absolute path of this repo>", cells: [{ model: "opus", effort: "high" }], repeats: 3 }
```

`cells` defaults to opus at `low`, `medium`, and `high`, and `repeats` defaults to 3, so a default run starts nine agents. The cells run one at a time, so each cell's output-token count is measured on its own.

The script scores each finding itself. A finding counts toward a planted bug when it is in that bug's file and its line falls inside the bug's `[lo, hi]` range in `BUGS`.

## Upload the results

The run returns `{ refused, cells, rows }`. Each row is ready to become one line of JSONL for the SignalDB MCP tool `upload_eval_results`. Upload one run per cell:

- `version`: the cell name, such as `opus@high`
- `agent`: `adversarial-review.lens`
- `set`: `review-lens-v1`
- format: `jsonl`, with the `version` key removed from each row, because it goes in the tool argument instead

Then call `compare_eval_runs` to compare the versions.

## Change the fixture

When you change the fixture, update the answer key (`BUGS` and `DECOY` in `review-lens.js`) and the `PLANTED` map in `tests/test_bench.py` together. That test fails when the key stops covering a planted line, and also when the lens text drifts from `adversarial-review.js`.

After editing `base/` or `src/`, regenerate the diff from `bench/fixtures/review-lens`:

```sh
git diff --no-index base src | sed -e 's#a/base/#a/#g' -e 's#b/src/#b/#g' > change.diff
```

## Limitation

The agents run with the repo as their working directory, so they could read the answer key in `review-lens.js`. Only the prompt stops them: it tells them to read files under the fixture's `src/` directory alone.
