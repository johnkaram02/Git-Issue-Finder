import streamlit as st
import google.generativeai as genai
from backend import get_available_models, get_github_issues, get_ai_analysis

st.set_page_config(
    page_title="Git Issue Finder",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🤖 Git Issue Finder")
st.markdown("An AI-powered assistant that analyzes repository code to rank and assign GitHub issues.")

if 'status' not in st.session_state: st.session_state.status = 'idle'
if 'results' not in st.session_state: st.session_state.results = []
if 'error_message' not in st.session_state: st.session_state.error_message = None
if 'raw_ai_response' not in st.session_state: st.session_state.raw_ai_response = None

with st.form(key="repo_form"):
    repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/streamlit/streamlit")
    token = st.text_input("GitHub Personal Access Token (if private)", type="password")
    
    user_api_key = st.text_input("Google AI Studio API Key", type="password")
    st.markdown(
        """<small>You can get your own key from <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a>.</small>""",
        unsafe_allow_html=True
    )
    
    team_info = st.text_input("Team Composition (Optional)", placeholder="e.g., 1 intern, 2 juniors, 1 senior")
    
    model_display_name = st.selectbox(
        "Choose AI Model",
        options=list(get_available_models(user_api_key).keys() if user_api_key else ["Enter API Key to load models"]),
        index=0
    )
    
    st.markdown(
        """<small>For private repos, generate a Token (classic) with the <strong>`repo`</strong> scope. 
        <a href="https://github.com/settings/tokens/new?scopes=repo&description=GitIssueFinder" target="_blank">
        Click here to create one.</a></small>""", unsafe_allow_html=True
    )
    debug_mode = st.checkbox("Enable Debug Mode")
    st.write("")
    submit_button = st.form_submit_button("Analyze Repo Issues", use_container_width=True)

if submit_button:
    if not repo_url:
        st.error("Please enter a GitHub repository URL.")
    elif not user_api_key:
        st.error("Please enter your Google AI Studio API Key.")
    else:
        st.session_state.status = 'loading'
        st.session_state.results = []
        st.session_state.error_message = None
        st.session_state.raw_ai_response = None
        
        try:
            genai.configure(api_key=user_api_key)
            available_models = get_available_models(user_api_key)
            selected_model_name = available_models[model_display_name]

            parts = repo_url.strip("/").split("/")
            owner, repo = parts[-2], parts[-1]
            
            with st.spinner("Connecting to repository and fetching issues..."):
                issues = get_github_issues(owner, repo, token or None)
            
            if not issues:
                st.warning("No open issues found in this repository.")
                st.session_state.status = 'idle'
                st.stop()
            
            analysis_results = get_ai_analysis(issues, owner, repo, token or None, team_info, selected_model_name)

            st.session_state.results = analysis_results.get("issues", [])
            st.session_state.status = 'success'

        except (ValueError, RuntimeError, Exception) as e:
            st.session_state.error_message = str(e)
            st.session_state.status = 'error'

if st.session_state.status == 'error':
    st.error(f"**An error occurred:** {st.session_state.error_message}")
    if debug_mode and st.session_state.raw_ai_response:
        st.subheader("Raw AI Response (for debugging):")
        st.code(st.session_state.raw_ai_response, language=None)

if st.session_state.status == 'success':
    st.success("✅ Analysis complete! Here are the recommended assignments:")
    st.markdown("---")
    
    if not st.session_state.results:
        st.warning("The AI analysis did not return any issues to display.")
    
    for issue in st.session_state.results:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"#### [{issue['title']} (#{issue['number']})]({issue['url']})")
            with col2:
                st.markdown(f"**Assignee:** <span style='background-color:#EEEEEE; border-radius:5px; padding: 3px 8px;'>{issue.get('assignee_level', 'N/A')}</span>", unsafe_allow_html=True)

            st.markdown(f"**AI Analysis:** *{issue['analysis']}*")
            
            if issue.get("reasoning"):
                with st.expander("Show AI Thought Process..."):
                    st.markdown(issue["reasoning"])
            
            if issue.get("plan"):
                st.markdown("**Proposed Plan:**")
                formatted_plan = issue['plan'].replace('\\n', '\n')
                st.code(formatted_plan, language='markdown')

            st_col1, st_col2 = st.columns(2)
            with st_col1:
                st.markdown(f"**Difficulty:** `{issue['difficulty']}/10`")
            with st_col2:
                st.markdown(f"**Category:** `{issue['category']}`")
        st.write("")
