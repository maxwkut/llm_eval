import time
import os
from typing import Dict, Any, List
from openai import OpenAi
import google.generativeai as genai
import anthropic
from ..db.database import Database

class ChatPipeline:
    def __init__(self, config: Dict[str, Any], db: Database = None):
        """Initialize the pipeline with configuration"""
        self.config = config
        self.db = db or Database()

        # Initialize appropriate API client
        if self.config['components']['api'] == 'openai':
            self.client = OpenAI()
            self.messages = [
                {"role": "system", "content": config['parameters']['system_message']}
            ]
        elif self.config['components']['api'] == 'google':
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
            generation_config = {
                "temperature": config['parameters']['temperature'],
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            self.client = genai.GenerativeModel(
                model_name=config['components']['model'],
                generation_config=generation_config
            )
            # Start chat with system message
            self.chat = self.client.start_chat(history=[])
            # Send system message
            self.chat.send_message(config['parameters']['system_message'])
        elif self.config['components']['api'] == 'anthropic':
            self.client = anthropic.Anthropic()
            self.messages = [] # Claude handles message differently
        else:
            raise ValueError(f"Unsupported API type: {self.config['components']['api']}")
        
        def get_response(self, user_input: str) -> str:
            """
            Get a response from the model for a given input
            Returns the model's response text
            """
            try:
                # Start timing
                start_time = time.time()

                # Get response based on API type
                if self.config['components']['api'] == 'openai':
                    # Add user message to conversation
                    self.messages.append({"role": "user", "content": user_input})

                    # Call OpenAI API
                    response = self.client.chat.completions.create(
                        model=self.config['components']['model'],
                        messages=self.messages,
                        temperature=self.config['parameters']['temperature']
                    )

                    # Get assistant's response
                    assistant_message = response.choices[0].message.content

                    # Add assistant's response to conversation history
                    self.messages.append({"role": "assistant", "content": assistant_message})

                    # Prepare metadata for logging
                    response_metadata = {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens,
                        'finish_reason': response.choices[0].finish_reason,
                    }

                elif self.config['components']['api'] == 'google':
                    # Send message and get response
                    response = self.chat.send_message(user_input)
                    assistant_message = response.text

                    # Prepare metadata for logging
                    response_metadata = {
                        'prompt_tokens': None, # Gemini doesn't provide token count
                        'completion_tokens': None,
                        'total_tokens': None,
                        'finish_reason': None,
                    }

                elif self.config['components']['api'] == 'anthropic':
                    # Add user message to conversation
                    self.messages.append({"role": "user", "content": [{"type": "text"}, user_input]})

                    # Call Claude API
                    response = self.client.messages.create(
                        model-self.config['components']['model'],
                        max_tokens=self.config['parameters'].get('max_tokens', 4098),
                        temperature=self.config['parameters']['temperature'],
                        system=self.config['parameters']['system_message'],
                        messages=self.messages
                    )

                    # Get assistant's response
                    assistant_message = response.content[0].text

                    # Add assistant's response to conversation history
                    self.messages.append({"role": "assistant", "content": [{"type": "text"}, assistant_message]})

                    # Prepare metadata for logging
                    response_metadata = {
                        'prompt_tokens': response.usage.input_tokens,
                        'completion_tokens': response.usage.output_tokens,
                        'total_tokens': response.usage.input_tokens + response.usage.output_tokens,
                        'finish_reason': response.stop_reason,
                    }

                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)
                    
                # Log the response
                self.db.log_response(
                    self.config,
                    user_input,
                    assistant_message,
                    latency_ms,
                    response_metadata
                )

                return assistant_message