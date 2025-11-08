# Contributing

Thanks for your interest in contributing to KubenAI. This document explains how to get the project running locally and the development workflow.

Getting started

1. Fork the repository and clone your fork.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Make changes, run tests (if present), and create a pull request back to the main repository.

Environment & Secrets

- Never commit API keys or secrets. Use the provided `.env.example` files and create `.env` locally.
- For CI or production, use secret stores or environment variables in your deployment system.

Code style & testing

- Keep changes small and focused.
- Add tests for new functionality where practical.

Reporting issues

- Open an issue and include logs, steps to reproduce, and your environment (OS, Docker version).

That's it — thanks for contributing!
