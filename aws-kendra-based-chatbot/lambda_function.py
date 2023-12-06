from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import os


chat_history = []
MAX_HISTORY_LENGTH = 5


def lambda_handler(event, context):
   user_message = event['question']
   user_name ='default'# request.headers['X-User-ID', 'default']
  
   qa = build_chain()
   try:
     if (len(chat_history) == MAX_HISTORY_LENGTH):
       chat_history.pop(0)
   except:
     print("no user")
   result = run_chain(qa, user_message, chat_history)
   chat_history.append((user_message, result["answer"]))
   answer=result['answer']
   if 'source_documents' in result:
     answer+="\nSources:\n"
     for d in result['source_documents']:
       answer+=d.metadata['source']+"\n"
  
   response = {
       'statusCode': 200,
       'body': answer
   }
   return response


region = os.environ["AWS_REGION"]
kendra_index_id = os.environ["KENDRA_INDEX_ID"]
openai_api_key=os.environ["OPENAI_API_KEY"]


def build_chain():


 llm = OpenAI(batch_size=5, temperature=0, max_tokens=100,openai_api_key=openai_api_key)
    
 retriever = AmazonKendraRetriever(index_id=kendra_index_id, region_name=region )


 prompt_template = """
 The following is a friendly conversation between a human and an AI.
 The AI is talkative and provides lots of specific details from its context.
 If the AI does not know the answer to a question, it truthfully says it
 does not know. The AI is helpful and tries to answer the question to the best of its ability.
 {context}
 Instruction: Based on the above documents, provide a detailed answer for, {question} Answer "don't know"
 if not present in the document.


 Solution:"""
 PROMPT = PromptTemplate(
     template=prompt_template, input_variables=["context", "question"]
 )


 condense_qa_template = """
 Given the following conversation and a follow up question, rephrase the follow up question
 to be a standalone question.


 Chat History:
 {chat_history}
 Follow Up Input: {question}
 Standalone question:"""
 standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)


 qa = ConversationalRetrievalChain.from_llm(
       llm=llm,
       retriever=retriever,
       condense_question_prompt=standalone_question_prompt,
       return_source_documents=True,
       combine_docs_chain_kwargs={"prompt":PROMPT})
 return qa


def run_chain(chain, prompt: str, history=[]):
 return chain({"question": prompt, "chat_history": history})