# 🤖 Chatbot GPT Django

Um chatbot inteligente construído com Django e OpenAI GPT que responde perguntas baseadas em documentos PDF específicos da sua empresa.

## 🎯 Sobre o Projeto

Este projeto implementa um sistema de chat conversacional que utiliza Retrieval-Augmented Generation (RAG) para responder perguntas com base no conteúdo de documentos PDF. O chatbot é especializado em informações da **Empresa Serval** e pode responder perguntas sobre produtos, serviços e políticas da empresa.

### ✨ Funcionalidades

-   💬 **Interface de Chat Moderna**: Interface web responsiva com Bootstrap
-   📄 **Processamento de PDF**: Extração e indexação automática de conteúdo
-   🧠 **IA Conversacional**: Respostas contextuais usando GPT-3.5-turbo
-   🔍 **Busca Vetorial**: Sistema de busca semântica com FAISS
-   📚 **Memória de Conversa**: Mantém contexto das conversas anteriores
-   ⚡ **Tempo Real**: Indicador de digitação e respostas instantâneas

## 🛠️ Tecnologias Utilizadas

### Backend

-   **Django 4.x** - Framework web Python
-   **Python 3.12** - Linguagem de programação
-   **OpenAI GPT-3.5-turbo** - Modelo de linguagem
-   **LangChain** - Framework para aplicações com LLM
-   **FAISS** - Biblioteca de busca vetorial (Facebook AI Similarity Search)

### Frontend

-   **Bootstrap 5.3** - Framework CSS
-   **JavaScript ES6** - Interatividade do chat
-   **HTML5/CSS3** - Interface do usuário

### Processamento de Dados

-   **PyPDF** - Extração de texto de PDFs
-   **OpenAI Embeddings** - Vetorização de texto
-   **RecursiveCharacterTextSplitter** - Divisão inteligente de texto

## 📋 Pré-requisitos

-   Python 3.8+
-   Chave da API OpenAI
-   Arquivo PDF com dados da empresa

## 🚀 Como Executar

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/antoniolmcandido/chatbot-gpt-django.git
cd chatbot-gpt-django
```

### 2️⃣ Instale as Dependências

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
DEBUG=True
SECRET_KEY=sua_secret_key_django
```

### 4️⃣ Execute as Migrações

```bash
python manage.py migrate
```

### 5️⃣ Processe o PDF (Primeira Execução)

Coloque seu arquivo PDF em `data/documento_empresa.pdf` e execute:

```bash
python manage.py process_pdf
```

### 6️⃣ Inicie o Servidor

```bash
python manage.py runserver
```

### 7️⃣ Acesse o Chatbot

Abra seu navegador e vá para: `http://localhost:8000/`

## 📁 Estrutura do Projeto

```text
chatbot-gpt-django/
├── 📂 chatbot/                 # App principal do Django
│   ├── 📂 management/
│   │   └── 📂 commands/
│   │       └── process_pdf.py  # Comando para processar PDFs
│   ├── 📂 templates/
│   │   └── 📂 chatbot/
│   │       └── chat.html       # Interface do chat
│   ├── models.py               # Modelos do Django
│   ├── views.py                # Views e API do chat
│   └── urls.py                 # URLs do app
├── 📂 config/                  # Configurações do Django
├── 📂 data/                    # Arquivos PDF para processamento
├── 📂 faiss_index/             # Índice vetorial gerado
├── 📄 manage.py                # Script de gerenciamento Django
└── 📄 requirements.txt         # Dependências Python
```

## 🔧 Comandos Úteis

### Reprocessar PDF

```bash
python manage.py process_pdf
```

### Criar Superusuário

```bash
python manage.py createsuperuser
```

### Executar Testes

```bash
python manage.py test
```

## 📖 Como Funciona

1. **📄 Carregamento**: O sistema carrega e processa o PDF da empresa
2. **✂️ Fragmentação**: O texto é dividido em chunks menores e gerenciáveis
3. **🔢 Vetorização**: Cada chunk é convertido em embeddings usando OpenAI
4. **💾 Indexação**: Os embeddings são armazenados no FAISS para busca rápida
5. **❓ Consulta**: Quando o usuário faz uma pergunta:
    - A pergunta é convertida em embedding
    - O sistema busca os chunks mais relevantes
    - O GPT gera uma resposta baseada no contexto encontrado

## 🌟 Exemplo de Uso

**Usuário**: "Quais são os produtos da empresa?"

**Bot**: _Busca no documento da Serval e responde baseado no conteúdo encontrado_

## 🔒 Segurança

-   ✅ Proteção CSRF ativada
-   ✅ Validação de entrada de dados
-   ✅ Tratamento de erros robusto
-   ✅ Chaves de API em variáveis de ambiente

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte, entre em contato:

-   💼 LinkedIn: [antoniolmcandido](https://linkedin.com/in/antoniolmcandido)

---

⭐ **Se este projeto foi útil, considere dar uma estrela no repositório!**
