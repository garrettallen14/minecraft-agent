import chromadb
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import memory_llms
from javascript import require
findAndParseJsonLikeText = require('json-like-parse')

class Module:
    def __init__(self, path_to_database='./memory_store/'):

        # Initialize the OpenAI Embeddings API
        load_dotenv()
        self.embeddings = OpenAIEmbeddings(model='text-embedding-3-small', api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize the databases
        # self.collections['collection'] allows us to dynamically write and read to different collections 
        self.database = chromadb.PersistentClient(path_to_database)
        self.collections = {
            'goal_lessons': self.database.get_or_create_collection('goal_lessons'),
            'general_perceptions': self.database.get_or_create_collection('general_perceptions'),
            'important_locations': self.database.get_or_create_collection('important_locations'),
            'core_memories': self.database.get_or_create_collection('core_memories')
        }

        self.mem_llms = memory_llms.get_llms()

    # Simple time-based scoring function
    def get_score(self, id, distance, last_accessed, document):

        last_accessed = datetime.strptime(last_accessed, '%Y-%m-%d %H:%M:%S.%f')
        time_since_last_accessed = datetime.now() - last_accessed

        # Return the document and the score
        # Before 30 minutes (1800 seconds), the score is greater than 1 / 2*(1-distance)
        # At 30 minutes, the score will be equal to 1 / 2*distance
        # After 30 minutes (1800 seconds), the score is less than 1 / 2*(1-distance)
        return [id, document, 1 / (1 + time_since_last_accessed.total_seconds()/1800) * (1-distance)]


    # Gather memories based on a query and collection name
    # Scored based on time since last accessed and distance from query
    # Returns the top 5 memories
    def retrieve_memories(self, query, collection_name):

        # Translate the query to an embedding
        embedding = self.embeddings.embed_query(query)

        # Retrieve memories from the collection
        results = self.collections[collection_name].query(query_embeddings=embedding)

        # Get scores for all results
        scores = []
        for id, distance, metadata, document in zip(results['ids'][0], results['distances'][0], results['metadatas'][0], results['documents'][0]):
            score = self.get_score(id, distance, metadata['last_accessed'], document)
            scores.append(score)

        # Sort the scores and return the top 5
        scores = sorted(scores, key=lambda x: x[2], reverse=True)

        # Update the last accessed time for the top 5
        for i in range(5):
            self.collections[collection_name].upsert(
                ids = [scores[i][0]],
                documents = scores[i][1],
                embeddings = self.collections[collection_name].get(ids=[scores[i][0]], include=['embeddings'])['embeddings'],
                metadatas={'last_accessed': str(datetime.now())}
            )
        
        return scores[:5]

    # get a vector embedding for the context
    def process_context(self, context):
        return self.embeddings.embed_query(context)

    # Storing a memory in the database
    def store_memory(self, memory, collection_name):

        # Embed the memory
        embedded_memory = self.embeddings.embed_documents([memory])

        # Add into the proper database collection
        self.collections[collection_name].upsert(
            ids = [f'{int(self.collections[collection_name].count()) + 1}'],
            documents = memory,
            embeddings = embedded_memory,
            metadatas={'last_accessed': str(datetime.now())}
        )
        
        return True

    # This is a function that will be called by the main program to query the memories
    # Takes an arbitrary question and returns an answer based on the memories
    def query_memories(self, question):

        # Get a set of three (3) queries from the language model, based on the question
        query_pairs = []
        attempts = 0
        while attempts <= 5:
            # Ensure we get the proper formatting
            try:
                queries = self.mem_llms['generate_queries'].invoke({
                    'question': question
                }).content

                queries = findAndParseJsonLikeText(queries)[0]
                query_pairs.append([queries['query1'].split(': ')[0], queries['query1'].split(': ')[1]])
                query_pairs.append([queries['query2'].split(': ')[0], queries['query2'].split(': ')[1]])
                query_pairs.append([queries['query3'].split(': ')[0], queries['query3'].split(': ')[1]])
                
                break
            except:
                attempts+=1
                continue
        
        # Get top memory results for each query
        top_memories = []
        for query_pair in query_pairs:
            # Retrieves the top 5 memories for each query, collection_name pair
            try:
                top_memories.append(self.retrieve_memories(query_pair[1], query_pair[0]))
            # If the query is not found in the collection, it will be skipped
            except:
                continue

        # Summarize the top memories and return the final answer
        answer = self.mem_llms['answer_question'].invoke({
            'top_memories': top_memories,
            'question': question
        }).content

        return answer


    # Reset the collection if necessary
    def reset_collection(self):
        print('Resetting...', 'Before:', self.database.list_collections())

        for i in range(len(self.database.list_collections())):
            if len(self.database.list_collections()) == 0:
                break
            self.database.delete_collection(self.database.list_collections()[0].name)

        print('After:', self.database.list_collections())