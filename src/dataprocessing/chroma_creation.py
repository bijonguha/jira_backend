# this file uses newly generated polaris data with click level data

import chromadb
import pandas as pd
from tqdm import tqdm
import os

client = chromadb.PersistentClient(path="data/chroma_db_v2")

jira_collection = client.get_or_create_collection("jira_collection_v2")

cols_to_drop = ['status', 'story_priority', 'story_description', 'story_summary', 'story_points']

def process_and_store_chunk(chunk, chroma_db_collection, cols_to_drop = cols_to_drop):

    chunk.dropna(inplace=True)

    chunk['days_effort_spent'] = chunk["total_in_progress_time"] + chunk["total_in_testing_time"]
    
    chunk['story_data'] = chunk['story_summary'] + chunk['story_description']
    
    chunk = chunk[(chunk['days_effort_spent'] > 0) & (chunk['days_effort_spent'] <= 10)]

    documents = []
    metadatas = []
    ids = []
    
    for _, row in chunk.iterrows():

        result = chroma_db_collection.get(ids=row['story_key'])

        if len(result['ids']) > 0:

            print("Id exists: ",row['story_key'])
            continue
        
        metadata = {
            'id': row['story_key'],
            'days_effort_spent': row['days_effort_spent'],
            'total_in_progress_time' : row['total_in_progress_time'],
            'total_in_testing_time' : row['total_in_testing_time'],
            'story_data': row['story_data']
        }
        
        documents.append(row['story_data'])
        metadatas.append(metadata)
        ids.append(row['story_key'])

    if len(ids)>0:
        chroma_db_collection.add( documents=documents, metadatas=metadatas, ids=ids )
        print("collection updated")
    else:
        print("No update")

def read_and_process_csv(file_path, chroma_db_collection, chunk_size=100):

    for chunk in tqdm(pd.read_csv(file_path, chunksize=chunk_size), desc=f"processing {filepath}"):
        process_and_store_chunk(chunk, chroma_db_collection)

filenames = ['jira_stories_new_polaris.csv']

filedir = "data/raw"

for filename in tqdm(filenames):
    filepath = os.path.join(filedir, filename)
    read_and_process_csv(file_path = filepath, chroma_db_collection = jira_collection)