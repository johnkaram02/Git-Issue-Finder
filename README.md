# Git Issue Finder

An AI-powered assistant that analyzes your repository's code to automatically rank, plan, and assign GitHub issues. Stop guessing which issue to tackle next—let an AI developer triage your backlog for you.

<p align="center">
<a href="https://youtu.be/8hFkMgqPcsA" target="_blank">
<img src="https://img.youtube.com/vi/8hFkMgqPcsA/maxresdefault.jpg" alt="Watch the Git Issue Finder Demo Video" width="600" />
</a>
</p>
<p align="center">
<em>Click the thumbnail above to watch the full demo on YouTube.</em>
</p>

## What's The Problem?

Manually triaging a GitHub backlog is a slow and inaccurate process. Product managers and senior developers waste hours trying to answer:

* "Which of these 50 issues is a quick fix?"
* "Which files are *actually* related to this bug?"
* "Is this a good task for our new intern, or does it need a senior dev?"

Guesswork leads to wasted sprints, mis-assigned tasks, and frustrated developers.

## The Solution

**Git Issue Finder** acts as an expert AI developer. It connects to your repository, reads your open issues, and then *reads your actual source code* to simulate a fix.

It doesn't just guess based on the issue title. It performs a two-stage analysis:

1.  **Initial Triage:** Scans all open issues to find the Top 5 most promising candidates for quick fixes.
2.  **Deep Code Analysis:** For each candidate, it:
    * Identifies the 3-5 most relevant files in your repo.
    * Fetches and reads the *content* of those files.
    * Simulates a fix and generates a detailed report.

The result is a simple, actionable list of issues, each with a proposed plan, difficulty score, and recommended assignee.

## Features

* **AI-Powered Triage:** Automatically identifies the top 5 "easiest" issues from your entire backlog.
* **Deep Code Analysis:** Doesn't just read the issue; it identifies and **reads the relevant files** in your repo to understand the context.
* **Automated Action Plans:** Generates a concise, step-by-step plan to implement the fix for each issue.
* **Transparent Reasoning:** Includes an expandable "thought process" that explains *why* the AI suggested a fix, which files it analyzed, and what logic it used.
* **Smart Assignments:** Recommends the best developer level (e.g., `Intern`, `Junior`, `Senior`) for the task based on its complexity.
* **Private Repo Support:** Works with public and private repositories (via GitHub Personal Access Token).
* **Model Selection:** Allows you to choose which Google Gemini model to use for the analysis.

## How It Works: The AI Pipeline

1.  **Fetch Issues:** The app uses the GitHub API to fetch all open issues from your repo.
2.  **Triage Prompt:** The titles of all issues are sent to the AI (`get_ai_analysis`) with a request to identify the **Top 5 easiest** ones to resolve.
3.  **Deep Analysis Loop:** The app then loops through those 5 selected issues:
    * **Identify Files:** It asks the AI, "Which 3-5 files are most relevant to this specific issue?"
    * **Fetch Content:** It uses the GitHub API to download the source code of *only* those relevant files (`get_file_content`).
    * **Final Analysis:** It sends the AI a final, detailed prompt containing the issue details *and* the full content of the relevant files.
    * **Generate Report:** The AI returns a structured JSON object with the `difficulty`, `analysis`, `plan`, `reasoning`, and `assignee_level`.
4.  **Display Results:** The Streamlit frontend renders these results in a clean, interactive UI.

## Setup & Local Usage

Get this running on your local machine in 4 easy steps.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/git-issue-finder.git](https://github.com/your-username/git-issue-finder.git)
cd git-issue-finder
```

### 2. Install Dependencies

Your `requirements.txt` file already exists. Install the necessary dependencies from your terminal:

```bash
pip install -r requirements.txt
```

### 3. Get Your API Keys

You will need two keys to run the app:

* **Google AI Studio API Key:**
    1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
    2.  Click "Create API key in new project".
    3.  Copy this key and paste it into the app's input field when you run it.

* **GitHub Personal Access Token (PAT):**
    * *Required for private repos. Optional (but recommended) for public repos to avoid rate limiting.*
    1.  Go to your GitHub [Developer Settings](https://github.com/settings/tokens).
    2.  Click "Generate new token" -> "Generate new token (classic)".
    3.  Give it a description (e.g., "GitIssueFinder").
    4.  Select the **`repo`** scope (this is all you need).
    5.  Generate the token and copy it.

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` and start analyzing!

## Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Model:** [Google Gemini API](https://ai.google.dev/)
* **Data:** [GitHub REST API](https://docs.github.com/en/rest)
* **Language:** [Python](https://www.python.org/)

## License

This project is open-source. Feel free to fork, modify, and use. We suggest the MIT License.

```
MIT License

Copyright (c) 2025 John & Raphael

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.