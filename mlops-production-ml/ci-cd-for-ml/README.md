# CI/CD for ML

## Objectives
- Automate linting, tests, and model-quality checks on every push using GitHub Actions.
- Distinguish CI for code (unit tests, lint) from CI for models (data validation,
  performance thresholds) and CD for deployment (build/push image, deploy).
- Add a "model regression gate" that fails the pipeline if a new model underperforms
  a baseline on a held-out set.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- GitHub Actions workflow syntax (`on`, `jobs`, `steps`).
- Caching dependencies in CI for speed.
- Testing data pipelines and models (not just application code): schema checks,
  training smoke tests, metric thresholds.
- Continuous training (CT) as a concept distinct from CI/CD.

## Resources
- GitHub Actions docs: https://docs.github.com/actions
- "Made With ML" MLOps course (CI/CD section): https://madewithml.com/
- Google's "MLOps: Continuous delivery and automation pipelines" whitepaper.

## Checklist
- [ ] Write a GitHub Actions workflow that runs `pytest` and `ruff`/`flake8` on push.
- [ ] Add a step that trains a small model and asserts its accuracy is above a
      fixed threshold (fails the build if not).
- [ ] Cache pip dependencies to speed up the workflow.
- [ ] Add a workflow badge to this README once the workflow exists.

## Mini-project
Create a minimal repo-in-a-folder here with a training script, a test that
checks model quality, and a `.github/workflows/ci.yml` that runs on every
push and fails if the model regresses below a threshold you define.
