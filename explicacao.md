Este projeto usará o padrão de arquitetura **RAG (Retrieval-Augmented Generation)**. Em vez de treinar um novo modelo, nós vamos:

1.  **Processar** o seu PDF, quebrando-o em pequenos pedaços.
2.  **Indexar** esses pedaços em um "banco de dados vetorial" que permite buscas por significado, não apenas por palavras-chave.
3.  Quando um usuário fizer uma pergunta, nós vamos primeiro **buscar** os pedaços mais relevantes do PDF nesse banco de dados.
4.  Finalmente, vamos **enviar** a pergunta do usuário junto com os pedaços encontrados para a API da OpenAI (GPT) e instruí-la a responder *com base exclusivamente* nesse contexto.

Isso garante que as respostas sejam fiéis ao seu documento e evita que o modelo "invente" informações.

-----

### **Estrutura da Aula**

  * **Parte 1: Configuração do Ambiente e do Projeto Django**
      * Pré-requisitos
      * Ambiente virtual
      * Instalação das bibliotecas
      * Criação do projeto e do app Django
  * **Parte 2: O Coração do Chatbot - Processando o PDF**
      * Configurando a API da OpenAI
      * Criando um script para ler, dividir e indexar o PDF
  * **Parte 3: Construindo o Backend com Django**
      * Criando a rota (URL) da API
      * Desenvolvendo a `view` que recebe a pergunta, busca no PDF e consulta o GPT
  * **Parte 4: Construindo o Frontend Interativo com Bootstrap**
      * Criando o template HTML base
      * Estilizando a interface do chat
      * Escrevendo o JavaScript para a comunicação com o backend
  * **Parte 5: Juntando Tudo e Rodando o Projeto**
      * Como executar e testar sua aplicação

-----

### **Parte 1: Configuração do Ambiente e do Projeto Django**

#### **1.1. Pré-requisitos**

  * **Python 3.8+** instalado. Você pode verificar com `python --version`.
  * **pip** (gerenciador de pacotes do Python) instalado.

#### **1.2. Ambiente Virtual**

É uma boa prática criar um ambiente isolado para cada projeto.

```bash
# Crie uma pasta para o seu projeto
mkdir projeto_chatbot
cd projeto_chatbot

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

Você saberá que funcionou pois o nome do ambiente (`(venv)`) aparecerá no início do seu terminal.

#### **1.3. Instalação das Bibliotecas**

Com o ambiente ativo, instale tudo o que vamos precisar:

```bash
pip install django openai langchain langchain-community langchain-openai "pypdf" faiss-cpu tiktoken python-dotenv
```

  * `django`: Nosso framework web backend.
  * `openai`: Biblioteca oficial da OpenAI para interagir com a API do GPT.
  * `langchain`: Uma biblioteca fantástica que simplifica muito a criação de aplicações com LLMs, incluindo o processo de RAG.
  * `pypdf`: Para ler o conteúdo do seu arquivo PDF.
  * `faiss-cpu`: Biblioteca do Facebook AI para buscas de similaridade eficientes. Será nosso banco de dados vetorial local.
  * `tiktoken`: Usado pela LangChain para calcular como dividir o texto de forma otimizada.
  * `python-dotenv`: Para gerenciar nossas chaves de API de forma segura.

#### **1.4. Criação do Projeto e App Django**

```bash
# Crie o projeto Django (não se esqueça do ponto no final)
django-admin startproject config .

# Crie o nosso app principal
python manage.py startapp chatbot
```

Agora, abra o arquivo `config/settings.py` e adicione o nosso app `chatbot` à lista de `INSTALLED_APPS`:

```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbot',  # Adicione esta linha
]
```

-----

### **Parte 2: O Coração do Chatbot - Processando o PDF**

#### **2.1. Configurando a API da OpenAI**

1.  Crie uma conta na [plataforma da OpenAI](https://platform.openai.com/).
2.  Vá para a seção "API keys" e crie uma nova chave secreta. **Copie-a e guarde em um lugar seguro.**
3.  Na raiz do seu projeto Django, crie um arquivo chamado `.env`.
4.  Dentro do `.env`, adicione sua chave:

<!-- end list -->

```
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

#### **2.2. Script para Processar o PDF**

Este é um script que rodaremos **uma única vez** para preparar nosso documento.

1.  Crie uma pasta chamada `data` na raiz do seu projeto e coloque seu arquivo PDF dentro dela. Vamos chamá-lo de `documento_empresa.pdf`.
2.  Dentro do app `chatbot`, crie a seguinte estrutura de pastas e arquivos: `chatbot/management/commands/process_pdf.py`.
3.  Cole o seguinte código em `process_pdf.py`:

<!-- end list -->

```python
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

```

Agora, rode o comando no seu terminal (com o ambiente virtual ativo):

```bash
python manage.py process_pdf
```

Se tudo der certo, uma nova pasta chamada `faiss_index` será criada na raiz do seu projeto. Ela contém o conhecimento do seu PDF pronto para ser consultado.

-----

### **Parte 3: Construindo o Backend com Django**

#### **3.1. Criando a Rota (URL)**

Primeiro, vamos definir os endereços da nossa aplicação.

No arquivo `config/urls.py`, inclua as URLs do nosso app `chatbot`:

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chatbot.urls')), # Adicione esta linha
]
```

Agora, crie o arquivo `chatbot/urls.py` e adicione as rotas específicas do chatbot:

```python
# chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Rota para a página principal que renderiza o chat
    path('', views.chat_view, name='chat'),
    # Rota da API que recebe as perguntas e devolve as respostas
    path('api/chat/', views.chat_api, name='chat_api'),
]
```

#### **3.2. Desenvolvendo a `view`**

É aqui que a mágica acontece. A `view` irá receber a pergunta do frontend, usar o índice FAISS para encontrar o contexto relevante e, em seguida, consultar o GPT.

Abra o arquivo `chatbot/views.py` e cole o código abaixo:

```python
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
```

-----

### **Parte 4: Construindo o Frontend Interativo com Bootstrap**

#### **4.1. Criando o Template HTML**

Dentro do app `chatbot`, crie a estrutura `templates/chatbot/` e, dentro dela, o arquivo `chat.html`.

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-g">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot da Empresa Serval</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Adicionar o CSRF token como meta tag -->
    <meta name="csrf-token" content="{{ csrf_token }}">
    <style>
        body {
            background-color: #f8f9fa;
        }
        #chat-window {
            height: 70vh;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow-y: auto;
            padding: 15px;
            background-color: #fff;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
        }
        .user-message {
            align-items: flex-end;
        }
        .bot-message {
            align-items: flex-start;
        }
        .message-bubble {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 15px;
            word-wrap: break-word;
        }
        .user-message .message-bubble {
            background-color: #0d6efd;
            color: white;
            border-bottom-right-radius: 0;
        }
        .bot-message .message-bubble {
            background-color: #e9ecef;
            color: #212529;
            border-bottom-left-radius: 0;
        }
        #loading-indicator {
            display: none; /* Escondido por padrão */
            justify-content: center;
            align-items: center;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">Chat de Atendimento - Serval</h4>
            </div>
            <div class="card-body" id="chat-window">
                <div class="message bot-message">
                    <div class="message-bubble">
                        Olá! Como posso ajudar você hoje com base nas informações do nosso documento?
                    </div>
                </div>
            </div>
            <div id="loading-indicator">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Digitando...</span>
                </div>
            </div>
            <div class="card-footer">
                <form id="chat-form">
                    <div class="input-group">
                        <input type="text" id="message-input" class="form-control" placeholder="Digite sua mensagem..." autocomplete="off" required>
                        <button class="btn btn-primary" type="submit">Enviar</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        const chatForm = document.getElementById('chat-form');
        const messageInput = document.getElementById('message-input');
        const chatWindow = document.getElementById('chat-window');
        const loadingIndicator = document.getElementById('loading-indicator');
        const chatHistory = [];

         // Função para obter o CSRF token
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const userMessage = messageInput.value.trim();
            if (!userMessage) return;

            // 1. Adicionar mensagem do usuário à tela
            appendMessage(userMessage, 'user');
            messageInput.value = '';
            showLoading(true);

            // 2. Enviar mensagem para o backend
            try {
                const csrftoken = getCookie('csrftoken');
                const response = await fetch('/api/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    body: JSON.stringify({
                        question: userMessage,
                        history: chatHistory
                    })
                });

                if (!response.ok) {
                    const errorData = await response.text();
                    console.error('Erro da API:', errorData);
                    throw new Error(`Erro na resposta da API: ${response.status}`);
                }

                const data = await response.json();
                const botMessage = data.answer;

                // 3. Adicionar resposta do bot à tela
                appendMessage(botMessage, 'bot');

                // 4. Atualizar o histórico
                chatHistory.push([userMessage, botMessage]);

            } catch (error) {
                console.error('Erro:', error);
                appendMessage('Desculpe, ocorreu um erro. Tente novamente mais tarde.', 'bot');
            } finally {
                showLoading(false);
            }
        });

        function appendMessage(message, sender) {
            const messageWrapper = document.createElement('div');
            messageWrapper.classList.add('message', `${sender}-message`);

            const messageBubble = document.createElement('div');
            messageBubble.classList.add('message-bubble');
            messageBubble.textContent = message;

            messageWrapper.appendChild(messageBubble);
            chatWindow.appendChild(messageWrapper);

            // Rolar para a última mensagem
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
        
        function showLoading(isLoading) {
            if (isLoading) {
                loadingIndicator.style.display = 'flex';
            } else {
                loadingIndicator.style.display = 'none';
            }
        }
    </script>
</body>
</html>
```

-----

### **Parte 5: Juntando Tudo e Rodando o Projeto**

Você chegou à etapa final\! Agora é só rodar o servidor de desenvolvimento do Django.

No seu terminal, na raiz do projeto (onde está o `manage.py`), execute:

```bash
python manage.py runserver
```

Abra seu navegador e acesse o endereço [http://127.0.0.1:8000/](https://www.google.com/search?q=http://127.0.0.1:8000/).

Você verá a interface do chatbot. Tente fazer uma pergunta relacionada ao conteúdo do seu PDF. O frontend enviará a pergunta para o seu backend Django, que por sua vez usará o LangChain e a API da OpenAI para gerar uma resposta baseada no documento e devolvê-la para a tela.

### **Próximos Passos e Melhorias**

  * **Segurança:** Em produção, nunca use `@csrf_exempt` de forma leviana. Implemente o envio do token CSRF do Django via JavaScript.
  * **Banco de Dados Vetorial:** Para projetos maiores, considere usar um banco de dados vetorial dedicado como Pinecone, ChromaDB ou Weaviate em vez do FAISS local.
  * **Streaming de Respostas:** Para uma experiência de usuário melhor, você pode implementar "streaming", onde a resposta do bot aparece palavra por palavra, como no ChatGPT.
  * **Cache:** Implemente um sistema de cache para perguntas frequentes para reduzir custos e latência.
  * **Tratamento de Erros:** Melhore o tratamento de erros tanto no frontend quanto no backend para dar feedback mais claro ao usuário.

Parabéns\! Você construiu uma aplicação web completa com Django e a integrou com uma das mais poderosas APIs de IA disponíveis hoje, criando um assistente especializado para o seu negócio.