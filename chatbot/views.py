# chatbot/views.py

import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain

load_dotenv()

# Carregar o índice FAISS (fazemos isso uma vez quando o servidor inicia)
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    index_path = os.path.join(settings.BASE_DIR, 'faiss_index')
    vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    print(f"Erro ao carregar o índice FAISS: {e}")
    vector_store = None

# Função para a página do chat
def chat_view(request):
    return render(request, 'chatbot/chat.html')

# Função da API
@csrf_exempt # Usado para simplificar. Em produção, use o método de token CSRF do Django.
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)
    
    if not vector_store:
        return JsonResponse({'error': 'Índice FAISS não foi carregado. Execute o comando process_pdf primeiro.'}, status=500)

    try:
        data = json.loads(request.body)
        question = data.get('question')
        chat_history = data.get('history', [])

        if not question:
            return JsonResponse({'error': 'Nenhuma pergunta fornecida.'}, status=400)

        # Converter o histórico para o formato esperado pelo LangChain
        # O LangChain espera uma lista de tuplas (pergunta, resposta)
        formatted_history = []
        for item in chat_history:
            if isinstance(item, list) and len(item) >= 2:
                formatted_history.append((item[0], item[1]))
        
        print(f"Histórico formatado: {formatted_history}")  # Para debug

        # Criar a cadeia de conversação
        # Usamos um modelo mais rápido e barato para o chatbot
        llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo", openai_api_key=openai_api_key)
        
        # O retriever é a nossa busca no PDF
        retriever = vector_store.as_retriever()

        # O ConversationalRetrievalChain junta tudo: o LLM, o retriever e o histórico
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            return_source_documents=False # Não precisamos ver os chunks que ele usou
        )

        # Fazer a pergunta usando o método invoke (nova versão)
        result = qa_chain.invoke({
            'question': question, 
            'chat_history': formatted_history
        })
        answer = result['answer']

        return JsonResponse({'answer': answer})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Corpo da requisição não é um JSON válido.'}, status=400)
    except Exception as e:
        print(f"Erro na API do chat: {e}")  # Para debug
        return JsonResponse({'error': str(e)}, status=500)