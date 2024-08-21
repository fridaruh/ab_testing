import streamlit as st
from openai import OpenAI
import random

# Streamlit app
st.title('OpenAI A/B Testing Tool')

# Input for OpenAI API Key
api_key = st.text_input('Enter your OpenAI API Key', type='password')

# Input for prompts
prompt_a = st.text_area('Enter Prompt A')
prompt_b = st.text_area('Enter Prompt B')

# Number of outputs per prompt
num_outputs = st.number_input('Number of outputs per prompt', min_value=1, max_value=10, value=5)

# Function to generate a single output
def generate_single_output(prompt):
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            n=1
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Function to generate multiple outputs
def generate_outputs(prompt, n):
    outputs = []
    for _ in range(n):
        output = generate_single_output(prompt + " En menos de 50 palabras.")
        if output:
            outputs.append(output)
    return outputs

# Button to run the test
if st.button('Run Test'):
    if not api_key or not prompt_a or not prompt_b:
        st.error('Please enter your API key and both prompts.')
    else:
        with st.spinner('Generating outputs...'):
            outputs_a = generate_outputs(prompt_a, num_outputs)
            outputs_b = generate_outputs(prompt_b, num_outputs)
        
        if outputs_a and outputs_b:
            # Combine and shuffle outputs
            all_outputs = [(output, 'A') for output in outputs_a] + [(output, 'B') for output in outputs_b]
            random.shuffle(all_outputs)
            
            # Store results
            if 'results' not in st.session_state:
                st.session_state.results = []
            
            # Display outputs and collect ratings using st.form
            with st.form(key='rating_form'):
                for i, (output, prompt_type) in enumerate(all_outputs):
                    st.subheader(f'Output {i+1}')
                    st.write(output)
                    rating = st.radio(f'Rate Output {i+1}', ['👍 Good', '👎 Poor'], key=f'rating_{i}')
                    st.session_state.results.append((prompt_type, 1 if rating == '👍 Good' else 0))
                
                submitted = st.form_submit_button("Submit Ratings")
            
            if submitted:
                # Calculate and display results
                st.subheader('Test Results')
                results_a = [score for prompt, score in st.session_state.results if prompt == 'A']
                results_b = [score for prompt, score in st.session_state.results if prompt == 'B']
                
                avg_a = sum(results_a) / len(results_a) if results_a else 0
                avg_b = sum(results_b) / len(results_b) if results_b else 0
                st.write(f'Prompt A average score: {avg_a:.2f}')
                st.write(f'Prompt B average score: {avg_b:.2f}')
                if avg_a > avg_b:
                    st.success('Prompt A performed better!')
                elif avg_b > avg_a:
                    st.success('Prompt B performed better!')
                else:
                    st.info('Both prompts performed equally.')
                
                # Clear results for next test
                st.session_state.results = []
