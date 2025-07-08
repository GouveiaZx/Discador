import csv
import io
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.contacts import ContactValidation
from app.schemas.lista_llamadas import validar_numero_telefone
from app.utils.logger import logger
import os

class ContactsService:
    """Service para gerenciar contatos e upload de arquivos."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def procesar_archivo_contatos(
        self, 
        archivo: UploadFile,
        incluir_nome: bool = True,
        pais_preferido: str = "auto"
    ) -> Dict[str, Any]:
        """
        Processa arquivo de contatos (CSV ou TXT).
        
        Args:
            archivo: Arquivo enviado
            incluir_nome: Se deve incluir nome nos contatos
            pais_preferido: País preferido para validação ("auto", "usa", "argentina")
            
        Returns:
            Dict com estatísticas do processamento
        """
        
        # Validar tipo de arquivo
        tipos_permitidos = [
            'text/csv', 'text/plain', 'application/csv',
            'application/vnd.ms-excel', 'text/comma-separated-values'
        ]
        
        if archivo.content_type not in tipos_permitidos:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de arquivo não suportado: {archivo.content_type}. "
                       f"Tipos aceitos: CSV, TXT"
            )
        
        try:
            # Ler conteúdo do arquivo
            conteudo = await archivo.read()
            
            # Tentar decodificar em UTF-8, depois latin-1 se falhar
            try:
                texto = conteudo.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    texto = conteudo.decode('latin-1')
                except UnicodeDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="Não foi possível decodificar o arquivo. Use UTF-8 ou ISO-8859-1"
                    )
            
            # Processar baseado na extensão
            if archivo.filename.lower().endswith('.csv'):
                contatos_processados = self._processar_csv(texto, incluir_nome)
            else:
                contatos_processados = self._processar_txt(texto, incluir_nome)
            
            # Validar e normalizar telefones
            contatos_validados = []
            contatos_invalidos = []
            telefones_duplicados = set()
            telefones_unicos = set()
            
            for contato in contatos_processados:
                telefone = contato.get('telefone', '').strip()
                
                if not telefone:
                    contatos_invalidos.append({
                        'linha': contato.get('linha', 0),
                        'erro': 'Telefone vazio'
                    })
                    continue
                
                # Validar telefone
                validacao = validar_numero_telefone(telefone, pais_preferido)
                
                if not validacao.valido:
                    contatos_invalidos.append({
                        'linha': contato.get('linha', 0),
                        'telefone': telefone,
                        'erro': validacao.motivo_invalido
                    })
                    continue
                
                # Verificar duplicados
                telefone_normalizado = validacao.numero_normalizado
                if telefone_normalizado in telefones_unicos:
                    telefones_duplicados.add(telefone_normalizado)
                    continue
                
                telefones_unicos.add(telefone_normalizado)
                
                contato_validado = {
                    'nome': contato.get('nome', ''),
                    'telefone': telefone,
                    'telefone_normalizado': telefone_normalizado,
                    'email': contato.get('email', ''),
                    'empresa': contato.get('empresa', ''),
                    'notas': contato.get('notas', ''),
                    'pais_detectado': validacao.pais_detectado,
                    'valido': True
                }
                contatos_validados.append(contato_validado)
            
            # Salvar contatos válidos no Supabase
            contatos_salvos = 0
            if contatos_validados:
                contatos_salvos = await self._salvar_contatos_supabase(contatos_validados)
            
            # Preparar resposta
            resultado = {
                'archivo_original': archivo.filename,
                'total_lineas_archivo': len(contatos_processados),
                'contatos_validos': contatos_salvos,
                'contatos_invalidos': len(contatos_invalidos),
                'contatos_duplicados': len(telefones_duplicados),
                'errores': [f"Linha {inv['linha']}: {inv['erro']}" for inv in contatos_invalidos[:10]]  # Limitar a 10 erros
            }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo de contatos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao processar arquivo: {str(e)}"
            )
    
    def _processar_csv(self, texto: str, incluir_nome: bool) -> List[Dict[str, Any]]:
        """Processa arquivo CSV."""
        contatos = []
        
        # Detectar delimitador
        delimitadores = [',', ';', '\t', '|']
        delimitador = ','
        
        for delim in delimitadores:
            if delim in texto:
                delimitador = delim
                break
        
        # Processar CSV
        reader = csv.DictReader(io.StringIO(texto), delimiter=delimitador)
        
        # Mapear colunas comuns
        mapeamento_colunas = {
            # Telefone
            'telefone': ['telefone', 'phone', 'numero', 'number', 'tel', 'celular', 'mobile'],
            # Nome
            'nome': ['nome', 'name', 'nombre', 'cliente', 'client', 'contact'],
            # Email
            'email': ['email', 'e-mail', 'mail', 'correo'],
            # Empresa
            'empresa': ['empresa', 'company', 'organizacao', 'organization'],
            # Notas
            'notas': ['notas', 'notes', 'observacoes', 'comments', 'comentarios']
        }
        
        # Detectar colunas automaticamente
        if reader.fieldnames:
            fieldnames_lower = [f.lower().strip() for f in reader.fieldnames]
            
            colunas_detectadas = {}
            for campo, opcoes in mapeamento_colunas.items():
                for opcao in opcoes:
                    if opcao in fieldnames_lower:
                        idx = fieldnames_lower.index(opcao)
                        colunas_detectadas[campo] = reader.fieldnames[idx]
                        break
            
            # Se não detectou telefone, usar primeira coluna
            if 'telefone' not in colunas_detectadas and reader.fieldnames:
                colunas_detectadas['telefone'] = reader.fieldnames[0]
        
        linha_num = 1
        for row in reader:
            linha_num += 1
            
            contato = {'linha': linha_num}
            
            # Extrair dados baseado no mapeamento
            for campo, coluna in colunas_detectadas.items():
                valor = row.get(coluna, '').strip()
                contato[campo] = valor
            
            # Garantir que telefone existe
            if 'telefone' not in contato or not contato['telefone']:
                # Tentar primeira coluna se não tem telefone
                if reader.fieldnames:
                    contato['telefone'] = row.get(reader.fieldnames[0], '').strip()
            
            contatos.append(contato)
        
        return contatos
    
    def _processar_txt(self, texto: str, incluir_nome: bool) -> List[Dict[str, Any]]:
        """Processa arquivo TXT."""
        contatos = []
        linhas = texto.strip().split('\n')
        
        for i, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha:
                continue
            
            # Tentar detectar se tem nome e telefone separados
            partes = linha.split('\t') if '\t' in linha else linha.split(',')
            
            if len(partes) >= 2 and incluir_nome:
                # Assumir que primeira parte é nome, segunda é telefone
                contato = {
                    'linha': i,
                    'nome': partes[0].strip(),
                    'telefone': partes[1].strip()
                }
                
                # Adicionar campos extras se existirem
                if len(partes) > 2:
                    contato['email'] = partes[2].strip() if len(partes) > 2 else ''
                if len(partes) > 3:
                    contato['empresa'] = partes[3].strip() if len(partes) > 3 else ''
                    
            else:
                # Assumir que toda linha é um telefone
                contato = {
                    'linha': i,
                    'telefone': linha,
                    'nome': ''
                }
            
            contatos.append(contato)
        
        return contatos
    
    async def _salvar_contatos_supabase(self, contatos: List[Dict[str, Any]]) -> int:
        """Salva contatos no Supabase."""
        try:
            # Configuração do Supabase
            SUPABASE_URL = "https://orxxocptgaeoyrtlxwkv.supabase.co"
            SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY5NzY1NTcsImV4cCI6MjA1MjU1MjU1N30.wWiJQlqd7_xKsQkQOkbJpVAMqaYHYqgUPNlWnJZWCXU"
            
            import requests
            
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            
            # Preparar dados para inserção
            dados_inserir = []
            for contato in contatos:
                dados_inserir.append({
                    "nome": contato.get('nome', ''),
                    "telefone": contato['telefone'],
                    "telefone_normalizado": contato['telefone_normalizado'],
                    "email": contato.get('email', ''),
                    "empresa": contato.get('empresa', ''),
                    "notas": contato.get('notas', ''),
                    "pais_detectado": contato.get('pais_detectado', ''),
                    "valido": True
                })
            
            # Inserir em lotes de 100
            contatos_inseridos = 0
            batch_size = 100
            
            for i in range(0, len(dados_inserir), batch_size):
                batch = dados_inserir[i:i + batch_size]
                
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/contacts",
                    headers=headers,
                    json=batch
                )
                
                if response.status_code in [200, 201]:
                    contatos_inseridos += len(batch)
                    logger.info(f"Batch {i//batch_size + 1} inserido com sucesso: {len(batch)} contatos")
                else:
                    logger.error(f"Erro ao inserir batch {i//batch_size + 1}: {response.status_code} - {response.text}")
                    # Continuar com próximo batch mesmo se um falhar
            
            return contatos_inseridos
            
        except Exception as e:
            logger.error(f"Erro ao salvar contatos no Supabase: {str(e)}")
            # Retornar 0 se falhar, mas não quebrar o processo
            return 0 