# 📂 Sistema de Upload de Listas - Discador

## 🎯 Como Usar

### 1. Acesso ao Sistema
- Entre no painel: https://discador.vercel.app
- Clique na aba **"Listas"**

### 2. Preparar Arquivo de Contatos

#### Formatos Aceitos:
- **CSV** (recomendado)
- **TXT** 

#### Separadores Suportados:
- Vírgula (`,`)
- Ponto e vírgula (`;`)
- Pipe (`|`)
- Tab (`\t`)

#### Estrutura do Arquivo:
```
TELEFONE,NOME
+54 11 1234-5678,Juan Pérez
+54 11 2345-6789,María García
```

### 3. Upload da Lista

1. **Selecione a campanha** destino no dropdown
2. **Arraste o arquivo** para a área de upload ou clique para selecionar
3. **Revise o preview** dos dados detectados
4. **Clique em "Subir Lista"** para processar

### 4. Validações Automáticas

- ✅ **Formato de arquivo**: Apenas CSV/TXT
- ✅ **Tamanho máximo**: 5MB
- ✅ **Números de telefone**: Validação automática
- ✅ **Preview**: Mostra detecção de telefone/nome

## 📋 Exemplos de Formatos

### CSV (vírgula):
```csv
+54 11 1234-5678,Juan Pérez
+54 11 2345-6789,María García
+54 11 3456-7890,Carlos López
```

### TXT (pipe):
```txt
+54 11 1234-5678|Juan Pérez
+54 11 2345-6789|María García
+54 11 3456-7890|Carlos López
```

### TXT (ponto e vírgula):
```txt
+54 11 1234-5678;Juan Pérez
+54 11 2345-6789;María García
+54 11 3456-7890;Carlos López
```

## 🔧 Funcionalidades

### ✅ Implementado
- Upload drag-and-drop
- Preview automático de dados
- Detecção automática de telefones
- Validação de formato e tamanho
- Progress bar em tempo real
- Associação com campanhas
- Suporte múltiplos separadores

### 🔄 Processamento
1. **Upload**: Arquivo enviado para o backend
2. **Parsing**: Detecta separadores e colunas
3. **Validação**: Confirma números válidos
4. **Armazenamento**: Salva contatos na campanha
5. **Feedback**: Mostra estatísticas do processo

## 📊 Estatísticas Retornadas

Após o upload, você verá:
- Total de linhas processadas
- Contatos válidos encontrados
- Contatos inválidos rejeitados
- Nome da campanha associada

## 🚨 Troubleshooting

### Arquivo não aceito?
- Verifique a extensão (.csv ou .txt)
- Confirme que o tamanho é menor que 5MB

### Números não detectados?
- Use formato +54 11 1234-5678
- Evite caracteres especiais extras
- Primeira coluna deve ser o telefone

### Preview vazio?
- Arquivo pode estar vazio
- Verifique se há quebras de linha

## 🎯 Próximos Passos

Quando conectado ao Supabase:
- Persistência real dos contatos
- Histórico de uploads
- Remoção de duplicatas
- Validação contra blacklist 