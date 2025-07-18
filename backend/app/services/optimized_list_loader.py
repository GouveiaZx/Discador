"""Serviço otimizado para carregamento de listas grandes."""

import logging
import asyncio
import csv
import io
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import UploadFile
import time
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class OptimizedListLoader:
    """Serviço otimizado para carregamento de listas grandes com processamento em lote."""
    
    def __init__(self, db: Session):
        self.db = db
        self.batch_size = 1000  # Processar em lotes de 1000
        self.max_workers = 4    # Máximo de threads para processamento
        self.progress_callbacks = {}
        self.processing_status = {}
        
    async def process_large_file(
        self,
        arquivo: UploadFile,
        nome_lista: str,
        campanha_id: Optional[int] = None,
        progress_callback_id: Optional[str] = None,
        max_records: int = 50000
    ) -> Dict[str, Any]:
        """Processa arquivo grande de forma otimizada."""
        
        start_time = time.time()
        task_id = progress_callback_id or f"task_{int(time.time())}"
        
        try:
            # Inicializar status de progresso
            self.processing_status[task_id] = {
                "status": "iniciando",
                "progress": 0,
                "total_records": 0,
                "processed_records": 0,
                "errors": [],
                "start_time": start_time
            }
            
            # Ler conteúdo do arquivo
            content = await arquivo.read()
            content_str = content.decode('utf-8', errors='ignore')
            
            # Detectar formato e separador
            file_info = self._detect_file_format(content_str)
            
            # Contar total de linhas para progresso
            total_lines = content_str.count('\n')
            self.processing_status[task_id]["total_records"] = min(total_lines, max_records)
            self.processing_status[task_id]["status"] = "processando"
            
            # Processar em lotes
            processed_count = 0
            valid_numbers = []
            errors = []
            
            # Usar StringIO para processar como CSV
            csv_reader = csv.reader(io.StringIO(content_str), delimiter=file_info["separator"])
            
            # Pular cabeçalho se existir
            if file_info["has_header"]:
                next(csv_reader, None)
            
            batch = []
            for row_num, row in enumerate(csv_reader):
                if processed_count >= max_records:
                    break
                    
                try:
                    # Extrair número da linha
                    numero = self._extract_number_from_row(row, file_info)
                    
                    if numero:
                        batch.append({
                            "numero": numero,
                            "nome": self._extract_name_from_row(row, file_info),
                            "linha": row_num + 1
                        })
                        
                        # Processar lote quando atingir o tamanho
                        if len(batch) >= self.batch_size:
                            batch_result = await self._process_batch(
                                batch, nome_lista, campanha_id, task_id
                            )
                            valid_numbers.extend(batch_result["valid"])
                            errors.extend(batch_result["errors"])
                            batch = []
                            
                            processed_count += len(batch_result["valid"])
                            
                            # Atualizar progresso
                            progress = min((processed_count / self.processing_status[task_id]["total_records"]) * 100, 100)
                            self.processing_status[task_id]["progress"] = progress
                            self.processing_status[task_id]["processed_records"] = processed_count
                            
                except Exception as e:
                    errors.append({
                        "linha": row_num + 1,
                        "erro": str(e),
                        "dados": row
                    })
            
            # Processar último lote
            if batch:
                batch_result = await self._process_batch(
                    batch, nome_lista, campanha_id, task_id
                )
                valid_numbers.extend(batch_result["valid"])
                errors.extend(batch_result["errors"])
                processed_count += len(batch_result["valid"])
            
            # Finalizar processamento
            end_time = time.time()
            processing_time = end_time - start_time
            
            self.processing_status[task_id].update({
                "status": "concluido",
                "progress": 100,
                "processed_records": processed_count,
                "processing_time": processing_time,
                "errors": errors[:100]  # Limitar erros mostrados
            })
            
            # Salvar lista no banco
            lista_id = await self._save_list_to_database(
                nome_lista, valid_numbers, campanha_id, task_id
            )
            
            result = {
                "success": True,
                "task_id": task_id,
                "lista_id": lista_id,
                "total_processed": processed_count,
                "total_errors": len(errors),
                "processing_time": processing_time,
                "records_per_second": processed_count / processing_time if processing_time > 0 else 0,
                "file_info": file_info
            }
            
            logger.info(f"✅ Lista processada: {processed_count} registros em {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento otimizado: {e}")
            self.processing_status[task_id] = {
                "status": "erro",
                "error": str(e),
                "progress": 0
            }
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def _detect_file_format(self, content: str) -> Dict[str, Any]:
        """Detecta formato do arquivo automaticamente."""
        lines = content.split('\n')[:10]  # Analisar primeiras 10 linhas
        
        # Detectar separador
        separators = [',', ';', '\t', '|']
        separator_counts = {sep: 0 for sep in separators}
        
        for line in lines:
            for sep in separators:
                separator_counts[sep] += line.count(sep)
        
        # Escolher separador mais comum
        best_separator = max(separator_counts, key=separator_counts.get)
        
        # Detectar se tem cabeçalho
        first_line = lines[0] if lines else ""
        has_header = any(keyword in first_line.lower() for keyword in 
                        ['nome', 'telefone', 'numero', 'phone', 'name', 'number'])
        
        # Detectar colunas
        if lines:
            sample_row = lines[1 if has_header else 0].split(best_separator)
            phone_column = 0
            name_column = 1 if len(sample_row) > 1 else None
            
            # Tentar detectar coluna do telefone
            for i, cell in enumerate(sample_row):
                if self._looks_like_phone(cell.strip()):
                    phone_column = i
                    break
        
        return {
            "separator": best_separator,
            "has_header": has_header,
            "phone_column": phone_column,
            "name_column": name_column,
            "total_columns": len(sample_row) if 'sample_row' in locals() else 1
        }
    
    def _looks_like_phone(self, text: str) -> bool:
        """Verifica se o texto parece um número de telefone."""
        import re
        # Remove caracteres não numéricos
        digits_only = re.sub(r'\D', '', text)
        # Telefone deve ter entre 8 e 15 dígitos
        return 8 <= len(digits_only) <= 15
    
    def _extract_number_from_row(self, row: List[str], file_info: Dict[str, Any]) -> Optional[str]:
        """Extrai número de telefone da linha."""
        try:
            if len(row) <= file_info["phone_column"]:
                return None
                
            numero_raw = row[file_info["phone_column"]].strip()
            
            # Limpar e validar número
            import re
            numero_limpo = re.sub(r'\D', '', numero_raw)
            
            # Validar tamanho
            if 8 <= len(numero_limpo) <= 15:
                return numero_limpo
                
            return None
            
        except Exception:
            return None
    
    def _extract_name_from_row(self, row: List[str], file_info: Dict[str, Any]) -> Optional[str]:
        """Extrai nome da linha se disponível."""
        try:
            name_col = file_info.get("name_column")
            if name_col is not None and len(row) > name_col:
                return row[name_col].strip()[:100]  # Limitar tamanho
            return None
        except Exception:
            return None
    
    async def _process_batch(
        self, 
        batch: List[Dict[str, Any]], 
        nome_lista: str, 
        campanha_id: Optional[int],
        task_id: str
    ) -> Dict[str, Any]:
        """Processa um lote de números."""
        
        valid_numbers = []
        errors = []
        
        # Validar e limpar números em paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for item in batch:
                future = executor.submit(self._validate_and_clean_number, item)
                futures.append(future)
            
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=5)  # Timeout de 5 segundos
                    if result["valid"]:
                        valid_numbers.append(result["data"])
                    else:
                        errors.append({
                            "linha": batch[i]["linha"],
                            "erro": result["error"],
                            "numero": batch[i]["numero"]
                        })
                except Exception as e:
                    errors.append({
                        "linha": batch[i]["linha"],
                        "erro": f"Timeout ou erro de processamento: {str(e)}",
                        "numero": batch[i]["numero"]
                    })
        
        return {
            "valid": valid_numbers,
            "errors": errors
        }
    
    def _validate_and_clean_number(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e limpa um número individual."""
        try:
            numero = item["numero"]
            
            # Validações básicas
            if not numero or len(numero) < 8:
                return {
                    "valid": False,
                    "error": "Número muito curto"
                }
            
            if len(numero) > 15:
                return {
                    "valid": False,
                    "error": "Número muito longo"
                }
            
            # Verificar se é apenas dígitos
            if not numero.isdigit():
                return {
                    "valid": False,
                    "error": "Número contém caracteres inválidos"
                }
            
            # Aplicar formatação específica por país
            numero_formatado = self._format_number_by_country(numero)
            
            return {
                "valid": True,
                "data": {
                    "numero": numero_formatado,
                    "nome": item.get("nome"),
                    "numero_original": numero
                }
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Erro na validação: {str(e)}"
            }
    
    def _format_number_by_country(self, numero: str) -> str:
        """Formata número baseado no país detectado."""
        # Brasil
        if numero.startswith('55') and len(numero) >= 12:
            return numero
        elif len(numero) == 11 and numero.startswith(('11', '21', '31', '41', '47', '48', '51', '61', '71', '81', '85')):
            return f"55{numero}"
        elif len(numero) == 10 and numero.startswith(('11', '21', '31', '41', '47', '48', '51', '61', '71', '81', '85')):
            return f"55{numero}"
        
        # EUA/Canadá
        elif numero.startswith('1') and len(numero) == 11:
            return numero
        elif len(numero) == 10 and not numero.startswith(('55', '52', '54')):
            return f"1{numero}"
        
        # México
        elif numero.startswith('52') and len(numero) >= 12:
            return numero
        elif len(numero) == 10 and numero.startswith(('55', '81', '33')):
            return f"52{numero}"
        
        # Retornar como está se não conseguir detectar
        return numero
    
    async def _save_list_to_database(
        self, 
        nome_lista: str, 
        numbers: List[Dict[str, Any]], 
        campanha_id: Optional[int],
        task_id: str
    ) -> int:
        """Salva a lista processada no banco de dados."""
        try:
            # Criar registro da lista
            insert_list_sql = """
            INSERT INTO listas_llamadas (nome, descripcion, total_numeros, campanha_id, created_at)
            VALUES (:nome, :descripcion, :total_numeros, :campanha_id, datetime('now'))
            """
            
            result = self.db.execute(text(insert_list_sql), {
                "nome": nome_lista,
                "descripcion": f"Lista processada otimizada - Task: {task_id}",
                "total_numeros": len(numbers),
                "campanha_id": campanha_id
            })
            
            lista_id = result.lastrowid
            
            # Inserir números em lotes
            batch_size = 500
            for i in range(0, len(numbers), batch_size):
                batch = numbers[i:i + batch_size]
                
                # Preparar dados para inserção
                values = []
                for num_data in batch:
                    values.append({
                        "lista_id": lista_id,
                        "numero": num_data["numero"],
                        "nome": num_data.get("nome"),
                        "numero_original": num_data.get("numero_original")
                    })
                
                # Inserir lote
                insert_numbers_sql = """
                INSERT INTO llamadas (lista_id, numero_destino, nome_contato, numero_original)
                VALUES (:lista_id, :numero, :nome, :numero_original)
                """
                
                self.db.execute(text(insert_numbers_sql), values)
            
            self.db.commit()
            logger.info(f"✅ Lista salva no banco: {lista_id} com {len(numbers)} números")
            return lista_id
            
        except Exception as e:
            logger.error(f"Erro ao salvar lista: {e}")
            self.db.rollback()
            raise
    
    def get_processing_status(self, task_id: str) -> Dict[str, Any]:
        """Obtém status do processamento."""
        return self.processing_status.get(task_id, {
            "status": "nao_encontrado",
            "error": "Task ID não encontrado"
        })
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tasks antigas do cache."""
        import time
        current_time = time.time()
        
        tasks_to_remove = []
        for task_id, status in self.processing_status.items():
            if "start_time" in status:
                age_hours = (current_time - status["start_time"]) / 3600
                if age_hours > max_age_hours:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.processing_status[task_id]
        
        logger.info(f"🧹 Removidas {len(tasks_to_remove)} tasks antigas")