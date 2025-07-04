from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.utils.logger import logger
import requests
import re
import json

router = APIRouter(prefix="/contacts", tags=["Contacts"])

# Configurações do Supabase
SUPABASE_URL = "https://orxxocptgaeoyrtlxwkv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ"

def validar_telefone_melhorado(numero: str) -> bool:
    """Validar número de telefone com suporte a múltiplos formatos."""
    if not numero or not isinstance(numero, str):
        return False
    
    # Remover espaços, hífens, parênteses, pontos e outros caracteres não numéricos
    numero_limpo = re.sub(r'[^\d+]', '', numero)
    
    # Se começar com +, manter apenas números após o +
    if numero_limpo.startswith('+'):
        numero_limpo = '+' + re.sub(r'[^\d]', '', numero_limpo[1:])
    else:
        numero_limpo = re.sub(r'[^\d]', '', numero_limpo)
    
    # Verificar se tem pelo menos 8 dígitos (números locais) e no máximo 15 (formato internacional)
    digits_only = re.sub(r'[^\d]', '', numero_limpo)
    
    if len(digits_only) < 8:
        return False
    
    if len(digits_only) > 15:
        return False
    
    # Padrões válidos para números brasileiros e internacionais
    patterns = [
        r'^\+\d{8,15}$',           # Formato internacional
        r'^\d{8,11}$',             # Números locais (8-11 dígitos)
        r'^(\d{2,3})\d{8,9}$',     # Com código de área
        r'^(0\d{2})\d{8,9}$',      # Com 0 + código de área
        r'^(\+55)(\d{2})\d{8,9}$', # Brasil formato completo
    ]
    
    for pattern in patterns:
        if re.match(pattern, numero_limpo):
            return True
    
    # Se não passou nos padrões, verificar se é um número simples com pelo menos 8 dígitos
    return len(digits_only) >= 8

def normalizar_telefone(numero: str) -> str:
    """Normalizar número de telefone para formato padrão."""
    if not numero:
        return numero
    
    # Manter apenas dígitos e + inicial se houver
    if numero.startswith('+'):
        numero_limpo = '+' + re.sub(r'[^\d]', '', numero[1:])
    else:
        numero_limpo = re.sub(r'[^\d]', '', numero)
    
    return numero_limpo

@router.post("/upload")
async def upload_contatos(
    arquivo: UploadFile = File(...),
    incluir_nome: bool = Form(True),
    pais_preferido: str = Form("auto"),
    campaign_id: int = Form(None)  # CORREÇÃO: Aceitar campaign_id
):
    """
    Upload de contatos - Processamento completo de listas pequenas e grandes.
    """
    logger.info(f"🚀 [UPLOAD] Iniciando upload: {arquivo.filename}")
    logger.info(f"📋 [UPLOAD] Params: incluir_nome={incluir_nome}, pais_preferido={pais_preferido}, campaign_id={campaign_id}")
    
    try:
        # 1. Validações básicas
        if not arquivo or not arquivo.filename:
            logger.error("❌ [UPLOAD] Arquivo não enviado")
            raise HTTPException(status_code=400, detail="Arquivo não enviado")
        
        # Verificar extensão do arquivo
        filename = arquivo.filename.lower()
        if not (filename.endswith('.txt') or filename.endswith('.csv')):
            logger.error(f"❌ [UPLOAD] Tipo de arquivo não suportado: {arquivo.filename}")
            raise HTTPException(
                status_code=400, 
                detail="Tipo de arquivo não suportado. Use apenas arquivos .txt ou .csv"
            )
        
        # Limite aumentado para 100MB para suportar listas realmente grandes
        if arquivo.size and arquivo.size > 100 * 1024 * 1024:  # 100MB
            logger.error(f"❌ [UPLOAD] Arquivo muito grande: {arquivo.size} bytes")
            raise HTTPException(
                status_code=413, 
                detail="Arquivo muito grande (máximo 100MB)."
            )
        
        # 2. Ler e processar arquivo
        logger.info(f"📖 [UPLOAD] Lendo arquivo: {arquivo.size} bytes")
        conteudo = await arquivo.read()
        
        if not conteudo:
            logger.error("❌ [UPLOAD] Arquivo vazio")
            raise HTTPException(status_code=400, detail="Arquivo vazio")
        
        # 3. Decodificar conteúdo com múltiplas tentativas
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        texto = None
        encoding_used = None
        
        for encoding in encodings:
            try:
                texto = conteudo.decode(encoding)
                encoding_used = encoding
                logger.info(f"✅ [UPLOAD] Decodificado como {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if texto is None:
            logger.error("❌ [UPLOAD] Não foi possível decodificar o arquivo")
            raise HTTPException(
                status_code=400, 
                detail="Não foi possível decodificar o arquivo. Verifique a codificação (use UTF-8 ou ISO-8859-1)"
            )
        
        # 4. Processar todas as linhas (SEM LIMITAÇÕES)
        linhas = texto.strip().split('\n')
        logger.info(f"📄 [UPLOAD] Total de linhas no arquivo: {len(linhas)} - PROCESSANDO TODAS!")
        
        # Log das primeiras linhas para debug
        for i, linha in enumerate(linhas[:5]):
            logger.debug(f"📝 [UPLOAD] Linha {i+1} (sample): '{linha.strip()}'")
        
        linhas_limpas = []
        linhas_invalidas = []
        
        for i, linha in enumerate(linhas):
            # Limpar caracteres especiais (\r, \n, espaços extras)
            linha_limpa = linha.replace('\r', '').replace('\n', '').strip()
            
            if linha_limpa:
                # Normalizar o número
                numero_normalizado = normalizar_telefone(linha_limpa)
                if validar_telefone_melhorado(numero_normalizado):
                    linhas_limpas.append(numero_normalizado)
                    if i < 10:  # Log apenas primeiras 10 para não poluir
                        logger.debug(f"📝 [UPLOAD] Linha {i+1}: '{linha_limpa}' -> '{numero_normalizado}' ✅")
                else:
                    linhas_invalidas.append(f"Linha {i+1}: '{linha_limpa}' - formato inválido")
                    if len(linhas_invalidas) <= 10:  # Log apenas primeiros 10 erros
                        logger.debug(f"📝 [UPLOAD] Linha {i+1}: '{linha_limpa}' ❌ inválida")
        
        total_linhas = len(linhas_limpas)
        logger.info(f"📊 [UPLOAD] Processadas {total_linhas} linhas válidas de {len(linhas)} total")
        
        if total_linhas == 0:
            error_msg = "Nenhuma linha válida encontrada no arquivo."
            if linhas_invalidas:
                error_msg += f" Primeiros erros: {'; '.join(linhas_invalidas[:3])}"
            logger.error(f"❌ [UPLOAD] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 5. Verificar limite prático para evitar timeout do servidor
        if len(linhas_limpas) > 150:
            logger.warning(f"⚠️ [UPLOAD] Arquivo muito grande ({len(linhas_limpas)} registros). Processando primeiros 150 para evitar timeout do servidor.")
            linhas_processadas = linhas_limpas[:150]
            arquivo_truncado = True
        else:
            linhas_processadas = linhas_limpas
            arquivo_truncado = False
            
        logger.info(f"📋 [UPLOAD] Processando {len(linhas_processadas)} de {len(linhas_limpas)} linhas")
        
        # 6. Verificar se existe uma campanha ativa para associar os contatos
        contatos_inseridos = 0
        contatos_duplicados = 0
        contatos_invalidos = 0
        erros_detalhados = []
        
        # Preparar headers para Supabase
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        logger.info("📡 [UPLOAD] Conectando ao Supabase...")
        
        # Definir campaign_id a ser usado
        if campaign_id:
            # Usar campaign_id fornecido pelo frontend
            logger.info(f"📋 [UPLOAD] Usando campaign_id fornecido: {campaign_id}")
            final_campaign_id = campaign_id
        else:
            # Buscar campanha ativa automaticamente
            try:
                campaign_response = requests.get(
                    f"{SUPABASE_URL}/rest/v1/campaigns?limit=1",
                    headers=headers,
                    timeout=10
                )
                
                if campaign_response.status_code == 200:
                    campaigns = campaign_response.json()
                    final_campaign_id = campaigns[0]["id"] if campaigns else 1
                    logger.info(f"📋 [UPLOAD] Usando campanha automaticamente: {final_campaign_id}")
                else:
                    final_campaign_id = 1
                    logger.warning("⚠️ [UPLOAD] Não foi possível buscar campanhas, usando ID padrão")
                    
            except Exception as e:
                final_campaign_id = 1
                logger.warning(f"⚠️ [UPLOAD] Erro ao buscar campanhas: {str(e)}, usando ID padrão")
        
        # 7. Inserir em lotes otimizados para evitar timeout
        if len(linhas_processadas) > 100:
            lote_size = 25  # Lotes pequenos para arquivos médios/grandes 
            logger.info(f"📦 [UPLOAD] Arquivo médio/grande ({len(linhas_processadas)} registros) - Lotes de {lote_size}")
        elif len(linhas_processadas) > 50:
            lote_size = 50  # Lotes médios para arquivos pequenos/médios
            logger.info(f"📦 [UPLOAD] Arquivo pequeno/médio ({len(linhas_processadas)} registros) - Lotes de {lote_size}")
        else:
            lote_size = len(linhas_processadas)  # Tudo de uma vez para arquivos muito pequenos
            logger.info(f"📦 [UPLOAD] Arquivo pequeno ({len(linhas_processadas)} registros) - Processando tudo de uma vez")
        
        total_lotes = (len(linhas_processadas) + lote_size - 1) // lote_size
        logger.info(f"📊 [UPLOAD] Total de lotes a processar: {total_lotes}")
        
        for i in range(0, len(linhas_processadas), lote_size):
            lote_atual = (i // lote_size) + 1
            lote = linhas_processadas[i:i+lote_size]
            
            # Preparar dados para inserção
            dados_insercao = []
            for linha in lote:
                dados_insercao.append({
                    "phone_number": linha,
                    "name": "",
                    "campaign_id": final_campaign_id,
                    "status": "not_started",
                    "attempts": 0
                })
            
            logger.info(f"📤 [UPLOAD] Enviando lote {lote_atual}/{total_lotes} com {len(dados_insercao)} contatos")
            
            try:
                # Fazer inserção no Supabase com timeout conservador
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/contacts",
                    headers=headers,
                    json=dados_insercao,
                    timeout=60  # Timeout conservador de 1 minuto por lote
                )
                
                logger.info(f"📥 [UPLOAD] Lote {lote_atual}: Status {response.status_code}")
                
                if response.status_code in [200, 201]:
                    contatos_inseridos += len(dados_insercao)
                    logger.info(f"✅ [UPLOAD] Lote {lote_atual} inserido: {len(dados_insercao)} contatos")
                elif response.status_code == 409:
                    # Conflito - números duplicados
                    contatos_duplicados += len(dados_insercao)
                    logger.info(f"⚠️ [UPLOAD] Lote {lote_atual} com duplicados: {len(dados_insercao)} contatos")
                else:
                    logger.error(f"❌ [UPLOAD] Erro no lote {lote_atual}: {response.status_code}")
                    logger.error(f"❌ [UPLOAD] Resposta: {response.text}")
                    contatos_invalidos += len(dados_insercao)
                    erros_detalhados.append(f"Lote {lote_atual}: Status {response.status_code} - {response.text[:100]}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"❌ [UPLOAD] Timeout no lote {lote_atual}")
                contatos_invalidos += len(dados_insercao)
                erros_detalhados.append(f"Lote {lote_atual}: Timeout na conexão")
            except Exception as e:
                logger.error(f"❌ [UPLOAD] Erro no lote {lote_atual}: {str(e)}")
                contatos_invalidos += len(dados_insercao)
                erros_detalhados.append(f"Lote {lote_atual}: {str(e)}")
        
        # 8. Preparar resposta
        total_processados = contatos_inseridos + contatos_duplicados
        
        if contatos_inseridos > 0:
            if arquivo_truncado:
                message = f"Upload parcial concluído! {contatos_inseridos} contatos processados dos primeiros 150 registros. ARQUIVO GRANDE: Para processar todos os {len(linhas_limpas)} registros, divida o arquivo em partes menores (máximo 150 por arquivo)."
            else:
                message = f"Upload concluído com sucesso! {contatos_inseridos} contatos novos processados."
        else:
            message = "Upload processado, mas nenhum contato novo foi inserido."
        
        if contatos_duplicados > 0:
            message += f" {contatos_duplicados} contatos já existentes."
        
        if contatos_invalidos > 0:
            message += f" {contatos_invalidos} contatos falharam na inserção."
        
        if arquivo_truncado:
            message += f" ⚠️ ATENÇÃO: Arquivo original tem {len(linhas_limpas)} registros, mas apenas 150 foram processados devido ao limite do servidor."
        
        resultado = {
            "mensaje": message,
            "archivo_original": arquivo.filename,
            "total_lineas_archivo": len(linhas_processadas),
            "contatos_validos": contatos_inseridos,
            "contatos_invalidos": contatos_invalidos,
            "contatos_duplicados": contatos_duplicados,
            "errores": erros_detalhados[:5],  # Primeiros 5 erros
            "linhas_invalidas_sample": linhas_invalidas[:10] if linhas_invalidas else [],  # Primeiras 10 linhas inválidas
            "encoding_usado": encoding_used,
            "total_linhas_arquivo_original": len(linhas),
            "lotes_processados": total_lotes,
            "lote_size_usado": lote_size,
            "arquivo_truncado": arquivo_truncado
        }
        
        logger.info(f"✅ [UPLOAD] FINALIZADO: {contatos_inseridos} inseridos, {contatos_duplicados} duplicados, {contatos_invalidos} com erro")
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [UPLOAD] Erro inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste."""
    logger.info("🔍 [TEST] Testando endpoint")
    return {
        "message": "Endpoint funcionando!",
        "version": "4.0.0",
        "timestamp": "2025-01-08",
        "supabase_url": SUPABASE_URL[:50] + "...",
        "status": "OK"
    }

@router.post("/debug-supabase")
async def debug_supabase():
    """Debug da conexão com Supabase."""
    logger.info("🔍 [DEBUG] Testando conexão com Supabase")
    
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        # Teste 1: Verificar se a tabela existe
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts?limit=1",
            headers=headers,
            timeout=10
        )
        
        logger.info(f"📊 [DEBUG] Teste de leitura: Status {response.status_code}")
        
        if response.status_code != 200:
            return {
                "error": "Erro na conexão com Supabase",
                "status_code": response.status_code,
                "response": response.text
            }
        
        # Teste 2: Verificar se a campanha existe
        response2 = requests.get(
            f"{SUPABASE_URL}/rest/v1/campaigns?id=eq.1",
            headers=headers,
            timeout=10
        )
        
        logger.info(f"📊 [DEBUG] Teste de campanha: Status {response2.status_code}")
        
        campaigns = response2.json() if response2.status_code == 200 else []
        
        return {
            "message": "Conexão com Supabase OK",
            "contacts_table": "OK" if response.status_code == 200 else "ERROR",
            "campaign_exists": len(campaigns) > 0,
            "campaigns_found": len(campaigns),
            "status": "SUCCESS"
        }
        
    except Exception as e:
        logger.error(f"❌ [DEBUG] Erro: {str(e)}")
        return {"error": str(e), "status": "ERROR"}

@router.post("/debug-txt")
async def debug_txt_upload(
    arquivo: UploadFile = File(...),
    incluir_nome: bool = Form(True),
    pais_preferido: str = Form("auto")
):
    """Debug específico para arquivos TXT."""
    logger.info(f"🔍 [DEBUG] Arquivo: {arquivo.filename}")
    
    try:
        conteudo = await arquivo.read()
        
        try:
            texto = conteudo.decode('utf-8')
        except UnicodeDecodeError:
            texto = conteudo.decode('latin-1')
        
        linhas = texto.strip().split('\n')
        linhas_limpas = [linha.replace('\r', '').strip() for linha in linhas]
        linhas_validas = [linha for linha in linhas_limpas if linha.strip() and validar_telefone_melhorado(linha)]
        
        return {
            "message": "Debug concluído",
            "filename": arquivo.filename,
            "size": arquivo.size,
            "total_linhas": len(linhas_validas),
            "primeiras_5_linhas": linhas_validas[:5],
            "tem_carriage_return": '\r' in texto,
            "exemplo_linha": linhas_validas[0] if linhas_validas else "Nenhuma",
            "todas_linhas_processadas": linhas_limpas[:10]  # Primeiras 10 linhas para debug
        }
        
    except Exception as e:
        logger.error(f"❌ [DEBUG] Erro: {str(e)}")
        return {"error": str(e)}

@router.get("/")
async def listar_contatos(skip: int = 0, limit: int = 100):
    """Lista contatos."""
    try:
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts?offset={skip}&limit={limit}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            contacts = response.json()
            return {"message": "Contatos listados", "total": len(contacts), "contatos": contacts}
        else:
            return {"message": "Erro ao listar contatos", "error": response.text}
            
    except Exception as e:
        return {"message": "Erro interno", "error": str(e)}

@router.options("/upload")
async def options_upload():
    """CORS para upload."""
    return {"message": "OK"}

@router.post("/test-simple")
async def test_simple():
    """Teste simples do endpoint."""
    return {"message": "Endpoint funcionando", "status": "OK"}

@router.post("/upload-large")
async def upload_large_file(
    arquivo: UploadFile = File(...),
    incluir_nome: bool = Form(True),
    pais_preferido: str = Form("auto"),
    max_registros: int = Form(10000)
):
    """
    Upload de arquivos grandes - Processamento otimizado.
    Especificamente para arquivos como Slackall.txt
    """
    logger.info(f"🚀 [UPLOAD-LARGE] Iniciando upload de arquivo grande: {arquivo.filename}")
    logger.info(f"📋 [UPLOAD-LARGE] Max registros: {max_registros}")
    
    try:
        # Usar o mesmo processamento do upload normal, mas otimizado
        if not arquivo or not arquivo.filename:
            raise HTTPException(status_code=400, detail="Arquivo não enviado")
        
        # Verificar extensão
        filename = arquivo.filename.lower()
        if not (filename.endswith('.txt') or filename.endswith('.csv')):
            raise HTTPException(
                status_code=400, 
                detail="Tipo de arquivo não suportado. Use apenas arquivos .txt ou .csv"
            )
        
        # Limite aumentado para arquivos grandes
        if arquivo.size and arquivo.size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(
                status_code=413, 
                detail="Arquivo muito grande (máximo 100MB para este endpoint)."
            )
        
        # Processar arquivo
        logger.info(f"📖 [UPLOAD-LARGE] Lendo arquivo: {arquivo.size} bytes")
        conteudo = await arquivo.read()
        
        # Decodificar
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        texto = None
        
        for encoding in encodings:
            try:
                texto = conteudo.decode(encoding)
                logger.info(f"✅ [UPLOAD-LARGE] Decodificado como {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if not texto:
            raise HTTPException(
                status_code=400, 
                detail="Não foi possível decodificar o arquivo"
            )
        
        # Processar linhas
        linhas = texto.strip().split('\n')
        logger.info(f"📄 [UPLOAD-LARGE] Total de linhas: {len(linhas)}")
        
        # Processar apenas o máximo solicitado
        if len(linhas) > max_registros:
            logger.info(f"⚠️ [UPLOAD-LARGE] Limitando a {max_registros} registros")
            linhas = linhas[:max_registros]
        
        # Processar números
        numeros_validos = []
        for i, linha in enumerate(linhas):
            linha_limpa = linha.replace('\r', '').replace('\n', '').strip()
            if linha_limpa:
                numero_normalizado = normalizar_telefone(linha_limpa)
                if validar_telefone_melhorado(numero_normalizado):
                    numeros_validos.append(numero_normalizado)
        
        logger.info(f"📊 [UPLOAD-LARGE] Números válidos: {len(numeros_validos)}")
        
        if not numeros_validos:
            raise HTTPException(
                status_code=400, 
                detail="Nenhum número válido encontrado"
            )
        
        # Processar em lotes muito pequenos (5 por vez)
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        contatos_inseridos = 0
        erros = []
        
        # Lotes de 5 para arquivos grandes
        lote_size = 5
        total_lotes = (len(numeros_validos) + lote_size - 1) // lote_size
        
        for i in range(0, len(numeros_validos), lote_size):
            lote = numeros_validos[i:i+lote_size]
            lote_num = (i // lote_size) + 1
            
            logger.info(f"📦 [UPLOAD-LARGE] Processando lote {lote_num}/{total_lotes}")
            
            dados_lote = []
            for numero in lote:
                dados_lote.append({
                    "phone_number": numero,
                    "name": "",
                    "campaign_id": 1,
                    "status": "pending",
                    "attempts": 0
                })
            
            try:
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/contacts",
                    headers=headers,
                    json=dados_lote,
                    timeout=30
                )
                
                if response.status_code == 201:
                    contatos_inseridos += len(lote)
                    logger.info(f"✅ [UPLOAD-LARGE] Lote {lote_num} inserido com sucesso")
                else:
                    logger.error(f"❌ [UPLOAD-LARGE] Erro no lote {lote_num}: {response.status_code}")
                    erros.append(f"Lote {lote_num}: {response.text}")
                    
            except Exception as e:
                logger.error(f"❌ [UPLOAD-LARGE] Erro no lote {lote_num}: {str(e)}")
                erros.append(f"Lote {lote_num}: {str(e)}")
        
        logger.info(f"🎉 [UPLOAD-LARGE] Concluído: {contatos_inseridos} contatos inseridos")
        
        return {
            "mensaje": f"Upload de arquivo grande concluído! {contatos_inseridos} contatos processados.",
            "archivo_original": arquivo.filename,
            "total_linhas_arquivo": len(linhas),
            "contatos_validos": len(numeros_validos),
            "contatos_inseridos": contatos_inseridos,
            "total_lotes": total_lotes,
            "erros": erros[:5],  # Apenas primeiros 5 erros
            "max_registros_processados": max_registros
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [UPLOAD-LARGE] Erro inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@router.options("/")
async def options_root():
    """CORS para root."""
    return {"message": "OK"} 