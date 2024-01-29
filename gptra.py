import streamlit as st
import openai
import datetime
import yaml
from yaml.loader import SafeLoader
import pypandoc
import os
import fitz  # PyMuPDF
import pyperclip

# Load configuratio+

api_key = st.secrets["OPENAI_API_KEY"]

# Initialize the response variable
response = None

# n from 'users.yaml' file
with open('users.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Function to log interactions to a file
def log_interaction(user_code, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} - User: {user_code} - {message}\n")
        
# Define a function to generate and display response
def generate_and_display_response():
    # Check if there is a response to display
    if response:
        if use_case != "Chat":
            st.markdown(response)

        # Create a row of columns for the copy and download buttons
        col1, col2, col3 = st.columns(3)

        # Add a button for copying the Markdown response to the clipboard with an icon
        with col1:
            copy_button = st.button('📋Copy Markdown')  # Clipboard icon
            if copy_button:
                pyperclip.copy(response)
                st.success('Markdown copied to clipboard!')

        # Add buttons for downloading the response
        with col2:
            download_md_button = st.download_button(
                label="📥Download Markdown",  # Download icon
                data=response,
                file_name="response.md",
                mime="text/markdown"
                #help="Download Markdown"
            )

        # Convert Markdown to Word and get the bytes
        word_response = markdown_to_word(response)

        # Add a button for downloading the Word response
        with col3:
            download_docx_button = st.download_button(
                label="📄Download Word File",  # Document icon
                data=word_response,
                file_name="response.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                #help="Download Word File"
            )


# Default stuff

s5 = "You are an assistant professor of business analytics at Wichita State University. Your name is Dr. Murtaza Nasir. You write very polite and concise emails. You sign off your emails with Murtaza."

# Function to convert PDF to Markdown using PyMuPDF
def pdf_to_markdown(pdf_file):
    markdown_text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            markdown_text += page.get_text("markdown")
    return markdown_text

# Function to convert Word to Markdown using pypandoc
def word_to_markdown(docx_file_path):
    if not os.path.exists(docx_file_path):
        raise FileNotFoundError(f"The file {docx_file_path} was not found.")
    try:
        return pypandoc.convert_file(docx_file_path, 'md')
    except Exception as e:
        st.error(f"An error occurred during file conversion: {e}")
        raise

# Set the page configuration, including title and favicon
st.set_page_config(page_title="Academic Helper", page_icon="📄")

# Set log file path
log_file_path = "productivity_helper_log.txt"

streaming_completed = st.session_state.get("streaming_completed", True)
if 'name' not in st.session_state:
    st.session_state['name'] = 'default_user'

if 'latest_response' not in st.session_state:
    st.session_state['latest_response'] = ""
    
# Initialize the dictionaries for custom prompts
if 'custom_intro_texts' not in st.session_state:
    st.session_state['custom_intro_texts'] = {}
if 'custom_prompts' not in st.session_state:
    st.session_state['custom_prompts'] = {}
    
if 'use_chat_history' not in st.session_state:
    st.session_state['use_chat_history'] = False
if 'system_prompt' not in st.session_state:
    st.session_state['system_prompt'] = "You are an expert data scientist and machine learning academic. You help researchers with their research work. You generate detailed responses supported by logical reasoning and factual arguments."
if 'system_prompt2' not in st.session_state: #for reviewer 
    st.session_state['system_prompt2'] = "You are an expert data scientist and machine learning academic and have reviewed many papers in {journal}. You help researchers with their response and rebuttal process for journal publications. You generate detailed responses supported by logical reasoning and factual arguments."
if 'system_prompt3' not in st.session_state: 
    st.session_state['system_prompt3'] = "You are an expert data scientist and machine learning academic and have reviewed many papers in {journal}. You help researchers with their writing process for journal publications. You generate detailed responses supported by logical reasoning and factual arguments."
if 'system_prompt4' not in st.session_state: 
    st.session_state['system_prompt4'] = "You are an expert {language} programmer."
if 'system_prompt5' not in st.session_state: 
    st.session_state['system_prompt5'] = s5
    
# Define the default prompts for each use case
if 'default_prompts' not in st.session_state:
    st.session_state['default_prompts'] = {
        'system_prompt': "You are an expert data scientist and machine learning academic. You help researchers with their research work. You generate detailed responses supported by logical reasoning and factual arguments.",
        'system_prompt2': "You are an expert data scientist and machine learning academic and have reviewed many papers in {journal}. You help researchers with their response and rebuttal process for journal publications. You generate detailed responses supported by logical reasoning and factual arguments.",
        'system_prompt3': "You are an expert data scientist and machine learning academic and have reviewed many papers in {journal}. You help researchers with their writing process for journal publications. You generate detailed responses supported by logical reasoning and factual arguments.",
        'system_prompt4': "You are an expert {language} programmer.",
        'system_prompt5': s5,
        'intro_text': "Following is my research paper that I submitted to the {journal} for review and acceptance:",
        'intro_text2': "Following is my research paper targeting {journal}:",
        'intro_text3': "Following is some {language} code:",
        'intro_text4': "Following is an email exchange with the most recent emails {order}:",
        'reviewer_comment_intro': "A reviewer commented the following:",
        'custom_prompt_defaults': {  # We'll use this to reset Custom Prompt Generator textboxes
            f'intro_text_{i}': "" for i in range(5)
        }
    }
if 'intro_text' not in st.session_state:
    st.session_state['intro_text'] = "Following is my research paper that I submitted to the {journal} for review and acceptance:"
if 'intro_text2' not in st.session_state:
    st.session_state['intro_text2'] = "Following is my research paper targeting {journal}:"
if 'intro_text3' not in st.session_state:
    st.session_state['intro_text3'] = "Following is some {language} code:"
if 'intro_text4' not in st.session_state:
    st.session_state['intro_text4'] = "Following is an email exchange with the most recent emails {order}:"
if 'reviewer_comment_intro' not in st.session_state:
    st.session_state['reviewer_comment_intro'] = "A reviewer commented the following:"

    
# Define a function to reset the prompt to its default value
def reset_prompt(use_case):
    if use_case == 'Reviewer Response Generator':
        st.session_state['system_prompt2'] = st.session_state['default_prompts']['system_prompt2']
        st.session_state['intro_text'] = st.session_state['default_prompts']['intro_text']
        st.session_state['reviewer_comment_intro'] = st.session_state['default_prompts']['reviewer_comment_intro']
    if use_case == 'Paper Writing':
        st.session_state['system_prompt3'] = st.session_state['default_prompts']['system_prompt3']
        st.session_state['intro_text2'] = st.session_state['default_prompts']['intro_text2']
    if use_case == 'Email':
        st.session_state['system_prompt5'] = st.session_state['default_prompts']['system_prompt5']
        st.session_state['intro_text4'] = st.session_state['default_prompts']['intro_text4']
    if use_case == 'Programming':
        st.session_state['system_prompt4'] = st.session_state['default_prompts']['system_prompt4']
        st.session_state['intro_text3'] = st.session_state['default_prompts']['intro_text3']
    elif use_case == 'Custom Prompt Generator':
        for i in range(5):
            st.session_state[f'intro_text_{i}'] = st.session_state['default_prompts']['custom_prompt_defaults'][f'intro_text_{i}']
    else:
        st.session_state['system_prompt'] = st.session_state['default_prompts']['system_prompt']
    st.rerun()
    
# Define the reset function
def reset_all():
    if use_case == 'Chat':
        st.session_state.messages = [{"role": "system", "content": st.session_state['system_prompt']}]
        st.rerun()
    else:  # General Use or any other use case
        reset_prompt(use_case)

# Sidebar dropdown for use case selection
use_case = st.sidebar.selectbox("Select Use Case", ['General Use', 'Reviewer Response Generator', 'Paper Writing', 'Email', 'Programming', 'Chat', 'Custom Prompt Generator'])  # Added 'Custom Prompt Generator'

# At the beginning of your Streamlit app, after initializing session state variables
if 'previous_use_case' not in st.session_state:
    st.session_state['previous_use_case'] = use_case

# Before displaying the response or in the section where you handle use case changes
if use_case != st.session_state['previous_use_case']:
    # Clear the latest response because the use case has changed
    st.session_state['latest_response'] = ""
    # Update the previous use case to the current one for future checks
    st.session_state['previous_use_case'] = use_case
    # Use st.experimental_rerun() if you need to refresh the page and reflect changes
    st.rerun()

# Create sidebar dropdown for model selection
model_choice = st.sidebar.selectbox("Select AI Model", ['Gpt3.5 turbo', 'Gpt4', 'Local Model', 'Local Model 2'])  # Added 'Local Model' option

# Sidebar inputs for model parameters
max_tokens = st.sidebar.number_input("Max Tokens", min_value=1, max_value=10000, value=1000)
temperature = st.sidebar.number_input("Temperature", min_value=0.0, max_value=5.0, value=0.7, format="%.2f")
    
if use_case == 'Custom Prompt Generator':
    st.session_state['system_prompt'] = st.sidebar.text_area(f"System Prompt for {use_case}", height=150, value=st.session_state['system_prompt'])
elif use_case == 'Reviewer Response Generator':
    st.session_state['system_prompt2'] = st.sidebar.text_area(f"System Prompt for {use_case}", height=150, value=st.session_state['system_prompt2'])
elif use_case == 'Paper Writing':
    st.session_state['system_prompt3'] = st.sidebar.text_area(f"System Prompt for {use_case}", height=150, value=st.session_state['system_prompt3'])
elif use_case == 'Email':
    st.session_state['system_prompt5'] = st.sidebar.text_area(f"System Prompt for {use_case}", height=150, value=st.session_state['system_prompt5'])
elif use_case == 'Programming':
    st.session_state['system_prompt4'] = st.sidebar.text_area(f"System Prompt for {use_case}", height=150, value=st.session_state['system_prompt4'])

# Sidebar textbox for specifying the journal only in Reviewer Response Generator use case
if use_case == 'Reviewer Response Generator':
    journal = st.sidebar.text_input("Specify Journal", "")
    st.sidebar.header("Customize Prompt")
    st.session_state['intro_text'] = st.sidebar.text_area("Introduction Text", value=st.session_state['intro_text'], height=75)
    st.session_state['reviewer_comment_intro'] = st.sidebar.text_area("Reviewer Comment Intro", value=st.session_state['reviewer_comment_intro'], height=75)
elif use_case == 'Paper Writing':
    journal = st.sidebar.text_input("Specify Journal", "")
    st.sidebar.header("Customize Prompt")
    st.session_state['intro_text2'] = st.sidebar.text_area("Introduction Text", value=st.session_state['intro_text2'], height=75)
elif use_case == 'Email':
    # Checkbox for determining the order of emails
    checkbox_state = st.sidebar.checkbox("Latest emails first", value=True)
    # Set the order based on the checkbox state
    order = 'first' if checkbox_state else 'last'
    st.sidebar.header("Customize Prompt")
    st.session_state['intro_text4'] = st.sidebar.text_area("Introduction Text", value=st.session_state['intro_text4'], height=75)
elif use_case == 'Programming':
    language = st.sidebar.text_input("Specify Language", "")
    st.sidebar.header("Customize Prompt")
    st.session_state['intro_text3'] = st.sidebar.text_area("Introduction Text", value=st.session_state['intro_text3'], height=75)
else:
    journal = None

uploaded_file = st.sidebar.file_uploader("Upload a file", type=['pdf', 'docx'])

# Process the uploaded file and display the content
if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == 'pdf':
        markdown_content = pdf_to_markdown(uploaded_file)
    elif file_extension == 'docx':
        # Save temporary file to disk to use with pypandoc
        temp_file_path = f'temp_{uploaded_file.name}'
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            # Convert the temporary file to markdown
            markdown_content = word_to_markdown(temp_file_path)
        except FileNotFoundError as fnf_error:
            st.error(f"File not found: {fnf_error}")
        except Exception as conv_error:
            st.error(f"Conversion error: {conv_error}")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    # Display the converted content as markdown and add a copy button
    st.sidebar.button('Copy to Clipboard', key='copy_markdown', on_click=lambda: pyperclip.copy(markdown_content))
    
# Function to convert Markdown to Word document using pypandoc
def markdown_to_word(markdown_text):
    output = pypandoc.convert_text(markdown_text, 'docx', format='md', outputfile="output.docx")
    with open("output.docx", "rb") as file:
        return file.read()

# Define a function to get a response from the selected model

def get_response(model_choice, journal, paper_content, reviewer_comment, response_idea, general_prompt, max_tokens, temperature, use_case):
    if model_choice == 'Local Model':
        # Instantates a local OpenAI client
        client = openai.OpenAI(api_key='dummy', base_url='http://192.168.blah.blah:5000/v1/')
    elif model_choice == 'Local Model 2':
        # Instantates a local OpenAI client
        client = openai.OpenAI(api_key='dummy', base_url='http://192.168.blah.blu:5000/v1/')
    else:
        # Instantates the default OpenAI client
        client = openai.OpenAI(api_key=api_key)

    if use_case == 'Reviewer Response Generator':
        system = f"""{st.session_state['system_prompt2'].format(journal=journal)}"""
        prompt = f"""{st.session_state['intro_text'].format(journal=journal)}\n\n{paper_content}\n\n{st.session_state['reviewer_comment_intro']}\n{reviewer_comment}\n\n{response_idea}"""
    elif use_case == 'Paper Writing':
        system = f"""{st.session_state['system_prompt3'].format(journal=journal)}"""
        prompt = f"""{st.session_state['intro_text2'].format(journal=journal)}\n\n{paper_content}\n\n{response_idea}"""
    elif use_case == 'Email':
        system = f"""{st.session_state['system_prompt5']}"""
        prompt = f"""{st.session_state['intro_text4']}\n\n{paper_content}\n\n{response_idea}"""
    elif use_case == 'Programming':
        system = f"""{st.session_state['system_prompt4'].format(language=language)}"""
        prompt = f"""{st.session_state['intro_text3'].format(language=language)}\n\n{paper_content}\n\n{response_idea}"""
    elif use_case == 'Chat':
        system = st.session_state['system_prompt']
    else:
        system = st.session_state['system_prompt']
        prompt = f"{response_idea}Generate a response."
        
    if use_case == 'Chat':
        
        if st.session_state['use_chat_history']:
            # Use the entire chat history if the checkbox is checked
            messages = [{"role": "system", "content": system}] + st.session_state.messages
        else:
            # Use only the latest user message if the checkbox is not checked
            messages = [{"role": "system", "content": system}, {"role": "user", "content": response_idea}]
    else:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]

    model = {
        'Gpt3.5 turbo': 'gpt-3.5-turbo-16k',
        'Gpt4': 'gpt-4-0125-preview',
        'Local Model': 'dummy',  # Placeholder model name for local endpoint
        'Local Model 2': 'dummy'
    }.get(model_choice, 'gpt-3.5-turbo-16k')
    
    if use_case == 'Chat':
        with st.chat_message("assistant"):
                response_placeholder = st.empty()

                full_response = ""
                
                #prompt = prp + prompt + "\n\nASSISTANT: "
                #print(prompt)
                for response in client.chat.completions.create(
                    model=model,
                    messages=messages,
                    #prompt=prompt,
                    stream=True,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    
                ):
                    content = response.choices[0].delta.content or ""
                    full_response += content
                    #full_response += (response.choices[0].delta.content or "")
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
    else:
        response_placeholder = st.empty()  # Placeholder inside the expander
        with st.spinner("Generating Response..."):
            full_response = ""
            for index, response in enumerate(client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )):
                content = response.choices[0].delta.content or ""
                full_response += content
                # Update the placeholder with the new Markdown-formatted response
                #if use_case != 'Chat':
                response_placeholder.markdown(full_response)
    # Update the session_state only if we actually generated a new response
    if full_response.strip():
        st.session_state['latest_response'] = full_response.strip()
        response_placeholder.empty()
    return full_response.strip()


# Place the Reset button in the sidebar, outside any loops or conditional blocks
if st.sidebar.button("Reset", key="reset_button"):
    reset_all()

# Rest of the code for the Streamlit app goes here...
if use_case == 'Reviewer Response Generator':
    paper_content = st.text_area("Paper Content", height=300)
    reviewer_comment = st.text_area("Reviewer's Comment", height=150)
    response_idea = st.text_area("Response", height=150)
    
    # Button to generate the response
    generate_clicked = st.button("Generate Response", key="generate_response_button")

    # Check if all required fields are filled
    if generate_clicked:
        if not journal:
            st.error("Please specify the journal.")
        elif not paper_content.strip():
            st.error("Please enter the paper content.")
        elif not reviewer_comment.strip():
            st.error("Please enter the reviewer's comment.")
        elif not response_idea.strip():
            st.error("Please enter your response.")
        elif not st.session_state['intro_text'].strip():
            st.error("Please enter the introduction text.")
        elif not st.session_state['reviewer_comment_intro'].strip():
            st.error("Please enter the reviewer comment intro.")
        else:
            # If all fields are filled, proceed to generate the response
            response = get_response(model_choice, journal, paper_content, reviewer_comment, response_idea, st.session_state['system_prompt'], max_tokens, temperature, use_case)
            # Log the interaction
            log_interaction("user", f"Use Case: {use_case}\nResponse: {response}")
elif use_case == 'Paper Writing':
    paper_content = st.text_area("Paper Content", height=300)
    response_idea = st.text_area("Request", height=300)
    
    generate_clicked = st.button("Generate Response", key="generate_response_button")

    # Check if all required fields are filled
    if generate_clicked:
        if not journal:
            st.error("Please specify the journal.")
        elif not paper_content.strip():
            st.error("Please enter the paper content.")
        elif not response_idea.strip():
            st.error("Please enter your request.")
        elif not st.session_state['intro_text2'].strip():
            st.error("Please enter the introduction text.")
        else:
            # If all fields are filled, proceed to generate the response
            response = get_response(model_choice, journal, paper_content, None, response_idea, st.session_state['system_prompt'], max_tokens, temperature, use_case)
            # Log the interaction
            log_interaction("user", f"Use Case: {use_case}\nResponse: {response}")
elif use_case == 'Email':
    paper_content = st.text_area("Email Exchange", height=300)
    response_idea = st.text_area("Request", height=300)
    
    generate_clicked = st.button("Generate Response", key="generate_response_button")

    # Check if all required fields are filled
    if generate_clicked:
        if not paper_content.strip():
            st.error("Please enter the paper content.")
        elif not response_idea.strip():
            st.error("Please enter your request.")
        elif not st.session_state['intro_text2'].strip():
            st.error("Please enter the introduction text.")
        else:
            # If all fields are filled, proceed to generate the response
            response = get_response(model_choice, None, paper_content, None, response_idea, st.session_state['system_prompt'], max_tokens, temperature, use_case)
            # Log the interaction
            log_interaction("user", f"Use Case: {use_case}\nResponse: {response}")
elif use_case == 'Programming':
    paper_content = st.text_area("Code", height=300)
    response_idea = st.text_area("Request", height=300)
    
    generate_clicked = st.button("Generate Response", key="generate_response_button")

    # Check if all required fields are filled
    if generate_clicked:
        if not language:
            st.error("Please specify the language.")
        elif not paper_content.strip():
            st.error("Please enter the code.")
        elif not response_idea.strip():
            st.error("Please enter your request.")
        elif not st.session_state['intro_text3'].strip():
            st.error("Please enter the introduction text.")
        else:
            # If all fields are filled, proceed to generate the response
            response = get_response(model_choice, language, paper_content, None, response_idea, st.session_state['system_prompt'], max_tokens, temperature, use_case)
            # Log the interaction
            log_interaction("user", f"Use Case: {use_case}\nResponse: {response}")
elif use_case == 'Chat':
    # System prompt textbox for chat use case
    st.session_state['system_prompt'] = st.sidebar.text_area("System Prompt for Chat", value=st.session_state['system_prompt'], height=100)
    # Checkbox to toggle the use of chat history
    st.session_state['use_chat_history'] = st.sidebar.checkbox("Use Complete Chat History", value=st.session_state['use_chat_history'])


    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display existing conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Button to clear chat history
    if st.sidebar.button("Clear Chat", key="clear_chat_button"):
        st.session_state.messages = [{"role": "system", "content": st.session_state['system_prompt']}]  # Clear the chat history
        st.rerun()  # Rerun the app to reflect changes
    
    if streaming_completed and (prompt := st.chat_input("How can I help?")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        st.chat_input("Wait!", key="disabled_chat_input", disabled=True)
        log_interaction(st.session_state["name"], f"User: {prompt}")
        streaming_completed = False

        # Call the get_response function for the chat use case
        full_response = get_response(
            model_choice,
            None,
            None,
            None,
            prompt,  
            None,    
            max_tokens,
            temperature,
            use_case
        )

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        log_interaction(st.session_state["name"], f"Assistant: {full_response}")
        st.rerun()

    streaming_completed = True
elif use_case == 'Custom Prompt Generator':
    num_of_textboxes = st.sidebar.number_input("Number of Textboxes", min_value=1, max_value=5, value=1, step=1)

    # Generate textboxes based on the number selected by the user
    for i in range(num_of_textboxes):
        # Create intro textbox in the sidebar
        intro_key = f'intro_text_{i}'
        st.session_state['custom_intro_texts'][intro_key] = st.sidebar.text_area(f"Introduction Text {i+1}", value=st.session_state['custom_intro_texts'].get(intro_key, ""), height=75)

        # Create main textbox in the main area
        prompt_key = f'prompt_text_{i}'
        st.session_state['custom_prompts'][prompt_key] = st.text_area(f"Textbox {i+1}", height=150)

    # Button to generate the custom prompt response
    if st.button("Generate Response"):
        # Check if all required intro and main textboxes are filled
        all_textboxes_filled = True
        for i in range(num_of_textboxes):
            intro_key = f'intro_text_{i}'
            prompt_key = f'prompt_text_{i}'

            if not st.session_state['custom_intro_texts'][intro_key].strip() or not st.session_state['custom_prompts'][prompt_key].strip():
                all_textboxes_filled = False
                st.error(f"Please enter all the required text for Textbox {i+1}.")
                break

        # If all textboxes are filled, proceed to generate the response
        if all_textboxes_filled:
            assembled_prompt = "\n\n".join(st.session_state['custom_intro_texts'][intro_key] + "\n\n" + st.session_state['custom_prompts'][prompt_key] for i in range(num_of_textboxes)).strip()
            if assembled_prompt:
                response = get_response(model_choice, None, None, None, assembled_prompt, None, max_tokens, temperature, use_case)
                # Log the interaction
                log_interaction("user", f"Use Case: {use_case}\nResponse: {response}")
else:
    st.session_state['system_prompt'] = st.text_area("System Prompt", height=150, value=st.session_state['system_prompt'])

    response_idea = st.text_area("Your Prompt", height=150)
    paper_content = reviewer_comment = None

    generate_clicked = st.button("Generate Response", key="generate_response_button")

    # If the "Generate Response" button is clicked, get and display the response
    if generate_clicked:
        if response_idea:
                # Get the suggested response from the selected model
                response = get_response(model_choice, journal, paper_content, reviewer_comment, response_idea, st.session_state['system_prompt'], max_tokens, temperature, use_case)
                # Log the interaction
                log_interaction("user", f"Use Case: {use_case}\nResponse: {response}")
                # Ensure we preserve the response across reruns
                st.session_state['latest_response'] = response  # <- Make sure to update the state here
        else:
            # If the required fields are empty, display an error message
            st.error("Please enter all the required fields.")
            

response = st.session_state.get('latest_response', '')

generate_and_display_response()