# Codeforces Coach

Codeforces Coach is a full-stack practice assistant for competitive programmers. It combines user profiling, semantic search, recommendation ranking, and guided debugging to help users improve faster on Codeforces.

## Overview

This project analyzes a Codeforces profile, identifies a training persona, and recommends problems that match the user's skill level and learning style. It also supports semantic search for concept-based problem discovery and a Socratic debugging mode that offers hints without spilling the solution.

## Included components

- FastAPI backend for authentication, search, profiling, and coaching endpoints
- ML engine for behavioral analysis and recommendation ranking
- Vector-based retrieval layer with ChromaDB and semantic embeddings
- Frontend interface for interactive browsing and debugging
- Training notebooks for profiling and ranking experiments

## Project structure

- backend/ - API, ML logic, and static app assets
- train/ - notebooks and experiment artifacts
- README.md - project overview
- .gitignore - repository hygiene rules

## Getting started

1. Create a virtual environment
2. Install the Python dependencies from backend/requirements.txt
3. Configure your environment variables using the sample file
4. Start the backend with uvicorn or the project's development flow

## Notes

This repository is intended for educational and research use in training workflows for Codeforces preparation.
