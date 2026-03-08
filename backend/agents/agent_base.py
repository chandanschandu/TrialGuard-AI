# import os
# import json
# import re
# import boto3
# from pinecone import Pinecone
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Initialize Clients
# # Ensure you have AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION in your .env
# bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# # Initialize Pinecone
# pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
# index = pc.Index(os.getenv('PINECONE_INDEX'))

# class BaseAgent:
#     def __init__(self, name):
#         self.name = name
#         # Use model ID from .env, fallback to Claude 3 Sonnet if not set
#         self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

#     def get_embedding(self, text):
#         """Generates embeddings using Amazon Titan v2"""
#         try:
#             body = json.dumps({
#                 "inputText": text[:8000],
#                 "dimensions": 1024, # Explicitly set dimensions if needed, Titan v2 supports variable sizes
#                 "normalize": True
#             })
            
#             response = bedrock.invoke_model(
#                 modelId='amazon.titan-embed-text-v2:0',
#                 body=body.encode(),
#                 contentType='application/json',
#                 accept='application/json'
#             )
            
#             response_body = json.loads(response['body'].read())
#             return response_body['embedding']
#         except Exception as e:
#             print(f"Error generating embedding: {e}")
#             return []

#     def rag_retrieve(self, query, top_k=3):
#         """Retrieves relevant context from Pinecone"""
#         embedding = self.get_embedding(query)
#         if not embedding:
#             return ""
            
#         try:
#             results = index.query(
#                 vector=embedding, 
#                 top_k=top_k, 
#                 include_metadata=True
#             )
            
#             # Safely extract text from metadata
#             contexts = [
#                 match['metadata'].get('text', '') 
#                 for match in results['matches'] 
#                 if 'metadata' in match
#             ]
#             return "\n".join(contexts)
#         except Exception as e:
#             print(f"Error retrieving from Pinecone: {e}")
#             return ""

#     def _clean_json_text(self, text):
#         """Helper to strip Markdown fences from LLM response"""
#         if not isinstance(text, str):
#             return text
#         # Remove ```json ... ``` or just ``` ... ```
#         pattern = r"```(?:json)?\s*(.*?)```"
#         match = re.search(pattern, text, re.DOTALL)
#         if match:
#             return match.group(1).strip()
#         return text.strip()

#     def call_bedrock(self, prompt):
#         """Calls Amazon Bedrock using the messages API"""
#         try:
#             # Check if using Nova models (requires different body format or Converse API)
#             is_nova = "nova" in self.model_id.lower()
            
#             if is_nova:
#                 # IMPORTANT: Nova Pro expects 'inferenceConfig' and 'messages'
#                 # but NOT 'anthropic_version'. It also uses a different response structure.
#                 body = json.dumps({
#                     "inferenceConfig": {
#                         "max_new_tokens": 2000,
#                         "temperature": 0.0,
#                         "top_p": 0.9
#                     },
#                     "messages": [
#                         {
#                             "role": "user",
#                             "content": [{"text": prompt}]
#                         }
#                     ]
#                 })
#             else:
#                 body = json.dumps({
#                     "anthropic_version": "bedrock-2023-05-31",
#                     "max_tokens": 2000,
#                     "temperature": 0.0,
#                     "messages": [
#                         {"role": "user", "content": [{"type": "text", "text": prompt}]}
#                     ]
#                 })
            
#             print(f"DEBUG: Calling Bedrock model {self.model_id}...")
#             response = bedrock.invoke_model(
#                 modelId=self.model_id,
#                 body=body,
#                 contentType='application/json',
#                 accept='application/json'
#             )
            
#             response_body = json.loads(response['body'].read())
#             # print(f"DEBUG: Response body: {json.dumps(response_body)[:500]}...")
            
#             if is_nova:
#                 # Nova response format: {'output': {'message': {'content': [{'text': '...'}]}}}
#                 raw_text = response_body['output']['message']['content'][0]['text']
#             else:
#                 # Claude response format: {'content': [{'text': '...'}]}
#                 raw_text = response_body['content'][0]['text']
            
#             # CLEAN THE OUTPUT
#             cleaned = self._clean_json_text(raw_text)
#             print(f"DEBUG: {self.name} raw response length: {len(raw_text)}")
#             return cleaned
            
#         except Exception as e:
#             print(f"Error calling Bedrock: {e}")
#             return "{}"
import os
import json
import re
import boto3
from pinecone import Pinecone
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Initialize Clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')


# Initialize Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX'))


class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

    def get_embedding(self, text):
        """Generates embeddings using Amazon Titan v2"""
        if not isinstance(text, str):
            print(f"⚠️ Warning: get_embedding expected string, got {type(text)}")
            return []
            
        try:
            body = json.dumps({
                "inputText": text[:8000],
                "dimensions": 1024,
                "normalize": True
            })
            
            response = bedrock.invoke_model(
                modelId='amazon.titan-embed-text-v2:0',
                body=body.encode(),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def rag_retrieve(self, query, top_k=3):
        """Retrieves relevant context from Pinecone - FIXED"""
        if not isinstance(query, str):
            print(f"⚠️ Warning: rag_retrieve expected string query, got {type(query)}")
            return ""
            
        embedding = self.get_embedding(query)
        if not embedding:
            return ""
            
        try:
            results = index.query(
                vector=embedding, 
                top_k=top_k, 
                include_metadata=True
            )
            
            # Safely extract text from metadata
            contexts = [
                match['metadata'].get('text', '') 
                for match in results['matches'] 
                if 'metadata' in match and isinstance(match['metadata'], dict)
            ]
            return "\n".join(contexts)
        except Exception as e:
            print(f"Error retrieving from Pinecone: {e}")
            return ""

    def _clean_json_text(self, text):
        """Helper to strip Markdown fences from LLM response - FIXED"""
        # ✅ CRITICAL FIX: Always ensure string input
        if not isinstance(text, str):
            print(f"⚠️ _clean_json_text: Converting {type(text)} to string")
            text = json.dumps(text) if isinstance(text, (dict, list)) else str(text)
        
        # Remove ```json ... ``` or just ``` ... ```
        pattern = r"```(?:json)?\s*(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
        else:
            cleaned = text.strip()
            
        return cleaned

    def call_bedrock(self, prompt):
        """Calls Amazon Bedrock using the messages API - FIXED"""
        # ✅ FIX 1: Ensure string prompt
        if not isinstance(prompt, str):
            print(f"⚠️ call_bedrock: Converting prompt {type(prompt)} to string")
            prompt = json.dumps(prompt) if isinstance(prompt, (dict, list)) else str(prompt)
        
        try:
            is_nova = "nova" in self.model_id.lower()
            
            if is_nova:
                body = json.dumps({
                    "inferenceConfig": {
                        "max_new_tokens": 2000,
                        "temperature": 0.0,
                        "top_p": 0.9
                    },
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ]
                })
            else:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "temperature": 0.0,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ]
                })
            
            print(f"DEBUG: Calling Bedrock model {self.model_id}...")
            response = bedrock.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            if is_nova:
                # Extra safety check for Nova response
                if 'output' in response_body and 'message' in response_body['output']:
                    raw_text = response_body['output']['message']['content'][0]['text']
                else:
                    print(f"⚠️ Unexpected Nova response format: {response_body.keys()}")
                    raw_text = str(response_body)
            else:
                # Extra safety check for Claude response
                if 'content' in response_body and response_body['content']:
                    raw_text = response_body['content'][0]['text']
                else:
                    print(f"⚠️ Unexpected Claude response format: {response_body.keys()}")
                    raw_text = str(response_body)
            
            # ✅ FIX 2: Debug and ensure string output
            print(f"DEBUG: {self.name} raw response type: {type(raw_text)}, length: {len(str(raw_text))}")
            
            cleaned = self._clean_json_text(raw_text)
            print(f"DEBUG: {self.name} final output type: {type(cleaned)}")
            
            return cleaned
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return "Error: Could not generate response"

