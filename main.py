import streamlit as st
import time
import random
from openai import OpenAI

# Configuración global
DAILY_QUOTA = 1000  # Ejemplo de cuota diaria (ajustar según su plan)
MONTHLY_QUOTA = 120  # Su límite mensual actual

# Variables para seguimiento de uso (deberían persistirse entre sesiones en una aplicación real)
daily_usage = 0
monthly_usage = 0

def check_quota(tokens_to_use):
    global daily_usage, monthly_usage
    if daily_usage + tokens_to_use > DAILY_QUOTA:
        raise Exception("Daily quota exceeded")
    if monthly_usage + tokens_to_use > MONTHLY_QUOTA:
        raise Exception("Monthly quota exceeded")

def update_usage(tokens_used):
    global daily_usage, monthly_usage
    daily_usage += tokens_used
    monthly_usage += tokens_used

def generate_single_output(prompt, max_retries=5, initial_delay=1):
    client = OpenAI(api_key=st.session_state.api_key)
    for attempt in range(max_retries):
        try:
            estimated_tokens = len(prompt.split()) + 50  # Estimación básica
            check_quota(estimated_tokens)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Usar un modelo más económico
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                n=1
            )
            
            tokens_used = response.usage.total_tokens
            update_usage(tokens_used)
            
            return response.choices[0].message.content
        except Exception as e:
            if "quota exceeded" in str(e).lower():
                st.error(f"Quota exceeded: {str(e)}")
                return None
            
            delay = (2 ** attempt) * initial_delay + random.uniform(0, 1)
            st.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f} seconds.")
            time.sleep(delay)
    
    st.error(f"Failed to generate output after {max_retries} attempts.")
    return None

# El resto de su código (generate_outputs, interfaz de Streamlit, etc.) permanece igual
