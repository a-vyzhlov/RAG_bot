
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

CHROMA_PATH = "chroma" # путь к векторной БД
DATA_PATH = "data" # путь в данных
CHUNK_SIZE = 1000 # длина окна
CHUNK_OVERLAP = 50 # длина перекрытия

# Функция выдает эмбеддинги
def get_embeddings():
    model_kwargs = {'device': 'cpu'}
    embeddings_hf = HuggingFaceEmbeddings(
      model_name='intfloat/multilingual-e5-large',
      model_kwargs=model_kwargs
      )
    
    return embeddings_hf

# Загрузка документов
def load_documents(folder_path):
    pdf_files = []
    txt_files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_name.endswith('.pdf'):
            pdf_files.append(file_path)
        elif file_name.endswith('.txt'):
            txt_files.append(file_path)
    
    # Обработка PDF файлов
    pdf_pages = []
    for pdf_file in pdf_files:
        pdf_pages.extend(PyPDFLoader(pdf_file).load_and_split())

    # Обработка TXT файлов
    txt_pages = []
    for txt_file in txt_files:
        txt_pages.extend(TextLoader(txt_file.replace('\\', '/'), encoding = 'UTF-8').load_and_split())

    return pdf_pages + txt_pages

# Разбиение документа на чанги
def split_text(pages: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=['\n\n','\n','.','']
    )
    chunks = text_splitter.split_documents(pages)
    print(f"Разбили {len(pages)} документов на {len(chunks)} чанков.")
    ids = [str(i) for i in range(1, len(chunks) + 1)]
    
    return chunks, ids

# Создание векторной базы данных
def save_to_chroma(chunks: list[Document], user_id, ids):
    
    # Создает новые базы данных для документов
    db = Chroma.from_documents(
       chunks, get_embeddings(), persist_directory=os.path.join(CHROMA_PATH, str(user_id)), ids=ids
    )
    db.persist()

    return 

def chroma_main(folder_path, user_id):
    documents = load_documents(folder_path)
    chunks, ids = split_text(documents)
    save_to_chroma(chunks, user_id, ids)

    return ids

if __name__ == '__main__':
    chroma_main()
