# Codeforces Coach

Codeforces Coach is a full-stack practice assistant for competitive programmers. It combines profile analysis, retrieval, ranking, and debugging support to identify the best next training step.

## Why this project exists

Most training tools focus on problem difficulty alone. This project goes further by profiling the solver's behavior, interpreting their strengths and weaknesses, and pairing them with problems that match their learning profile.

## Main capabilities

- Codeforces profile analysis and feature extraction
- Persona-based recommendation using ranking models
- Concept search with a semantic retrieval layer
- Guided debugging with Socratic hints and editorial awareness
- Interactive web frontend for user workflows

## Setup summary

- Python 3.10+
- A working Codeforces profile and API access
- A Gemini API key for the assistant behavior
- PostgreSQL and ChromaDB configured for local development

## Repository layout

- backend/ contains the API layer and app logic
- train/ contains experimental notebooks and modeling assets
- .env.example provides the environment variables for local configuration

## License

This project is provided for educational use.
