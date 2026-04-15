import copy
import json
import subprocess
from llama_cpp import Llama


def execute_linux_command(command):
    try:
        # use a list to avoid shell=True for better security
        result = subprocess.run(
            command, #.split(), 
            shell=True,
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as error:
        return str(error)


class GeneralCommandExecutor:
    def __init__(self, model_path='qwen2.5-1.5b-instruct-q6_k.gguf', track_messages=False):
        self.llm = Llama(model_path=model_path, n_ctx=2048, chat_format="chatml", verbose=0)
        system_prompt = (
            'You are a Linux system assistant. If a user asks for information or a task '
            'requiring a shell command, respond ONLY with the command that should satisfy the need of the user.'
            'The answer should be one line that can be executed directly in the bash shell, without block of code or any formatting'
        ) 
        self.messages = [{"role": "system", "content": system_prompt}]
        self.track_messages = track_messages


    def __call__(self, user_input):
        if self.track_messages:
            self.messages.append({"role": "user", "content": user_input})     
            messages = self.messages
        else:
            messages = copy.copy(self.messages)
            messages.append({"role": "user", "content": user_input})
        response = self.llm.create_chat_completion(messages=messages)
        command = response["choices"][0]["message"]["content"]    
        print(f'{command}:\n', execute_linux_command(command))
        if self.track_messages:
            self.messages.append({"role": "assistant", "content": content})
            self.messages.append({"role": "system", "content": f"Command output: {output}"})


class HumanLanguageInterface:
    def __init__(self, model_path='qwen2.5-1.5b-instruct-q6_k.gguf', n_ctx=2048, verbose=0):
        self.llm = Llama(model_path=model_path, n_ctx=n_ctx, chat_format="chatml", verbose=verbose)


    def __call__(self, input_request, system_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_request}
        ]
        response = self.llm.create_chat_completion(messages=messages)
        return response["choices"][0]["message"]["content"], messages 
