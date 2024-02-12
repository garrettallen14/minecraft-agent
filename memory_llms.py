from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_prompts():
    
    generate_queries = """As a Minecraft helper bot, your task is to use your memory module to respond to a specific question by crafting three separate queries for the database collections. These collections are:

'goal_lessons_learned': Archives insights and key takeaways from past Minecraft goal achievements.
'general_perceptions': Stores observations and thoughts on the Minecraft world.
'important_locations': Contains information on significant places discovered in the game.
For each query, select the appropriate collection to pull relevant documents. The relevance is gauged by a cosine similarity score, with higher scores indicating closer matches.

Your queries must seek to help inform the answer to the Question. 
Each query is sent directly to the database. It will retrieve information based on a cosine similarity measurement. You must make each query as specific as possible to ensure the most relevant information is retrieved.

You may query any collection more than once if it's necessary for the question.
You must return the queries in a JSON formatted response.

The structure of the JSON response should have the key be queryN, where N is the query number. 
The following value will be the following format: "collection_name: query for relevant documents", where collection_name is the relevant collection being searched, and query for relevant documents is the specific query you have formulated to retrieve the most relevant information from the collection.
Here's an example of the structure for your JSON formatted response:
    "query1": "collection_name: query for relevant documents",
    "query2": "collection_name: another query for relevant documents",
    "query3": "collection_name: yet another query for relevant documents"

This format will guide you in fetching information that aids in providing the best answer to the Minecraft-related question.

Question: {question}
# Reminder, respond in JSON format.
JSON Formatted Query Response: """

    answer_question = """As a Minecraft helper bot, your task is to use your memory module to answer a specific question using the information retrieved from the database collections.
You have collected the following information:
{top_memories}
You must use the information to answer the following question in the most accurate, informative, and helpful way possible.
Question: {question}
# Respond here with your answer to the question based on the collected information.
Response:"""



    return {'generate_queries': generate_queries, 'answer_question': answer_question}


def get_llms(query=''):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")

        llm = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, api_key=openai_api_key)
        llm_4 = ChatOpenAI(model='gpt-4-0125-preview', temperature=0.1, api_key=openai_api_key)

        if query == '': prompts = get_prompts()
        else: prompts = get_prompts()[query]

        for key, value in prompts.items():
            # save money by using gpt-3.5-turbo-1106
            # if key == 'action_proposal':
            #     prompts[key] = ChatPromptTemplate.from_template(value) | llm_4
            # else:
            #     prompts[key] = ChatPromptTemplate.from_template(value) | llm
            
            prompts[key] = ChatPromptTemplate.from_template(value) | llm

        return prompts