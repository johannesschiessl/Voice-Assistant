from datetime import datetime
from groq import Groq

groq_client = Groq()

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

system_message = f"""You are a helpful voice assistant. The user is talking to you via voice and can hear your responses, so keep them concise and short. You can't do any human things, other than talking. Max 3 sentences.
- Date: {get_current_date()}"""

conversation_history = [
    {"role": "system", "content": system_message}
]

def generate_response(question):
    try:
        conversation_history.append({"role": "user", "content": question})
        response = groq_client.chat.completions.create(
            messages=conversation_history,
            model="llama-3.2-3b-preview",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        generated_text = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": generated_text})
        return generated_text
    except Exception as e:
        return ""
