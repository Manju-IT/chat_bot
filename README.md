**TalentScout Hiring Assistant Chatbot**

**Project Overview**
The TalentScout Hiring Assistant is an AI-powered chatbot designed to streamline the initial screening process for recruitment agencies. This chatbot engages with candidates in natural conversation to:

-	Collect essential candidate information (contact details, experience, etc.)
-	Identify the candidate's technical skills and expertise
-	Generate relevant technical questions based on their declared tech stack
-	Provide a smooth, conversational experience that feels human-like

I built this to demonstrate how AI can handle the repetitive early stages of technical screening, freeing up human recruiters for more complex evaluations. The chatbot maintains context throughout the conversation and gracefully handles unexpected inputs.

**Installation Instructions**

Getting this running locally is straightforward:

1. Clone the repository
    bash
   git clone https://github.com/Manju-IT/chat_bot.git
   cd talentscout-chatbot

2. Set up a virtual environment (recommended)  
    bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
3. Install dependencies
    bash
   pip install -r requirements.txt

4. Run the application
    bash
   streamlit run hiring_assistant.py
The app will automatically open in your default browser at `http://localhost:8501/`
AWS live demo Link :- http://13.233.126.150:8501/  ## You can directly run this anywhere. ## Ignore model loading Warning 

**Usage Guide**
Using the chatbot couldn't be simpler:
1. Start chatting - The bot will initiate the conversation automatically
2. Follow the prompts - Provide the requested information when asked
3. Tech stack questions- After listing your skills, you'll get relevant technical questions
4. Exit anytime - Just type "exit", "quit", or "bye" to end the session

Pro tip: The bot understands natural language - you don't need to be overly formal in your responses.

**Technical Details**
 Core Technologies
- Python 3.10+ - The backbone of the application
- Streamlit- For the clean, interactive web interface
- HuggingFace Transformers - Provides the DialoGPT-small language model
- Regex - For input validation (emails, phone numbers)

**Architectural Decisions**

I opted for a modular conversation flow design where:
-	Each "step" in the screening process has a dedicated handler
-	Session state maintains context between interactions
-	The UI updates dynamically based on conversation progress
The DialoGPT-small model was chosen because:
-	It's lightweight enough to run locally
-	Provides decent conversational abilities
-	Doesn't require expensive API calls

**Prompt Design Strategy**
The conversation follows a carefully designed flow:
1. Information Gathering
   Uses direct but friendly prompts to collect candidate data  
   Example: "Nice to meet you, [Name]! Could you please share your email address?"
2. Tech Stack Handling
   Candidates can list skills naturally (e.g., "Python, JavaScript, React")  
   The system then selects appropriate questions from its database
3. Error Recovery  
   Friendly re-prompts for invalid inputs:  
   "That doesn't look like a valid email. Could you try again?"
4. Context Maintenance
   The bot remembers previous answers and uses them naturally in follow-ups

**Challenges & Solutions**

Challenge 1: Model Limitations
The smaller DialoGPT model sometimes generates odd responses compared to larger models like GPT-3.
Solution:
I implemented a structured conversation flow that constrains the model's responses while still allowing natural interaction.

Challenge 2: Tech Question Generation
Initially wanted dynamic question generation, but this required expensive APIs.
Solution:
Built a comprehensive question database covering common technologies, with fallback generic questions for uncommon tech.

Challenge 3: Input Validation
Need to validate emails, phone numbers, etc. without breaking conversation flow.
Solution:
Used regex patterns with friendly error messages that guide candidates to provide valid information.

Challenge 4: State Management
Keeping track of where candidates are in the screening process.
Solution:
Implemented a step-based system using Streamlit's session state features.
**
Final Thoughts**

This project was a great exercise in balancing AI capabilities with practical constraints. While there's always room for improvement (I'd love to add multilingual support next!), the current version provides a solid foundation for automated technical screening that actually feels human.
