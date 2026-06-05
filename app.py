import streamlit as st
import pandas as pd
import ollama
import json
from database import init_db, save_interview, get_all_interviews

# Initialize Database
init_db()

# Page Config
st.set_page_config(page_title="AI Interview Assistant", page_icon="🤖", layout="wide")

# Load CSS
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# State Initialization
if "page" not in st.session_state:
    st.session_state.page = "Setup"
if "history" not in st.session_state:
    st.session_state.history = []
if "free_chat_history" not in st.session_state:
    st.session_state.free_chat_history = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "tech" not in st.session_state:
    st.session_state.tech = ""
if "diff" not in st.session_state:
    st.session_state.diff = ""

def reset_interview():
    st.session_state.history = []
    st.session_state.question_count = 0
    st.session_state.page = "Setup"

# Helper for Ollama Chat
def get_ai_response(prompt, system_prompt="You are an expert technical interviewer."):
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.history:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = ollama.chat(model='llama3', messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

# Sidebar Navigation
st.sidebar.title("Navigation")
nav = st.sidebar.radio("Go to", ["Interview Session", "Dashboard", "Free Chat"])

if nav == "Dashboard":
    st.session_state.page = "Dashboard"
elif nav == "Free Chat":
    st.session_state.page = "Free Chat"
elif nav == "Interview Session" and st.session_state.page in ["Dashboard", "Free Chat"]:
    st.session_state.page = "Setup"

# Header
st.markdown("""
<div class="interview-header">
    <h1>🤖 AI Interview Assistant</h1>
    <p>Practice your tech interviews with Llama 3</p>
</div>
""", unsafe_allow_html=True)


if st.session_state.page == "Setup":
    st.subheader("1. Interview Setup")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.tech = st.selectbox("Technology", ["Python", "JavaScript", "React Native", "Flutter", "HR Interview"])
    with col2:
        st.session_state.diff = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
    
    if st.button("Start Interview"):
        st.session_state.page = "Interview"
        st.session_state.history = []
        st.session_state.question_count = 1
        st.rerun()

elif st.session_state.page == "Interview":
    st.subheader(f"{st.session_state.tech} Interview - {st.session_state.diff} Level")
    
    # Generate First Question if empty
    if not st.session_state.history:
        with st.spinner("Generating first question..."):
            system_prompt = f"You are a Senior Technical Interviewer conducting a {st.session_state.diff} level interview on {st.session_state.tech}. Ask ONE clear, professional interview question. Do not provide the answer."
            first_q = get_ai_response("Please ask the first interview question.", system_prompt)
            st.session_state.history.append({"role": "assistant", "content": first_q})
    
    # Display Chat History
    for msg in st.session_state.history:
        role_class = "ai-message" if msg["role"] == "assistant" else "user-message"
        st.markdown(f"<div class='{role_class}'><b>{'🤖 AI' if msg['role'] == 'assistant' else '👤 You'}:</b> {msg['content']}</div>", unsafe_allow_html=True)
    
    # Input for User Answer
    if st.session_state.question_count <= 5:
        st.write(f"**Question {st.session_state.question_count} of 5**")
        user_answer = st.text_area("Your Answer:", key=f"ans_{st.session_state.question_count}")
        
        if st.button("Submit Answer"):
            if user_answer.strip():
                st.session_state.history.append({"role": "user", "content": user_answer})
                
                if st.session_state.question_count < 5:
                    with st.spinner("Analyzing answer and generating next question..."):
                        system_prompt = f"You are a Senior Technical Interviewer. The user is interviewing for {st.session_state.tech} ({st.session_state.diff}). Evaluate their last answer briefly, then ask the NEXT interview question. Only ask one question. Do not ask more than one. Be concise."
                        next_q = get_ai_response("Here is my answer. Please give brief feedback and ask the next question.", system_prompt)
                        st.session_state.history.append({"role": "assistant", "content": next_q})
                        st.session_state.question_count += 1
                        st.rerun()
                else:
                    st.session_state.page = "Feedback"
                    st.rerun()
            else:
                st.warning("Please enter an answer before submitting.")

elif st.session_state.page == "Feedback":
    st.subheader("Final Feedback")
    
    if "feedback_generated" not in st.session_state:
        with st.spinner("Analyzing your entire interview and generating final feedback..."):
            system_prompt = f"You are a Senior Technical Interviewer. Review the entire interview history for {st.session_state.tech} ({st.session_state.diff}). Provide a JSON response with the following format EXACTLY: {{\"score\": <integer 1-10>, \"strengths\": \"<text>\", \"weaknesses\": \"<text>\", \"improvement\": \"<text>\"}}. Do not include any other text outside the JSON."
            feedback_raw = get_ai_response("The interview is complete. Please provide the final assessment in the requested JSON format.", system_prompt)
            
            try:
                # Try to parse JSON from the response
                start_idx = feedback_raw.find("{")
                end_idx = feedback_raw.rfind("}") + 1
                feedback_json = json.loads(feedback_raw[start_idx:end_idx])
                
                st.session_state.feedback_data = feedback_json
                st.session_state.feedback_generated = True
                
                # Save to DB
                save_interview(
                    st.session_state.tech, 
                    st.session_state.diff, 
                    feedback_json.get("score", 0),
                    feedback_json.get("strengths", ""),
                    feedback_json.get("weaknesses", "")
                )
                
            except Exception as e:
                st.error(f"Failed to parse AI feedback. Make sure you use a capable model. Raw output: {feedback_raw}")
    
    if "feedback_data" in st.session_state:
        data = st.session_state.feedback_data
        
        st.markdown(f"""
        <div class="metric-card" style="background-color: #2b313e; border: 2px solid #4b6cb7;">
            <h3>Overall Score</h3>
            <h2 style="font-size: 3rem; color: #4b6cb7;">{data.get('score', 0)} / 10</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strengths")
            st.info(data.get("strengths", "N/A"))
        with col2:
            st.markdown("### 📉 Weaknesses")
            st.warning(data.get("weaknesses", "N/A"))
            
        st.markdown("### 🚀 Improvement Suggestions")
        st.success(data.get("improvement", "N/A"))
        
        if st.button("Start New Interview"):
            del st.session_state.feedback_generated
            del st.session_state.feedback_data
            reset_interview()
            st.rerun()

elif st.session_state.page == "Dashboard":
    st.subheader("Interview Dashboard")
    
    interviews = get_all_interviews()
    
    if not interviews:
        st.info("No interviews recorded yet. Go to 'Interview Session' to start one!")
    else:
        df = pd.DataFrame(interviews, columns=["ID", "Date", "Technology", "Difficulty", "Score", "Strengths", "Weaknesses"])
        
        total_interviews = len(df)
        avg_score = df["Score"].mean()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Interviews</h3>
                <h2>{total_interviews}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Average Score</h3>
                <h2>{avg_score:.1f} / 10</h2>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### Interview History")
        
        # Display as a clean dataframe
        display_df = df[["Date", "Technology", "Difficulty", "Score"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("### Detailed History")
        for _, row in df.iterrows():
            with st.expander(f"{row['Date']} - {row['Technology']} ({row['Difficulty']}) - Score: {row['Score']}/10"):
                st.write(f"**Strengths:** {row['Strengths']}")
                st.write(f"**Weaknesses:** {row['Weaknesses']}")

elif st.session_state.page == "Free Chat":
    st.subheader("💬 Free Chat with AI")
    st.markdown("Practice, ask questions, or just chat normally with Llama 3.")
    
    # Display chat messages from history
    for message in st.session_state.free_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.free_chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = ollama.chat(model='llama3', messages=st.session_state.free_chat_history)
                    reply = response['message']['content']
                    st.markdown(reply)
                    st.session_state.free_chat_history.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error connecting to Ollama: {str(e)}")
