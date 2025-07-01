# 🚀 Como Usar o Discador Predictivo em Localhost

## ✅ **SERVIDOR EM FUNCIONAMENTO**

O sistema está configurado e funcionando em localhost! 

### 📍 **URLs Principais**

- **🏠 API Principal**: http://localhost:8000
- **📖 Documentação Interativa**: http://localhost:8000/docs
- **📚 Documentação Redoc**: http://localhost:8000/redoc
- **🌐 Interface Frontend**: abra o arquivo `frontend_simples.html` no navegador

### 🔧 **Como Iniciar o Servidor**

Para iniciar o servidor, execute um dos comandos abaixo no terminal:

```powershell
# Opção 1: Servidor simplificado (recomendado para testes)
venv\Scripts\python.exe servidor_simples.py

# Opção 2: Servidor completo (quando quiser todas as funcionalidades)
venv\Scripts\python.exe main.py

# Opção 3: Usando uvicorn diretamente
venv\Scripts\python.exe -m uvicorn servidor_simples:app --host 0.0.0.0 --port 8000 --reload
```

### 📋 **Endpoints Disponíveis**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Página inicial da API |
| `GET` | `/api/v1/status` | Status do sistema |
| `GET` | `/api/v1/test` | Endpoint de teste |
| `GET` | `/docs` | Documentação Swagger |
| `GET` | `/redoc` | Documentação Redoc |

### 🧪 **Testando a API**

Você pode testar a API usando:

#### PowerShell/Curl:
```powershell
# Testar página inicial
curl http://localhost:8000

# Testar status
curl http://localhost:8000/api/v1/status

# Testar endpoint de teste
curl http://localhost:8000/api/v1/test
```

#### Browser:
- Abra http://localhost:8000 no seu navegador
- Abra http://localhost:8000/docs para a documentação interativa

### 🔄 **Parar o Servidor**

Para parar o servidor:
- Pressione `Ctrl+C` no terminal onde o servidor está rodando
- Ou execute: `taskkill /f /im python.exe` no PowerShell

### 🐛 **Solução de Problemas**

#### ❌ **Erro: "Porta 8000 já está em uso"**
```powershell
# Ver processos usando a porta 8000
netstat -ano | findstr :8000

# Matar processo Python
taskkill /f /im python.exe
```

#### ❌ **Erro: "Módulo não encontrado"**
```powershell
# Ativar ambiente virtual
venv\Scripts\activate

# Reinstalar dependências
pip install fastapi uvicorn
```

#### ❌ **Erro: "Permissão negada"**
```powershell
# Executar como administrador ou ajustar política de execução
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 🎯 **Funcionalidades Principais**

1. **📞 Gestão de Chamadas**: Sistema de discado predictivo
2. **📋 Listas de Contatos**: Gerenciamento de listas
3. **🎤 STT (Speech-to-Text)**: Reconhecimento de voz
4. **📊 Relatórios**: Análises e métricas
5. **⚙️ CLI**: Interface de linha de comando

### 🔧 **Configurações**

O sistema usa as seguintes configurações padrão:
- **Host**: 0.0.0.0 (acessível de qualquer IP local)
- **Porta**: 8000
- **Banco de Dados**: SQLite (discador.db)
- **Debug**: Ativado
- **CORS**: Permitido para todos os origins

### 📱 **Próximos Passos**

1. **Explore a documentação** em http://localhost:8000/docs
2. **Teste os endpoints** usando a interface Swagger
3. **Implemente funcionalidades** específicas do seu projeto
4. **Configure banco PostgreSQL** se necessário
5. **Integre com Asterisk** para funcionalidades completas

### 🆘 **Precisa de Ajuda?**

Se encontrar problemas:
1. Verifique se o Python está instalado: `python --version`
2. Verifique se as dependências estão instaladas: `pip list`
3. Verifique os logs do servidor para erros específicos
4. Consulte a documentação em http://localhost:8000/docs

---

✅ **Sistema funcionando corretamente!** Aproveite o desenvolvimento! 🚀 