#!/usr/bin/env python3

import os
import glob
from typing import List
from multiprocessing import Pool
from tqdm import tqdm
import time

from langchain.document_loaders import (
    SitemapLoader,
    GitHubIssuesLoader,
    GitLoader,
    DirectoryLoader,
    UnstructuredHTMLLoader,
    ConfluenceLoader,
)
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import (
    OpenAIEmbeddings,
    HuggingFaceEmbeddings,
    HuggingFaceInstructEmbeddings,
)
from langchain.docstore.document import Document
from app.env import (
    EMBEDDINGS_MODEL_NAME,
    EMBEDDINGS_SLEEP_TIME,
    EMBEDDINGS_REQUEST_CONCURRENT_JOB,
    MEMORY_DIR,
    BASE_PATH,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    GITHUB_PERSONAL_ACCESS_TOKEN,
    GIT_REPOSITORIES,
    GIT_ISSUE_REPOSITORIES,
    CONFLUENCE_BASE_URL,
    CONFLUENCE_SPACE_KEY,
    CONFLUENCE_EMAIL,
    JIRA_API_KEY,
    CONFLUENCE_LIMIT_PER_REQUEST,
    CONFLUENCE_TOTAL_LIMIT_PAGES,
)

from langchain.chains import RetrievalQA
from langchain.chat_models import (
    ChatOpenAI,
    AzureChatOpenAI,
)
from chromadb.config import Settings
from langchain.vectorstores.base import VectorStoreRetriever

# Define the folder for storing database
PERSIST_DIRECTORY = os.path.join(MEMORY_DIR, "chromadb")

# Define the Chroma settings
CHROMA_SETTINGS = Settings(
    chroma_db_impl='duckdb+parquet',
    persist_directory=PERSIST_DIRECTORY,
    anonymized_telemetry=False,
)


def append_line_to_file(line, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    else:
        print("dir already exists")
    # Get current date in YYYY-MM-DD format
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Create file if it doesn't exist
    file_path = os.path.join(folder_path, f"{date_str}.txt")
    if not os.path.exists(file_path):
        with open(file_path, "w"):
            pass

    # Append line to file
    with open(file_path, "a") as f:
        f.write(line + "\n")


def ask_with_memory(line) -> str:
    embeddings = OpenAIEmbeddings(
        model=EMBEDDINGS_MODEL_NAME, openai_api_base=BASE_PATH
    )
    db = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
        client_settings=CHROMA_SETTINGS,
    )
    retriever = db.as_retriever()

    res = ""
    llm = AzureChatOpenAI(
        temperature=OPENAI_TEMPERATURE, 
        openai_api_base=BASE_PATH, 
        model_name=OPENAI_MODEL, 
        deployment_name=OPENAI_MODEL
    )
    
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )

    # Get the answer from the chain
    res = qa(
        "---------------------\n Given the context above, answer to the following question: "
        + line
    )
    answer, docs = res["result"], res["source_documents"]
    res = answer

    # sources = set()  # To store unique sources

    # # Collect unique sources
    # for document in docs:
    #     if "source" in document.metadata:
    #         sources.add(document.metadata["source"])

    # # imporve this sources part by checking if the source value exist or not
    # if len(sources) > 0:
    #     res += "\n\n\n" + "Sources:\n"

    #     # Print the relevant sources used for the answer
    #     for source in sources:
    #         if source.startswith("http"):
    #             res += "- " + source + "\n"
    #         else:
    #             res += "- source code: " + source + "\n"

    return res

def fix_metadata(original_metadata):
    new_metadata = {}
    for k, v in original_metadata.items():
        if type(v) in [str, int, float]:
            # str, int, float are the types chroma can handle
            new_metadata[k] = v
        elif isinstance(v, list):
            new_metadata[k] = ",".join(v)
        else:
            # e.g. None, bool
            new_metadata[k] = str(v)
    return new_metadata


def build_knowledgebase():
    chunk_size = 2000
    chunk_overlap = 5

    embeddings = OpenAIEmbeddings(
        model=EMBEDDINGS_MODEL_NAME, 
        openai_api_base=BASE_PATH, 
        chunk_size = EMBEDDINGS_REQUEST_CONCURRENT_JOB,
        max_retries=6,
        show_progress_bar=True,
    )

    documents = []

    # git source code
    git_repos = GIT_REPOSITORIES.split(",")

    for repo in git_repos:
        print("Checking git repo: ", repo)

        loader = GitLoader(
            clone_url=f"https://github.com/{repo}",
            repo_path="./data/repo/" + repo.split("/")[-1],
            branch="main",
        )
        documents.extend(loader.load())

    # github issues loader
    issue_repos = GIT_ISSUE_REPOSITORIES.split(",")
    
    for repo in issue_repos:
        print("Checking repo's issues: ", repo)
        loader = GitHubIssuesLoader(
            repo=repo, 
            access_token=GITHUB_PERSONAL_ACCESS_TOKEN,
            status="all",
            sort="created",
            include_prs=True,
        )
        documents.extend(loader.load())

    # confluence loader
    if JIRA_API_KEY != "" and CONFLUENCE_BASE_URL != "" and CONFLUENCE_SPACE_KEY != "" and CONFLUENCE_EMAIL != "":
        loader = ConfluenceLoader(url=CONFLUENCE_BASE_URL, username=CONFLUENCE_EMAIL, api_key=JIRA_API_KEY)
        loaders = loader.load(
            space_key=CONFLUENCE_SPACE_KEY, 
            include_attachments=False, 
            limit=CONFLUENCE_LIMIT_PER_REQUEST, 
            max_pages=CONFLUENCE_TOTAL_LIMIT_PAGES
        )
        documents += loaders

    # fix metadata
    for doc in documents:
        doc.metadata = fix_metadata(doc.metadata)

    # process data
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)

    print("Creating embeddings. May take some minutes...")

    batch = EMBEDDINGS_REQUEST_CONCURRENT_JOB
    total_docs = len(texts)
    vectordb = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
        client_settings=CHROMA_SETTINGS
    )

    for i in range(0, total_docs, batch):
        print(f"added {i+batch} documents")
        sample_docs = texts[i:i+batch]
        vectordb.add_documents(sample_docs)

        print(f"sleeping for {EMBEDDINGS_SLEEP_TIME} seconds")
        time.sleep(EMBEDDINGS_SLEEP_TIME)

    vectordb.persist()

def update_memory(line):
    # append_line_to_file(line, os.path.join(MEMORY_DIR, "dataset"))
    print(line)

    # # This example uses text-davinci-003 by default; feel free to change if desired
    # llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_base=BASE_PATH))

    # # Configure prompt parameters and initialise helper
    # max_input_size = 200
    # num_output = 256
    # max_chunk_overlap = 30
    # d = Document(line)
    # documents = [d]

    # persist_dir = os.path.join(MEMORY_DIR, "memory")
    # prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

    # # Load documents from the 'data' directory
    # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    # docstore = os.path.join(persist_dir, "/docstore.json")

    # if not os.path.exists(docstore):
    #     os.makedirs(persist_dir, exist_ok=True)
    #     index = GPTVectorStoreIndex.from_documents( documents, service_context=service_context)
    #     index.storage_context.persist(persist_dir=persist_dir)
    #     return
    # else:
    #     print("docstore already exists")
    # # rebuild storage context
    # storage_context = StorageContext.from_defaults(persist_dir=persist_dir)

    # # store to index
    # index = load_index_from_storage(storage_context,     service_context=service_context,    )
    # index.insert(d)
    # index.storage_context.persist(persist_dir=persist_dir)
