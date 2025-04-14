import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import random
from collections import defaultdict
import re
import json
from pathlib import Path
import os


os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"

st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
        return tokenizer, model
    except Exception as e:
        st.warning(f"Model loading warning: {str(e)}")
        st.info("Using simple text responses instead of AI model.")
        return None, None

tokenizer, model = load_model()

TECH_QUESTIONS = {
    "python": [
        "Explain the difference between lists and tuples in Python.",
        "What are decorators in Python and how would you use them?",
        "How does Python's garbage collection work?",
        "Explain the Global Interpreter Lock (GIL) in Python."
    ],
    "java": [
        "Explain the difference between ArrayList and LinkedList in Java.",
        "What is the Java Memory Model?",
        "How does garbage collection work in Java?",
        "What are Java streams and how would you use them?"
    ],
    "javascript": [
        "Explain the event loop in JavaScript.",
        "What are closures in JavaScript?",
        "Explain the difference between == and === in JavaScript.",
        "What are promises and how do they work?"
    ],
    "react": [
        "Explain the virtual DOM in React.",
        "What are React hooks and how do you use them?",
        "Explain the component lifecycle in React.",
        "What is JSX and how does it work?"
    ],
    "django": [
        "Explain Django's MTV architecture.",
        "What are Django middleware and how would you use them?",
        "How does Django's ORM work?",
        "Explain Django's authentication system."
    ],
    "sql": [
        "Explain the difference between INNER JOIN and LEFT JOIN.",
        "What are database indexes and when would you use them?",
        "Explain database normalization.",
        "What are stored procedures and when would you use them?"
    ]
}

if 'candidate_data' not in st.session_state:
    st.session_state.candidate_data = defaultdict(str)

def load_candidate_data():
    try:
        if Path("candidate_data.json").exists():
            with open("candidate_data.json", "r") as f:
                return defaultdict(str, json.load(f))
    except Exception:
        pass
    return defaultdict(str)

def save_candidate_data(data):
    try:
        structured_data = {
            "personal_info": {
                "full_name": data.get("full_name", ""),
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "years_experience": data.get("years_experience", ""),
                "desired_position": data.get("desired_position", ""),
                "location": data.get("location", ""),
                "tech_stack": data.get("tech_stack", ""),
            },
            "technical_qa": {}
        }

        tech_list = data.get("tech_stack", "").split(", ") if data.get("tech_stack") else []
        for tech in tech_list:
            structured_data["technical_qa"][tech] = []
            i = 1
            while f"{tech}_q{i}" in data and f"{tech}_a{i}" in data:
                structured_data["technical_qa"][tech].append({
                    "question": data[f"{tech}_q{i}"],
                    "answer": data[f"{tech}_a{i}"]
                })
                i += 1

        with open("candidate_data.json", "w") as f:
            json.dump(structured_data, f, indent=4)
          
        with open("candidate_data.txt", "w") as f:
            f.write("=== CANDIDATE APPLICATION DATA ===\n\n")
            f.write("=== PERSONAL INFORMATION ===\n")
            for key, value in structured_data["personal_info"].items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\n=== TECHNICAL QUESTIONS & ANSWERS ===\n")
            for tech, qa_list in structured_data["technical_qa"].items():
                f.write(f"\nTechnology: {tech}\n")
                for i, qa in enumerate(qa_list, 1):
                    f.write(f"\nQuestion {i}: {qa['question']}\n")
                    f.write(f"Answer {i}: {qa['answer']}\n")

    except Exception as e:
        st.error(f"Error saving data: {e}")

st.markdown("""
    <style>
        .stApp {
            background-color: #13344d;
        }
        .stChatFloatingInputContainer {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 6px 8px rgba(0, 0, 0.1, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.current_step = "greeting"
    st.session_state.tech_stack = []
    st.session_state.questions_asked = 0
    st.session_state.current_tech = ""
    st.session_state.collected_data = False
    st.session_state.conversation_active = True

def generate_tech_questions(tech):
    tech_lower = tech.lower()
    if tech_lower in TECH_QUESTIONS:
        return random.sample(TECH_QUESTIONS[tech_lower], min(3, len(TECH_QUESTIONS[tech_lower])))
    else:
        return [
            f"What experience do you have with {tech}?",
            f"Can you explain a challenging project you've worked on using {tech}?",
            f"What are the key features of {tech} that you find most valuable?"
        ]

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

def is_valid_phone(phone):
    pattern = r"^[\d\s\+\-\(\)]{7,15}$"
    return re.match(pattern, phone)

def display_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f'<div class="chat-message {"assistant-message" if message["role"] == "assistant" else "user-message"}">{message["content"]}</div>', 
                       unsafe_allow_html=True)

def handle_conversation(user_input):
    if not st.session_state.conversation_active:
        return
    
 
    exit_keywords = ["exit", "quit", "bye", "goodbye", "stop", "end"]
    if any(keyword in user_input.lower() for keyword in exit_keywords):
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Thank you for your time! Your information has been recorded. A recruiter will review your details and get back to you soon. Have a great day!"
        })
        st.session_state.conversation_active = False
        save_candidate_data(st.session_state.candidate_data)
        return
 
    if st.session_state.current_step == "greeting":
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I'm TalentScout's Hiring Assistant. I'll help with the initial screening process. First, I need to collect some basic information from you. May I have your full name?"
        })
        st.session_state.current_step = "get_name"
    
    elif st.session_state.current_step == "get_name":
        st.session_state.candidate_data["full_name"] = user_input
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Nice to meet you, {user_input}! Could you please share your email address?"
        })
        st.session_state.current_step = "get_email"
    
    elif st.session_state.current_step == "get_email":
        if is_valid_email(user_input):
            st.session_state.candidate_data["email"] = user_input
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Thank you! Could you also provide your phone number?"
            })
            st.session_state.current_step = "get_phone"
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "That doesn't look like a valid email address. Please enter a valid email (e.g., name@example.com)."
            })
    
    elif st.session_state.current_step == "get_phone":
        if is_valid_phone(user_input):
            st.session_state.candidate_data["phone"] = user_input
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Great! How many years of professional experience do you have in your field?"
            })
            st.session_state.current_step = "get_experience"
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Please enter a valid phone number (e.g., +1 123-456-7890 or 0123456789)."
            })
    
    elif st.session_state.current_step == "get_experience":
        if user_input.isdigit():
            st.session_state.candidate_data["years_experience"] = user_input
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Thank you. What position(s) are you applying for?"
            })
            st.session_state.current_step = "get_position"
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Please enter a valid number for years of experience (e.g., 3)."
            })
    
    elif st.session_state.current_step == "get_position":
        st.session_state.candidate_data["desired_position"] = user_input
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Got it! What is your current location (city and country)?"
        })
        st.session_state.current_step = "get_location"
    
    elif st.session_state.current_step == "get_location":
        st.session_state.candidate_data["location"] = user_input
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Thanks! Now, could you list the technologies in your tech stack? Please separate them with commas (e.g., Python, JavaScript, React)."
        })
        st.session_state.current_step = "get_tech_stack"
    
    elif st.session_state.current_step == "get_tech_stack":
        tech_list = [tech.strip() for tech in user_input.split(",") if tech.strip()]
        if tech_list:
            st.session_state.tech_stack = tech_list
            st.session_state.candidate_data["tech_stack"] = ", ".join(tech_list)
            
            st.session_state.current_tech = st.session_state.tech_stack[0]
            questions = generate_tech_questions(st.session_state.current_tech)
            st.session_state.current_questions = questions
            st.session_state.questions_asked = 0
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Great! Let's start with some technical questions about {st.session_state.current_tech}. Here's the first question:\n\n{questions[0]}"
            })
            st.session_state.current_step = "ask_technical"
        else:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Please list at least one technology in your tech stack (e.g., Python, JavaScript, React)."
            })
    
    elif st.session_state.current_step == "ask_technical":
        tech = st.session_state.current_tech
        question = st.session_state.current_questions[st.session_state.questions_asked]
        
        question_num = st.session_state.questions_asked + 1
        st.session_state.candidate_data[f"{tech}_q{question_num}"] = question
        st.session_state.candidate_data[f"{tech}_a{question_num}"] = user_input
        
        st.session_state.questions_asked += 1
        
        if st.session_state.questions_asked < len(st.session_state.current_questions):
            next_question = st.session_state.current_questions[st.session_state.questions_asked]
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Thanks for your answer! Next question about {tech}:\n\n{next_question}"
            })
        else:
            current_index = st.session_state.tech_stack.index(st.session_state.current_tech)
            if current_index + 1 < len(st.session_state.tech_stack):
                st.session_state.current_tech = st.session_state.tech_stack[current_index + 1]
                st.session_state.current_questions = generate_tech_questions(st.session_state.current_tech)
                st.session_state.questions_asked = 0
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Great! Now let's move on to {st.session_state.current_tech}. Here's your first question:\n\n{st.session_state.current_questions[0]}"
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Thanks for answering the questions! We've collected all the necessary information."
                })
                st.session_state.current_step = "end_conversation"
                st.session_state.collected_data = True
                save_candidate_data(st.session_state.candidate_data)

def main():
    st.markdown('<div class="header">TalentScout Hiring Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Initial Candidate Screening Chatbot</div>', unsafe_allow_html=True)
    

    progress_steps = {
        "greeting": 0,
        "get_name": 1,
        "get_email": 2,
        "get_phone": 3,
        "get_experience": 4,
        "get_position": 5,
        "get_location": 6,
        "get_tech_stack": 7,
        "ask_technical": 8,
        "complete": 9
    }
    
    current_progress = progress_steps.get(st.session_state.current_step, 0) / 9.0
    
    st.markdown(f"""
        <div class="progress-bar">
            <div class="progress" style="width: {current_progress * 100}%"></div>
        </div>
    """, unsafe_allow_html=True)
    
    display_chat()
    
   
    if st.session_state.conversation_active:
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Thinking..."):
                handle_conversation(prompt)
            st.rerun()
    
    
    if st.session_state.collected_data:
        try:
            
            with open("candidate_data.json", "r") as f:
                structured_data = json.load(f)
            
            download_content = "=== CANDIDATE APPLICATION DATA ===\n\n"
            download_content += "=== PERSONAL INFORMATION ===\n"
            for key, value in structured_data["personal_info"].items():
                download_content += f"{key.replace('_', ' ').title()}: {value}\n"
            
            download_content += "\n=== TECHNICAL QUESTIONS & ANSWERS ===\n"
            for tech, qa_list in structured_data["technical_qa"].items():
                download_content += f"\nTechnology: {tech}\n"
                for i, qa in enumerate(qa_list, 1):
                    download_content += f"\nQuestion {i}: {qa['question']}\n"
                    download_content += f"Answer {i}: {qa['answer']}\n"
            
           
            st.download_button(
                label="Download Complete Application Data",
                data=download_content,
                file_name="candidate_application_data.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error loading candidate data: {e}")

if __name__ == "__main__":
    main()