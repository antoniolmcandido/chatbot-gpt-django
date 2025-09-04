# chatbot/management/commands/process_pdf.py

import os
from django.conf import settings
from django.core.management.base import BaseCommand
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Processa o PDF e cria o banco de dados vetorial.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando o processamento do PDF...")

        # 1. Carregar o PDF
        pdf_path = os.path.join(settings.BASE_DIR, 'data', 'documento_empresa.pdf')
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        if not documents:
            self.stdout.write(self.style.ERROR("Nenhum documento encontrado no PDF."))
            return

        self.stdout.write(f"PDF carregado. {len(documents)} páginas encontradas.")

        # 2. Dividir o texto em chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        self.stdout.write(f"Texto dividido em {len(texts)} chunks.")

        # 3. Criar embeddings e armazenar no FAISS
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            self.stdout.write(self.style.ERROR("Chave da API da OpenAI não encontrada no .env"))
            return
            
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        try:
            vector_store = FAISS.from_documents(texts, embeddings)
            
            # 4. Salvar o índice FAISS localmente
            index_path = os.path.join(settings.BASE_DIR, 'faiss_index')
            vector_store.save_local(index_path)
            
            self.stdout.write(self.style.SUCCESS(f"Banco de dados vetorial criado e salvo em '{index_path}'."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocorreu um erro ao criar o banco vetorial: {e}"))