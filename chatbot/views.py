# chatbot/views.py

import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

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

        # Converter o histórico para mensagens do LangChain
        history_messages = []
        for item in chat_history:
            if isinstance(item, list) and len(item) >= 2:
                history_messages.append(HumanMessage(content=item[0]))
                history_messages.append(AIMessage(content=item[1]))
        
        print(f"Histórico: {len(history_messages)} mensagens")  # Para debug

        # Criar o LLM
        llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo", openai_api_key=openai_api_key)
        
        # O retriever é a nossa busca no PDF
        retriever = vector_store.as_retriever()
        
        # Buscar documentos relevantes
        docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Criar o template do prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Você é um assistente útil que responde perguntas com base no seguinte contexto:\n\n{context}\n\nSe a informação não estiver no contexto, diga que não sabe."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])
        
        # Criar a chain
        chain = prompt_template | llm | StrOutputParser()
        
        # Fazer a pergunta
        answer = chain.invoke({
            'context': context,
            'history': history_messages,
            'question': question
        })

        return JsonResponse({'answer': answer})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Corpo da requisição não é um JSON válido.'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Corpo da requisição não é um JSON válido.'}, status=400)
    except Exception as e:
        print(f"Erro na API do chat: {e}")  # Para debug
        return JsonResponse({'error': str(e)}, status=500)