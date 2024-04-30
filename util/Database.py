import openai
import os
import numpy as np
from util.ListSerializer import ListSerializer

from dotenv import dotenv_values
config = dotenv_values(".env")
openai.api_key = config['OPENAI_TOKEN']

from progressbar import progressbar

class DB:
    def __init__(self, initState = []) -> None:
        self.embeddings = []
        self.entries = []

        for i in progressbar(range(len(initState))):
            self.AddEmbedding(initState[i])

        print(f"Initialised")
    

    def AddEmbedding(self, sentence):
        # Encode sentences into vectors using OpenAI's text-embedding-ada-002 model
        response = openai.Embedding.create(
                input=sentence,
                model="text-embedding-ada-002"
            )
        self.embeddings.append(response['data'][0]['embedding'])
        self.entries.append(sentence)

    def QueryDatabase(self, query):
        # Encode query into vector using OpenAI's text-embedding-ada-002 model
        response = openai.Embedding.create(
            input=query,
            model="text-embedding-ada-002"
        )
        query_embedding = response['data'][0]['embedding']
        query_embedding = np.array(query_embedding)

        embeddings = np.array(self.embeddings)
        # Calculate cosine similarity between query vector and sentence vectors
        similarities = np.dot(embeddings, query_embedding) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding))

        # Get indices of top N most similar sentences
        N = 5  # number of similar sentences to return
        top_N_indices = np.argsort(similarities)[::-1][:N]

        # Get top N most similar sentences
        top_N_sentences = [self.entries[i] for i in top_N_indices]

        return top_N_sentences

    def Save(self, databaseName, dirPath):
        # If the directory doesn't exist
        if not os.path.exists(dirPath):
            # Create a directory to store the database
            os.mkdir(dirPath)
        # Save the entries to a JSON file
        ListSerializer.serialize(self.entries, os.path.join(dirPath, f'{databaseName}.entries'))
        # Save the embeddings to a JSON file
        ListSerializer.serialize(self.embeddings, os.path.join(dirPath, f'{databaseName}.embeddings'))

    def Load(self, databaseName, dirPath):
        # Load the entries from a JSON file
        self.entries = ListSerializer.deserialize(os.path.join(dirPath, f'{databaseName}.entries'))
        # Load the embeddings from a JSON file
        self.embeddings = ListSerializer.deserialize(os.path.join(dirPath, f'{databaseName}.embeddings'))