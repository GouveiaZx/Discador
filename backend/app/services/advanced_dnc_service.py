"""
Serviço avançado de Do Not Call (DNC) com configuração por país.
Gerencia listas negras com diferentes configurações por país e teclas personalizáveis.
"""

from typing import Dict, List, Optional, Any, Set
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from app.utils.logger import logger

class AdvancedDNCService:
    """
    Serviço avançado para gerenciar listas DNC (Do Not Call).
    
    Funcionalidades:
    - DNC por país com configurações específicas
    - Teclas personalizáveis para remoção
    - Múltiplas listas DNC por campanha
    - Expiração automática de DNC
    - Auditoria de adições/remoções
    - Importação/exportação de listas
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.dnc_storage = {}  # Em produção, usar banco de dados
        self.country_configs = self._load_country_dnc_configs()
        self.audit_log = []
        
    def _load_country_dnc_configs(self) -> Dict[str, Dict[str, Any]]:
        """Carrega configurações DNC por país."""
        return {
            "usa": {
                "country_name": "Estados Unidos",
                "dnc_key": "2",
                "confirmation_required": True,
                "expiration_days": 365,  # DNC expira em 1 ano
                "legal_compliance": "FTC_DNC",
                "removal_confirmation": {
                    "english": "You have been removed from our calling list. Thank you.",
                    "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias."
                },
                "automatic_removal": True,
                "audit_required": True,
                "multiple_attempts_allowed": False,
                "grace_period_hours": 24
            },
            "canada": {
                "country_name": "Canadá",
                "dnc_key": "2",
                "confirmation_required": True,
                "expiration_days": 365,
                "legal_compliance": "CRTC_DNC",
                "removal_confirmation": {
                    "english": "You have been removed from our calling list. Thank you.",
                    "french": "Vous avez été retiré de notre liste d'appels. Merci."
                },
                "automatic_removal": True,
                "audit_required": True,
                "multiple_attempts_allowed": False,
                "grace_period_hours": 24
            },
            "mexico": {
                "country_name": "México",
                "dnc_key": "2",
                "confirmation_required": False,
                "expiration_days": 180,  # 6 meses
                "legal_compliance": "PROFECO",
                "removal_confirmation": {
                    "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias.",
                    "english": "You have been removed from our calling list. Thank you."
                },
                "automatic_removal": True,
                "audit_required": False,
                "multiple_attempts_allowed": True,
                "grace_period_hours": 0
            },
            "brasil": {
                "country_name": "Brasil",
                "dnc_key": "2",
                "confirmation_required": False,
                "expiration_days": 180,
                "legal_compliance": "PROCON",
                "removal_confirmation": {
                    "portuguese": "Você foi removido da nossa lista de chamadas. Obrigado.",
                    "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias."
                },
                "automatic_removal": True,
                "audit_required": False,
                "multiple_attempts_allowed": True,
                "grace_period_hours": 0
            },
            "colombia": {
                "country_name": "Colombia",
                "dnc_key": "2", 
                "confirmation_required": False,
                "expiration_days": 90,
                "legal_compliance": "SIC",
                "removal_confirmation": {
                    "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias."
                },
                "automatic_removal": True,
                "audit_required": False,
                "multiple_attempts_allowed": True,
                "grace_period_hours": 0
            },
            "argentina": {
                "country_name": "Argentina",
                "dnc_key": "2",
                "confirmation_required": False,
                "expiration_days": 180,
                "legal_compliance": "DNPDP",
                "removal_confirmation": {
                    "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias."
                },
                "automatic_removal": True,
                "audit_required": False,
                "multiple_attempts_allowed": True,
                "grace_period_hours": 0
            },
            "chile": {
                "country_name": "Chile",
                "dnc_key": "2",
                "confirmation_required": False,
                "expiration_days": 180,
                "legal_compliance": "SERNAC",
                "removal_confirmation": {
                    "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias."
                },
                "automatic_removal": True,
                "audit_required": False,
                "multiple_attempts_allowed": True,
                "grace_period_hours": 0
            },
            "peru": {
                "country_name": "Peru",
                "dnc_key": "2",
                "confirmation_required": False,
                "expiration_days": 90,
                "legal_compliance": "INDECOPI",
                "removal_confirmation": {
                    "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias."
                },
                "automatic_removal": True,
                "audit_required": False,
                "multiple_attempts_allowed": True,
                "grace_period_hours": 0
            }
        }
    
    def add_to_dnc(self, phone_number: str, country: str, campaign_id: Optional[str] = None, 
                   reason: str = "customer_request") -> Dict[str, Any]:
        """Adiciona número à lista DNC."""
        try:
            # Normalizar número de telefone
            clean_phone = self._normalize_phone_number(phone_number)
            country_key = country.lower()
            
            if country_key not in self.country_configs:
                logger.warning(f"⚠️ País {country} não configurado para DNC")
                country_key = "default"
            
            config = self.country_configs.get(country_key, self._get_default_dnc_config())
            
            # Verificar se já está na lista
            dnc_key = f"{country_key}:{clean_phone}"
            if campaign_id:
                dnc_key = f"{campaign_id}:{country_key}:{clean_phone}"
            
            if dnc_key in self.dnc_storage:
                existing_entry = self.dnc_storage[dnc_key]
                logger.info(f"📞 Número {clean_phone} já está na DNC de {country}")
                
                # Atualizar tentativas se permitido
                if config["multiple_attempts_allowed"]:
                    existing_entry["attempts"] += 1
                    existing_entry["last_attempt"] = datetime.now().isoformat()
                
                return {
                    "success": True,
                    "action": "already_exists",
                    "phone_number": clean_phone,
                    "country": country,
                    "campaign_id": campaign_id,
                    "attempts": existing_entry["attempts"],
                    "message": "Número já está na lista DNC"
                }
            
            # Calcular data de expiração
            expiration_date = None
            if config["expiration_days"] > 0:
                expiration_date = (datetime.now() + timedelta(days=config["expiration_days"])).isoformat()
            
            # Criar entrada DNC
            dnc_entry = {
                "phone_number": clean_phone,
                "country": country,
                "campaign_id": campaign_id,
                "reason": reason,
                "added_date": datetime.now().isoformat(),
                "expiration_date": expiration_date,
                "dnc_key_used": config["dnc_key"],
                "attempts": 1,
                "last_attempt": datetime.now().isoformat(),
                "legal_compliance": config["legal_compliance"],
                "confirmation_sent": False,
                "status": "active"
            }
            
            # Salvar na lista
            self.dnc_storage[dnc_key] = dnc_entry
            
            # Log de auditoria
            self._add_audit_log("ADD", clean_phone, country, campaign_id, reason)
            
            # Enviar confirmação se necessário
            confirmation_message = None
            if config["confirmation_required"]:
                confirmation_message = self._send_removal_confirmation(clean_phone, country, config)
                dnc_entry["confirmation_sent"] = True
            
            logger.info(f"✅ Número {clean_phone} adicionado à DNC de {country}")
            
            return {
                "success": True,
                "action": "added",
                "phone_number": clean_phone,
                "country": country,
                "campaign_id": campaign_id,
                "expiration_date": expiration_date,
                "confirmation_required": config["confirmation_required"],
                "confirmation_message": confirmation_message,
                "legal_compliance": config["legal_compliance"],
                "message": "Número adicionado à lista DNC com sucesso"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar {phone_number} à DNC: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "phone_number": phone_number,
                "country": country
            }
    
    def check_dnc_status(self, phone_number: str, country: str, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """Verifica se número está na lista DNC."""
        try:
            clean_phone = self._normalize_phone_number(phone_number)
            country_key = country.lower()
            
            # Verificar DNC específico da campanha primeiro
            if campaign_id:
                campaign_key = f"{campaign_id}:{country_key}:{clean_phone}"
                if campaign_key in self.dnc_storage:
                    entry = self.dnc_storage[campaign_key]
                    if self._is_dnc_active(entry):
                        return {
                            "is_dnc": True,
                            "scope": "campaign",
                            "entry": entry,
                            "reason": "Number in campaign DNC list"
                        }
            
            # Verificar DNC global do país
            global_key = f"{country_key}:{clean_phone}"
            if global_key in self.dnc_storage:
                entry = self.dnc_storage[global_key]
                if self._is_dnc_active(entry):
                    return {
                        "is_dnc": True,
                        "scope": "country",
                        "entry": entry,
                        "reason": "Number in country DNC list"
                    }
            
            return {
                "is_dnc": False,
                "scope": None,
                "entry": None,
                "reason": "Number not in DNC list"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar DNC para {phone_number}: {str(e)}")
            return {
                "is_dnc": False,
                "error": str(e)
            }
    
    def remove_from_dnc(self, phone_number: str, country: str, campaign_id: Optional[str] = None, 
                       reason: str = "manual_removal") -> Dict[str, Any]:
        """Remove número da lista DNC."""
        try:
            clean_phone = self._normalize_phone_number(phone_number)
            country_key = country.lower()
            
            removed_entries = []
            
            # Remover de campanha específica se fornecida
            if campaign_id:
                campaign_key = f"{campaign_id}:{country_key}:{clean_phone}"
                if campaign_key in self.dnc_storage:
                    removed_entries.append(self.dnc_storage[campaign_key])
                    del self.dnc_storage[campaign_key]
            
            # Remover de DNC global do país
            global_key = f"{country_key}:{clean_phone}"
            if global_key in self.dnc_storage:
                removed_entries.append(self.dnc_storage[global_key])
                del self.dnc_storage[global_key]
            
            if removed_entries:
                # Log de auditoria
                self._add_audit_log("REMOVE", clean_phone, country, campaign_id, reason)
                
                logger.info(f"✅ Número {clean_phone} removido da DNC de {country}")
                
                return {
                    "success": True,
                    "action": "removed",
                    "phone_number": clean_phone,
                    "country": country,
                    "campaign_id": campaign_id,
                    "removed_entries": len(removed_entries),
                    "message": "Número removido da lista DNC com sucesso"
                }
            else:
                return {
                    "success": True,
                    "action": "not_found",
                    "phone_number": clean_phone,
                    "country": country,
                    "message": "Número não estava na lista DNC"
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover {phone_number} da DNC: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "phone_number": phone_number,
                "country": country
            }
    
    def get_dnc_stats(self, country: Optional[str] = None, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """Obtém estatísticas da lista DNC."""
        try:
            total_entries = 0
            active_entries = 0
            expired_entries = 0
            by_country = {}
            by_campaign = {}
            
            for key, entry in self.dnc_storage.items():
                # Filtrar por país se especificado
                if country and entry["country"].lower() != country.lower():
                    continue
                
                # Filtrar por campanha se especificada
                if campaign_id and entry.get("campaign_id") != campaign_id:
                    continue
                
                total_entries += 1
                
                if self._is_dnc_active(entry):
                    active_entries += 1
                else:
                    expired_entries += 1
                
                # Estatísticas por país
                country_name = entry["country"]
                if country_name not in by_country:
                    by_country[country_name] = {"total": 0, "active": 0, "expired": 0}
                
                by_country[country_name]["total"] += 1
                if self._is_dnc_active(entry):
                    by_country[country_name]["active"] += 1
                else:
                    by_country[country_name]["expired"] += 1
                
                # Estatísticas por campanha
                camp_id = entry.get("campaign_id", "global")
                if camp_id not in by_campaign:
                    by_campaign[camp_id] = {"total": 0, "active": 0, "expired": 0}
                
                by_campaign[camp_id]["total"] += 1
                if self._is_dnc_active(entry):
                    by_campaign[camp_id]["active"] += 1
                else:
                    by_campaign[camp_id]["expired"] += 1
            
            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "expired_entries": expired_entries,
                "by_country": by_country,
                "by_campaign": by_campaign,
                "filter_country": country,
                "filter_campaign": campaign_id,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas DNC: {str(e)}")
            return {
                "error": str(e),
                "total_entries": 0
            }
    
    def cleanup_expired_dnc(self, country: Optional[str] = None) -> Dict[str, Any]:
        """Remove entradas DNC expiradas."""
        try:
            removed_count = 0
            keys_to_remove = []
            
            for key, entry in self.dnc_storage.items():
                # Filtrar por país se especificado
                if country and entry["country"].lower() != country.lower():
                    continue
                
                if not self._is_dnc_active(entry):
                    keys_to_remove.append(key)
                    self._add_audit_log("EXPIRE", entry["phone_number"], entry["country"], 
                                      entry.get("campaign_id"), "automatic_expiration")
            
            # Remover entradas expiradas
            for key in keys_to_remove:
                del self.dnc_storage[key]
                removed_count += 1
            
            logger.info(f"✅ Limpeza DNC concluída: {removed_count} entradas removidas")
            
            return {
                "success": True,
                "removed_count": removed_count,
                "filter_country": country,
                "message": f"Limpeza concluída: {removed_count} entradas expiradas removidas"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza DNC: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "removed_count": 0
            }
    
    def export_dnc_list(self, country: Optional[str] = None, campaign_id: Optional[str] = None, 
                       format: str = "json") -> Dict[str, Any]:
        """Exporta lista DNC."""
        try:
            filtered_entries = []
            
            for entry in self.dnc_storage.values():
                # Filtrar por país se especificado
                if country and entry["country"].lower() != country.lower():
                    continue
                
                # Filtrar por campanha se especificada  
                if campaign_id and entry.get("campaign_id") != campaign_id:
                    continue
                
                filtered_entries.append(entry)
            
            if format.lower() == "csv":
                # Converter para CSV
                import csv
                import io
                
                output = io.StringIO()
                if filtered_entries:
                    fieldnames = filtered_entries[0].keys()
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(filtered_entries)
                
                exported_data = output.getvalue()
                content_type = "text/csv"
            else:
                # JSON (padrão)
                exported_data = json.dumps(filtered_entries, indent=2)
                content_type = "application/json"
            
            return {
                "success": True,
                "format": format,
                "content_type": content_type,
                "data": exported_data,
                "total_entries": len(filtered_entries),
                "filter_country": country,
                "filter_campaign": campaign_id,
                "export_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar DNC: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def import_dnc_list(self, data: List[Dict[str, Any]], country: str, 
                       campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """Importa lista DNC."""
        try:
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for entry_data in data:
                try:
                    phone_number = entry_data.get("phone_number") or entry_data.get("telefone")
                    if not phone_number:
                        skipped_count += 1
                        continue
                    
                    result = self.add_to_dnc(
                        phone_number=phone_number,
                        country=country,
                        campaign_id=campaign_id,
                        reason="bulk_import"
                    )
                    
                    if result["success"]:
                        imported_count += 1
                    else:
                        skipped_count += 1
                        errors.append(f"Erro ao importar {phone_number}: {result.get('error', 'Unknown')}")
                        
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"Erro ao processar entrada: {str(e)}")
            
            logger.info(f"✅ Importação DNC concluída: {imported_count} importados, {skipped_count} ignorados")
            
            return {
                "success": True,
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "total_processed": len(data),
                "errors": errors[:10],  # Primeiros 10 erros
                "country": country,
                "campaign_id": campaign_id,
                "message": f"Importação concluída: {imported_count} números adicionados à DNC"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na importação DNC: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "imported_count": 0
            }
    
    def _normalize_phone_number(self, phone: str) -> str:
        """Normaliza número de telefone."""
        # Remove caracteres especiais
        clean = ''.join(filter(str.isdigit, phone))
        
        # Adiciona + se não tiver
        if not phone.startswith('+'):
            clean = '+' + clean
        else:
            clean = '+' + clean
        
        return clean
    
    def _is_dnc_active(self, entry: Dict[str, Any]) -> bool:
        """Verifica se entrada DNC está ativa."""
        if entry["status"] != "active":
            return False
        
        expiration_date = entry.get("expiration_date")
        if expiration_date:
            try:
                exp_datetime = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                return datetime.now() < exp_datetime
            except:
                return True  # Se não conseguir parsear, considerar ativo
        
        return True  # Sem expiração = sempre ativo
    
    def _send_removal_confirmation(self, phone_number: str, country: str, config: Dict[str, Any]) -> str:
        """Envia confirmação de remoção (simulado)."""
        confirmations = config["removal_confirmation"]
        
        # Selecionar idioma apropriado
        if "spanish" in confirmations:
            message = confirmations["spanish"]
        elif "english" in confirmations:
            message = confirmations["english"]
        else:
            message = list(confirmations.values())[0]
        
        # Em produção, aqui enviaria SMS ou faria chamada de confirmação
        logger.info(f"📞 Confirmação DNC enviada para {phone_number}: {message}")
        
        return message
    
    def _add_audit_log(self, action: str, phone_number: str, country: str, 
                      campaign_id: Optional[str], reason: str):
        """Adiciona entrada ao log de auditoria."""
        log_entry = {
            "action": action,
            "phone_number": phone_number,
            "country": country,
            "campaign_id": campaign_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "user": "system"  # Em produção, usar usuário atual
        }
        
        self.audit_log.append(log_entry)
        
        # Manter apenas últimas 1000 entradas
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def _get_default_dnc_config(self) -> Dict[str, Any]:
        """Configuração DNC padrão para países não configurados."""
        return {
            "country_name": "Default",
            "dnc_key": "2",
            "confirmation_required": False,
            "expiration_days": 180,
            "legal_compliance": "GENERIC",
            "removal_confirmation": {
                "spanish": "Ha sido removido de nuestra lista de llamadas. Gracias."
            },
            "automatic_removal": True,
            "audit_required": False,
            "multiple_attempts_allowed": True,
            "grace_period_hours": 0
        }
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtém log de auditoria."""
        return self.audit_log[-limit:] if self.audit_log else [] 