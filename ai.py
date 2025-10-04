
from groq import Groq

class AIDebugger:
  def __init__(self, model="openai/gpt-oss-20b", temperature=1, max_completion_tokens=8192, top_p=1, reasoning_effort="medium"):
    self.client = Groq()
    self.model = model
    self.temperature = temperature
    self.max_completion_tokens = max_completion_tokens
    self.top_p = top_p
    self.reasoning_effort = reasoning_effort

  def analyze_traceback(self, traceback_str, stream=False, on_first_chunk=None):
    prompt_instructions = (
        "You are an AI Debugging Assistant.\n"
        "When given Python error tracebacks or code, analyze them and return solutions in a clean, structured format.\n"
        "Always follow this format exactly:\n\n"
        "1. **Error Name**: <type of error, e.g., ZeroDivisionError>\n"
        "   - **Error Line**: line number if available>\n"
        "   - **Error Description**: <explain in simple language what caused the error>\n"
        "   - **Error Fix**: <provide one or more possible solutions with code snippets if needed>\n\n"
        "If there are multiple errors, list them as separate numbered items (1, 2, 3, …).\n\n"
        "Keep explanations clear, beginner-friendly, and concise.\n"
    )
    user_content = f"{prompt_instructions}\nTraceback:\n{traceback_str}"
    completion = self.client.chat.completions.create(
      model=self.model,
      messages=[
        {"role": "user", "content": user_content}
      ],
      temperature=self.temperature,
      max_completion_tokens=self.max_completion_tokens,
      top_p=self.top_p,
      stream=stream,
      stop=None
    )
    if stream:
      first_chunk = True
      for chunk in completion:
        if first_chunk and on_first_chunk:
          on_first_chunk()
          first_chunk = False
        print(chunk.choices[0].delta.content or "", end="")
    else:
      return completion.choices[0].message.content