# research/daily

One file per UTC day, written by `.github/workflows/daily-research.yml`.

Each file lists what an unattended agent found in the previous 24 hours on this
repository's topic. **Nothing here is merged into `docs/` or `data/`.** An item
marked `verified` had its source page fetched and its quote found in the run;
an item marked `lead` did not. Read a lead as a pointer to check, not as a fact.
Promote a finding into the catalogue only through the existing `experiments/`
and `tools/` gates.

How the run works:

- `kage -p` runs `.github/research/prompt.md` headless against the oc-free
  gateway, with the Deep-Research skills installed by
  `.github/research/install-deep-research.sh`.
- The gateway key is the repository secret `OC_FREE_API_KEY`. It is read from
  the environment and is hidden from the model's shell.
- The job fails, and commits nothing, if the report is missing, is not ASCII, has
  CR characters, or if the agent changed any file outside `research/daily/`.
- Run it on demand from the Actions tab (`workflow_dispatch`).
