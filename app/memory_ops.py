import os
from datetime import datetime
from llama_index import  GPTListIndex, LLMPredictor, PromptHelper, Document, ServiceContext
from langchain.llms.openai import OpenAI
from llama_index import GPTVectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.indices.composability import ComposableGraph
from app.env import (
    MEMORY_DIR,
    BASE_PATH,
)

def append_line_to_file(line, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    else:
        print("dir already exists")
    # Get current date in YYYY-MM-DD format
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Create file if it doesn't exist
    file_path = os.path.join(folder_path, f'{date_str}.txt')
    if not os.path.exists(file_path):
        with open(file_path, 'w'):
            pass
    
    # Append line to file
    with open(file_path, 'a') as f:
        f.write(line + '\n')

def ask_with_memory(line) -> str:
    # This example uses text-davinci-003 by default; feel free to change if desired
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_base=BASE_PATH))

    # Configure prompt parameters and initialise helper
    max_input_size = 1024
    num_output = 256
    max_chunk_overlap = 50

    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap, chunk_size_limit=512)

    # Load documents from the 'data' directory
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    docstore = os.path.join(MEMORY_DIR, "knowledgebase", "docstore.json")
    if not os.path.exists(docstore):
        d = Document(line)
        documents = [d]
        os.makedirs(os.path.join(MEMORY_DIR, "knowledgebase"), exist_ok=True)
        index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
        index.storage_context.persist(persist_dir=os.path.join(MEMORY_DIR, "knowledgebase"))
    else:
        print("docstore already exists")


    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir=os.path.join(MEMORY_DIR, "knowledgebase"))
    storage_context2 = StorageContext.from_defaults(persist_dir=os.path.join(MEMORY_DIR, "memory"))
    

    # load index
    index = load_index_from_storage(storage_context, service_context=service_context,    )
    index2 = load_index_from_storage(storage_context2, service_context=service_context,    )

    graph = ComposableGraph.from_indices(GPTListIndex, [index, index2], index_summaries=["knowledgebase", "conversations"], service_context=service_context)
    query_engine = graph.as_query_engine()

    return query_engine.query(line).response


def update_memory(line):
    append_line_to_file(line, os.path.join(MEMORY_DIR, "dataset"))

    # This example uses text-davinci-003 by default; feel free to change if desired
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_base=BASE_PATH))

    # Configure prompt parameters and initialise helper
    max_input_size = 450
    num_output = 256
    max_chunk_overlap = 50
    d = Document(line)
    documents = [d]

    persist_dir = os.path.join(MEMORY_DIR, "memory")
    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

    # Load documents from the 'data' directory
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    docstore = os.path.join(persist_dir, "/docstore.json")

    if not os.path.exists(docstore):
        os.makedirs(persist_dir, exist_ok=True)
        index = GPTVectorStoreIndex.from_documents( documents, service_context=service_context)
        index.storage_context.persist(persist_dir=persist_dir)
        return
    else:
        print("docstore already exists")
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)

    # store to index
    index = load_index_from_storage(storage_context,     service_context=service_context,    )
    index.insert(d)
    index.storage_context.persist(persist_dir=persist_dir)
