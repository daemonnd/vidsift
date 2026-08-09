# `vidsift`

> **AI-powered YouTube feed filtering and transcript-based video validation.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey)
![CI](https://img.shields.io/github/actions/workflow/status/daemonnd/vidsift-python/ci.yml?label=CI\&logo=github)
![Last Commit](https://img.shields.io/github/last-commit/daemonnd/vidsift-python)
![Repo Size](https://img.shields.io/github/repo-size/daemonnd/vidsift-python)
![Maintained](https://img.shields.io/badge/maintained-yes-success)

---

# Project Overview

`vidsift` is a modular Python CLI application that processes YouTube videos from configured channels and validates their relevance using local LLM analysis on transcript content.

The pipeline currently performs:

## Ingestion

1. Process Videos that got interrupted during the last run
2. Fetch Videos from rss to get data about new videos that get processed.

## Processing

The processing depends on the action, pre-defined in the config for the channel

### Download

- Downloads the video url using yt-dlp

### Summarize

1. Fetch the transcript
2. Chunk the transcript into chunks
3. Summarize each chunk individually to a few bullet points using AI
4. Summarize all the chunk summaries into a final summary

### Validate

1. Run AI against the video metadata
1. Fetch the transcript
1. Chunk the transcript into 2 begin chunks, 1 middle chunk and 2 end chunks.

The project is designed around:

- local-first AI workflows
- modular feature isolation
- pipeline-oriented execution
- minimal external dependencies
- Linux-first development

`vidsift` is built as a step-by-step pipeline designed to keep data downloading and local AI processing separate.

---

# Current Status

| Component           | Status      | Notes                                       |
| ------------------- | ----------- | ------------------------------------------- |
| URL collection      | Working     | Channel video collection implemented        |
| AI validation       | Working     | Local Ollama validation functional          |
| Summarization       | Working     | Transcript-based summarization              |
| Transcript pipeline | Working | Full pipeline implemented        |
| Integer validation  | Working | AI response validation finished |
| CI/CD               | Not started |                                             |
| Tests               | Not started |                                             |

---

# Key Features

- Transcript-driven AI relevance validation
- Local Ollama integration
- Modular feature-based architecture
- Pipeline-oriented execution flow
- Linux-first CLI workflow
- Shared utility layer
- Feature-scoped custom errors
- Transcript extraction from VTT files

---

# Architecture & Project Structure

## Directory Structure

```bash
.
├── CONTRIBUTING.md
├── fake-transcript.txt
├── LICENSE
├── README.md
├── requirements.txt
├── src
│   ├── config
│   │   └── parser.py
│   │
│   ├── features
│   │   ├── summary
│   │   │   └── summarizer.py
│   │   │
│   │   ├── transcript
│   │   │   ├── errors.py
│   │   │   ├── fetcher.py
│   │   │   └── vtt_transcript_extractor.py
│   │   │
│   │   └── validation
│   │       └── video_validator.py
│   │
│   ├── ingestion
│   │   └── url_collector.py
│   │
│   ├── models
│   │   └── video.py
│   │
│   ├── pipeline
│   │   └── vidsift_pipeline.py
│   │
│   ├── shared
│   │   ├── errorprotocol.py
│   │   └── video_id_extractor.py
│   │
│   └── main.py
│
└── system_prompts
    ├── summary.md
    └── validation.md
```

---

# File Responsibilities

| File                                                  | Responsibility                     |
| ----------------------------------------------------- | ---------------------------------- |
| `src/main.py`                                         | Application entrypoint             |
| `src/pipeline/vidsift_pipeline.py`                    | High-level orchestration           |
| `src/config/parser.py`                                | Configuration loading/parsing      |
| `src/ingestion/url_collector.py`                      | Collects YouTube video URLs        |
| `src/features/transcript/fetcher.py`                  | Downloads transcript/VTT resources |
| `src/features/transcript/vtt_transcript_extractor.py` | Converts VTT → transcript text     |
| `src/features/transcript/errors.py`                   | Transcript-specific exceptions     |
| `src/features/validation/video_validator.py`          | AI-based relevance validation      |
| `src/features/summary/summarizer.py`                  | Transcript summarization           |
| `src/models/video.py`                                 | Shared video model                 |
| `src/shared/video_id_extractor.py`                    | Converts YouTube url -> Video ID   |
| `src/shared/errorprotocol.py`                         | Shared logging file  |
| `system_prompts/validation.md`                        | Validation system prompt           |
| `system_prompts/summary.md`                           | Summarization system prompt        |

---

# Execution Flow

```text
Configured Channel IDs
        ↓
URL Collection
        ↓
Video ID Extraction
        ↓
Transcript Fetching
        ↓
VTT Extraction / Cleanup
        ↓
AI Validation
        ↓
Decision
   ├── Download
   ├── Summarize
   └── Ignore
```

---

# Data Flow

```text
YouTube Channel
    ↓
Collected Video URLs
    ↓
Transcript Data
    ↓
Extracted Transcript Text
    ↓
LLM Validation
    ↓
Summary / Download / Ignore Decision
```

---

# AI Validation

Validation is based on transcript content rather than titles or metadata.

Current implementation uses:

- local Ollama inference
- prompt-driven validation
- transcript text as primary input

Current work in progress:

- strict integer parsing
- AI response validation
- malformed response handling

---

# Transcript Pipeline

Current transcript flow:

```text
VTT Download
    ↓
VTT Parsing
    ↓
Transcript Cleanup
    ↓
Transcript String
```

Known pending areas:

- real transcript integration across full pipeline
- fallback behavior
- transcript validation hardening

---

# Configuration (Not implemented yet)

Current configuration system:

```text
src/config/parser.py
```

Possible future additions:

- environment variable overrides
- schema validation
- multiple config layers

---

# Prerequisites

## Required

- Python >= 3.14.5
- Ollama + LLM
- Internet access
- Linux environment

## Python Dependencies

See:

```bash
requirements.txt
```

## Ollama

Example:

```bash
ollama pull [MODEL_NAME]
ollama serve
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/daemonnd/vidsift-python.git
cd vidsift-python
```

## Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Quick Start

## Configure (Not implemented yet)

```bash
[fill here]
```

## Run

```bash
python -m src.main
```

---

# Usage

## Current Pipeline

1. Configure channel IDs
2. Run pipeline
3. Videos are collected
4. Transcripts are processed
5. AI validates relevance
6. Video is summarized or ignored

## Planned CLI Improvements

```bash
vidsift run
vidsift validate
vidsift summarize
vidsift fetch-transcript
```

---

# Error Handling

The project currently uses feature-scoped custom exceptions.

Example:

```text
src/features/transcript/errors.py
```

Shared abstractions currently exist in:

```text
src/shared/errorprotocol.py
```

Current error handling strategy (Not implemented yet):

-

---

# Logging (Only STDOUT logging implemented)

Current logging implementation:

```text
[fill here]
```

Possible future structure:

```text
logs/
├── vidsift.log
├── validation.log
└── transcript.log
```

---

# Security Considerations

- Transcript content should be treated as untrusted input
- AI responses should not be trusted without validation
- Local-first inference reduces external API exposure

Pending hardening work:

- strict validator parsing
- deterministic AI output handling
- malformed response rejection

---

# Testing

Current testing status: Tests don't exist yet

```text

```

Planned areas:

- transcript extraction tests
- validator tests
- malformed AI output tests
- integration tests

---

# Performance Notes

Current bottlenecks likely include: YouTube-related issues because of transcript fetching / Video downloading

- transcript download latency
- local model inference speed
- sequential pipeline execution

Potential future improvements:

- async processing
- caching
- worker pools

---

# Contributing

## Development Standards

- Modular feature isolation
- Explicit responsibilities
- Avoid unnecessary abstractions
- Prefer readable execution flow

## Before Opening PR

Run:

```bash

```

Recommended tooling:

```bash
ruff
mypy
pytest
```

---

# Versioning (No versions yet)

---

# License

Licensed under the MIT License.

See `LICENSE`.

---

# Roadmap

## Near Term

- transcript cleanup improvements
- logging improvements
- summarization implementation
- testing
- video downloading

## Mid Term

- async processing
- caching layer
- improved CLI interface
- expanded testing

## Long Term

- multi-source ingestion
- persistent storage
- distributed processing
- feedback-driven filtering

---

# Contact / Support

## Issues

## Discussions / Community

---

# Acknowledgments

- Ollama contributors
- yt-dlp ecosystem
- Python open-source tooling community
- Linux CLI ecosystem
