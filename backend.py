import time
import json
import base64
import requests
import streamlit as st
import google.generativeai as genai
 
@st.cache_data(ttl=3600)
def get_available_models(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        models_data = response.json().get("models", [])
 
        generative_models = [
            m for m in models_data 
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
 
        model_options = {m["displayName"]: m["name"] for m in generative_models}
 
        if "Gemini Pro" not in model_options:
            for m in models_data:
                if m['name'] == 'models/gemini-pro':
                    model_options[m['displayName']] = m['name']
                    break
 
        return model_options
    except Exception as e:
        st.error(f"Could not fetch AI models. Using default. Error: {e}")
        return {"Gemini Pro": "models/gemini-pro"}
 
def get_github_issues(owner, repo, token):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open"
    headers = {"Accept": "application/vnd.github.v3+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
 
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        issues = response.json()
        return [
            {
                "id": issue["id"], "number": issue["number"], "title": issue["title"],
                "body": (issue.get("body") or "No description provided.")[:500],
                "url": issue["html_url"], "labels": [label["name"] for label in issue.get("labels", [])]
            } for issue in issues
        ]
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 404: raise ValueError("Repo not found. Check URL/token.")
        elif err.response.status_code == 401: raise ValueError("Auth failed. Check token.")
        else: raise ValueError(f"HTTP error: {err}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch issues: {e}")
 
def get_file_content(owner, repo, path, token):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.v3+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
 
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 404:
            return f"File not found at path: {path}"
        response.raise_for_status()
        content = base64.b64decode(response.json()['content']).decode('utf-8', errors='ignore')
        return content[:3000]
    except Exception:
        return f"Could not retrieve or decode file: {path}"
 
def get_ai_analysis(issues, owner, repo, token, team_info, selected_model_name):
    model = genai.GenerativeModel(selected_model_name)
 
    status_placeholder = st.empty()
    status_placeholder.info("⏳ Performing initial triage to find the best candidate issues...")
 
    issues_str = "\n".join([f"- Issue #{i['number']}: {i['title']}" for i in issues])
    triage_prompt = f"""
    From the following list of GitHub issues, identify the **Top 5** that seem easiest to resolve.
    "Easiest" means they are likely self-contained bug fixes or minor features.
    Issues:
    {issues_str}
 
    Return ONLY a JSON object with a single key "selected_issues", which is a list of the issue numbers you selected.
    Example: {{"selected_issues": [123, 145, 150, 162, 180]}}
    """
 
    response = None
    try:
        response = model.generate_content(triage_prompt)
        raw_response = response.text.strip()
        json_str = raw_response[raw_response.find('{'):raw_response.rfind('}')+1]
        triage_result = json.loads(json_str)
        selected_numbers = triage_result["selected_issues"]
        selected_issues = [i for i in issues if i["number"] in selected_numbers]
    except (Exception, json.JSONDecodeError) as e:
        if response:
            st.session_state.raw_ai_response = response.text
        else:
            st.session_state.raw_ai_response = "The AI model failed to generate a response during triage. This could be due to a network issue, an invalid API key, or a content safety block."
        raise RuntimeError(f"AI triage failed. The model may have returned a malformed response. Error: {e}")
 
    final_results = []
    for issue in selected_issues:
        status_placeholder.info(f"🕵️‍♀️ Performing deep analysis for Issue #{issue['number']}...")
        time.sleep(1)
 
        status_placeholder.info(f"🧠 Identifying relevant files for Issue #{issue['number']}...")
        files_prompt = f"""
        For GitHub issue #{issue['number']}: "{issue['title']}", which 3 to 5 files in a standard web project repository are most likely relevant to implementing a fix?
        Return ONLY a JSON object with a single key "files", which is a list of file paths.
        Example: {{"files": ["src/components/Header.js", "src/styles/main.css"]}}
        """
        response = None
        try:
            response = model.generate_content(files_prompt)
            raw_response = response.text.strip()
            json_str = raw_response[raw_response.find('{'):raw_response.rfind('}')+1]
            relevant_files = json.loads(json_str)["files"]
        except (Exception, json.JSONDecodeError):
            relevant_files = []
 
        file_contents_str = ""
        if relevant_files:
            status_placeholder.info(f"📥 Fetching source code for Issue #{issue['number']}...")
            for file_path in relevant_files:
                content = get_file_content(owner, repo, file_path, token)
                file_contents_str += f"\n--- Start of {file_path} ---\n{content}\n--- End of {file_path} ---\n"
 
        status_placeholder.info(f"🔬 Simulating a fix for Issue #{issue['number']}...")
        final_analysis_prompt = f"""
        You are an expert developer. Your task is to analyze a GitHub issue with relevant code context and simulate a Pull Request plan.
 
        **Issue Details:**
        - Title: "{issue['title']}"
        - Body: "{issue['body']}"
 
        **Relevant File Contents:**
        {file_contents_str if file_contents_str else "No file content could be retrieved."}
 
        **Your Task:**
        Based on the issue and the code, provide a final analysis. Return ONLY a JSON object with the following keys:
        - `difficulty`: A new score from 1-10 based on the code.
        - `category`: The area of work (e.g., 'Frontend', 'Backend').
        - `analysis`: A short summary of the proposed fix.
        - `reasoning`: **IMPORTANT: Provide your thought process. Explain which files you analyzed and what specific lines of code or logic led you to your proposed plan.**
        - `plan`: A concise, step-by-step plan to implement the fix.
        - `assignee_level`: The best person for the job ('Intern', 'Junior', 'Mid-level', 'Senior').
 
        Example:
        {{
            "difficulty": 3,
            "category": "Frontend",
            "analysis": "The fix requires adding a new prop to the UserProfile component and updating the CSS.",
            "reasoning": "I analyzed UserProfile.js and saw that it renders user information but lacks an avatar. The issue description mentions showing an avatar. Therefore, adding a conditional 'showAvatar' prop is the logical first step. I also looked at 'styles.css' and noted the existing class for the username, which is the best place to add a margin to correctly space the new avatar.",
            "plan": "1. Add a 'showAvatar' prop to UserProfile.js.\\n2. Conditionally render the avatar based on the prop.\\n3. Add 'margin-left: 10px' to the username class in 'styles.css'.",
            "assignee_level": "Junior"
        }}
        """
        response = None
        try:
            response = model.generate_content(final_analysis_prompt)
            raw_response = response.text.strip()
            json_str = raw_response[raw_response.find('{'):raw_response.rfind('}')+1]
            analysis = json.loads(json_str)
 
            analysis.update({
                "id": issue["id"],
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["url"],
            })
            final_results.append(analysis)
        except (Exception, json.JSONDecodeError) as e:
            if response:
                st.session_state.raw_ai_response = response.text
            else:
                st.session_state.raw_ai_response = f"The AI model failed to generate a response for Issue #{issue['number']}. This could be a network issue, an invalid API key, or a content safety block."
            print(f"Deep analysis failed for issue #{issue['number']}: {e}")
            continue
 
    status_placeholder.empty()
    return {"issues": final_results}
 