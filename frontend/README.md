# Painel de Monitoramento de Chamadas

Painel web moderno para monitorar chamadas em tempo real com atualização automática a cada 5 segundos. 

## 📋 Características

- **Monitoramento em Tempo Real**: Exibe todas as chamadas com estado "en_progreso"
- **Atualização Automática**: Polling a cada 5 segundos sem recargar a página
- **Interface Responsiva**: Layout adaptável para desktop e mobile
- **Modo Escuro**: Interface com tema escuro moderno
- **Cronômetro ao Vivo**: Exibe a duração atual de cada chamada em tempo real
- **Finalização Manual**: Permite finalizar chamadas diretamente pelo painel

## 🚀 Tecnologias

- React.js
- TailwindCSS
- Jest + Testing Library (testes)

## 📦 Instalação

Clone o repositório e instale as dependências:

```bash
git clone [URL_DO_REPOSITORIO]
cd frontend
npm install
```

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

Ajuste a URL da API conforme necessário para apontar para seu backend do Discador.

## 🔧 Desenvolvimento

Para iniciar o servidor de desenvolvimento:

```bash
npm start
```

Acesse http://localhost:3000 para visualizar o painel.

## 🧪 Testes

Execute os testes automatizados:

```bash
npm test
```

## 📦 Build para Produção

Para gerar a versão de produção:

```bash
npm run build
```

Os arquivos serão gerados na pasta `build/` e podem ser servidos por qualquer servidor HTTP.

## 🌐 Conexão com a API

O sistema se conecta ao backend FastAPI do Discador através dos seguintes endpoints:

- `GET /llamadas/en-progreso`: Para obter as chamadas em andamento
- `POST /llamadas/finalizar`: Para finalizar manualmente uma chamada

## 📱 Responsividade

O painel é totalmente responsivo:
- **Desktop**: Visualização completa da tabela 
- **Mobile**: Tabela com scroll horizontal e tamanho de fonte reduzido

## 🔍 Uso

1. Após iniciar, o painel exibirá automaticamente todas as chamadas com estado "en_progreso"
2. A atualização ocorre a cada 5 segundos, indicada por um spinner no topo
3. O cronômetro de cada chamada é atualizado em tempo real
4. Para finalizar uma chamada, clique no botão "Finalizar" e confirme a ação

## 🔜 Funcionalidades Futuras

- Integração WebSocket para atualizações em tempo real
- Filtro por usuário/operador
- Notificações sonoras para novas chamadas
- Modo claro/escuro alternável

## 📄 Licença

Este projeto está sob a licença MIT.