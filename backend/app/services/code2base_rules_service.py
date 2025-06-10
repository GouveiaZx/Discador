"""
Serviço de Gestão de Regras do Sistema CODE2BASE
Responsável por gerenciar regras de seleção inteligente de CLIs
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException

from app.models.code2base import (
    ReglaCli, TipoRegra, TipoOperadora, TipoNumero,
    HistorialSeleccionCli, CliGeo, Prefijo, Pais, Estado
)
from app.schemas.code2base import (
    ReglaCliCreate, ReglaCliUpdate, ReglaCliResponse,
    EstadisticasSeleccion, ConfiguracionSistema, ConfiguracionSistemaResponse,
    TesteSistemaRequest, TesteSistemaResponse
)
from app.utils.logger import logger


class Code2BaseRulesService:
    """Serviço para gestão de regras de seleção de CLI"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ================== GESTÃO DE REGRAS ==================
    
    def criar_regra(self, regla_data: ReglaCliCreate) -> ReglaCliResponse:
        """
        Cria uma nova regra de seleção de CLI
        
        Args:
            regla_data: Dados da regra
            
        Returns:
            ReglaCliResponse com dados da regra criada
        """
        # Validar condições JSON
        if not self._validar_condiciones(regla_data.condiciones):
            raise HTTPException(
                status_code=400,
                detail="Condições da regra inválidas"
            )
        
        nova_regla = ReglaCli(
            nome=regla_data.nome,
            descripcion=regla_data.descripcion,
            tipo_regra=regla_data.tipo_regra,
            condiciones=regla_data.condiciones,
            prioridad=regla_data.prioridad,
            peso=regla_data.peso,
            activo=regla_data.activo,
            aplica_a_campaña=regla_data.aplica_a_campaña,
            campaña_ids=regla_data.campaña_ids
        )
        
        try:
            self.db.add(nova_regla)
            self.db.commit()
            self.db.refresh(nova_regla)
            
            logger.info(f"Regra {nova_regla.nome} criada")
            return ReglaCliResponse.from_orm(nova_regla)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Erro ao criar regra"
            )
    
    def listar_regras(
        self, 
        tipo_regra: Optional[TipoRegra] = None,
        apenas_ativas: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ReglaCliResponse]:
        """Lista regras com filtros opcionais"""
        query = self.db.query(ReglaCli)
        
        if apenas_ativas:
            query = query.filter(ReglaCli.activo == True)
        
        if tipo_regra:
            query = query.filter(ReglaCli.tipo_regra == tipo_regra)
        
        reglas = query.order_by(ReglaCli.prioridad, ReglaCli.nome).offset(skip).limit(limit).all()
        return [ReglaCliResponse.from_orm(r) for r in reglas]
    
    def obter_regra(self, regla_id: int) -> ReglaCliResponse:
        """Obtém regra por ID"""
        regla = self.db.query(ReglaCli).filter(ReglaCli.id == regla_id).first()
        if not regla:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        
        return ReglaCliResponse.from_orm(regla)
    
    def atualizar_regra(self, regla_id: int, regla_data: ReglaCliUpdate) -> ReglaCliResponse:
        """Atualiza regra"""
        regla = self.db.query(ReglaCli).filter(ReglaCli.id == regla_id).first()
        if not regla:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        
        # Validar novas condições se fornecidas
        if regla_data.condiciones is not None:
            if not self._validar_condiciones(regla_data.condiciones):
                raise HTTPException(
                    status_code=400,
                    detail="Condições da regra inválidas"
                )
        
        for field, value in regla_data.dict(exclude_unset=True).items():
            setattr(regla, field, value)
        
        regla.fecha_actualizacao = func.now()
        
        try:
            self.db.commit()
            self.db.refresh(regla)
            return ReglaCliResponse.from_orm(regla)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao atualizar regra")
    
    def remover_regra(self, regla_id: int) -> bool:
        """Remove regra (soft delete)"""
        regla = self.db.query(ReglaCli).filter(ReglaCli.id == regla_id).first()
        if not regla:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        
        regla.activo = False
        regla.fecha_actualizacao = func.now()
        
        self.db.commit()
        logger.info(f"Regra {regla.nome} removida")
        return True
    
    def _validar_condiciones(self, condiciones: Dict[str, Any]) -> bool:
        """
        Valida se as condições da regra são válidas
        
        Args:
            condiciones: Condições a validar
            
        Returns:
            True se válidas
        """
        try:
            # Verificar tipos de dados válidos
            campos_validos = {
                'pais', 'estado', 'prefijo', 'cidade', 
                'tipo_numero', 'operadora', 
                'calidad_minima', 'tasa_exito_minima',
                'horario', 'dia_semana'
            }
            
            for campo in condiciones.keys():
                if campo not in campos_validos:
                    logger.warning(f"Campo {campo} não é válido em condições de regra")
                    return False
            
            # Validações específicas
            if 'calidad_minima' in condiciones:
                valor = condiciones['calidad_minima']
                if not isinstance(valor, (int, float)) or not (0.0 <= valor <= 1.0):
                    return False
            
            if 'tasa_exito_minima' in condiciones:
                valor = condiciones['tasa_exito_minima']
                if not isinstance(valor, (int, float)) or not (0.0 <= valor <= 1.0):
                    return False
            
            if 'tipo_numero' in condiciones:
                try:
                    TipoNumero(condiciones['tipo_numero'])
                except ValueError:
                    return False
            
            if 'operadora' in condiciones:
                try:
                    TipoOperadora(condiciones['operadora'])
                except ValueError:
                    return False
            
            if 'horario' in condiciones:
                horario = condiciones['horario']
                if not isinstance(horario, dict):
                    return False
                
                if 'inicio' in horario and 'fim' in horario:
                    # Validar formato HH:MM
                    import re
                    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
                    if not re.match(pattern, horario['inicio']) or not re.match(pattern, horario['fim']):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar condições: {e}")
            return False
    
    # ================== REGRAS PRÉ-DEFINIDAS ==================
    
    def criar_regras_padrao(self) -> List[ReglaCliResponse]:
        """
        Cria regras padrão do sistema
        
        Returns:
            Lista de regras criadas
        """
        regras_padrao = [
            {
                'nome': 'Priorizar mesmo prefixo',
                'descripcion': 'Dar prioridade máxima a CLIs do mesmo prefixo que o destino',
                'tipo_regra': TipoRegra.GEOGRAFIA,
                'condiciones': {'mismo_prefijo': True},
                'prioridad': 1,
                'peso': 1.5,
                'activo': True,
                'aplica_a_campaña': False
            },
            {
                'nome': 'Qualidade mínima móvel',
                'descripcion': 'CLIs móveis devem ter qualidade mínima de 0.7',
                'tipo_regra': TipoRegra.GEOGRAFIA,
                'condiciones': {'tipo_numero': 'movil', 'calidad_minima': 0.7},
                'prioridad': 2,
                'peso': 1.2,
                'activo': True,
                'aplica_a_campaña': False
            },
            {
                'nome': 'Horário comercial Movistar',
                'descripcion': 'Usar Movistar apenas em horário comercial',
                'tipo_regra': TipoRegra.HORARIO,
                'condiciones': {
                    'operadora': 'movistar',
                    'horario': {'inicio': '09:00', 'fim': '18:00'}
                },
                'prioridad': 3,
                'peso': 1.1,
                'activo': True,
                'aplica_a_campaña': False
            },
            {
                'nome': 'Taxa de sucesso mínima',
                'descripcion': 'CLIs devem ter taxa de sucesso mínima de 0.3',
                'tipo_regra': TipoRegra.GEOGRAFIA,
                'condiciones': {'tasa_exito_minima': 0.3},
                'prioridad': 4,
                'peso': 1.0,
                'activo': True,
                'aplica_a_campaña': False
            },
            {
                'nome': 'Fallback geral',
                'descripcion': 'Regra de fallback para quando nenhuma outra se aplica',
                'tipo_regra': TipoRegra.FALLBACK,
                'condiciones': {},
                'prioridad': 10,
                'peso': 0.8,
                'activo': True,
                'aplica_a_campaña': False
            }
        ]
        
        regras_criadas = []
        
        for regra_data in regras_padrao:
            # Verificar se já existe
            existente = self.db.query(ReglaCli).filter(
                ReglaCli.nome == regra_data['nome']
            ).first()
            
            if not existente:
                try:
                    nova_regla = ReglaCli(**regra_data)
                    self.db.add(nova_regla)
                    self.db.commit()
                    self.db.refresh(nova_regla)
                    
                    regras_criadas.append(ReglaCliResponse.from_orm(nova_regla))
                    logger.info(f"Regra padrão '{regla_data['nome']}' criada")
                    
                except Exception as e:
                    self.db.rollback()
                    logger.error(f"Erro ao criar regra padrão '{regla_data['nome']}': {e}")
        
        return regras_criadas
    
    # ================== ESTATÍSTICAS ==================
    
    def obter_estatisticas_seleccion(self) -> EstadisticasSeleccion:
        """
        Obtém estatísticas das seleções de CLI
        
        Returns:
            EstadisticasSeleccion com estatísticas
        """
        # Contadores básicos
        total_selecciones = self.db.query(HistorialSeleccionCli).count()
        selecciones_exitosas = self.db.query(HistorialSeleccionCli).filter(
            HistorialSeleccionCli.llamada_exitosa == True
        ).count()
        
        # Taxa de sucesso global
        tasa_exito_global = selecciones_exitosas / total_selecciones if total_selecciones > 0 else 0.0
        
        # Prefixos mais usados
        prefijos_mas_usados = self.db.query(
            HistorialSeleccionCli.prefijo_destino,
            func.count(HistorialSeleccionCli.id).label('count')
        ).filter(
            HistorialSeleccionCli.prefijo_destino != None
        ).group_by(
            HistorialSeleccionCli.prefijo_destino
        ).order_by(
            desc('count')
        ).limit(10).all()
        
        prefijos_lista = [
            {'prefijo': prefijo, 'count': count}
            for prefijo, count in prefijos_mas_usados
        ]
        
        # Operadoras mais exitosas
        operadoras_exitosas = self.db.query(
            CliGeo.operadora,
            func.count(HistorialSeleccionCli.id).label('total'),
            func.sum(func.case([(HistorialSeleccionCli.llamada_exitosa == True, 1)], else_=0)).label('exitosas')
        ).join(
            HistorialSeleccionCli, CliGeo.id == HistorialSeleccionCli.cli_geo_id
        ).filter(
            HistorialSeleccionCli.llamada_exitosa != None
        ).group_by(
            CliGeo.operadora
        ).all()
        
        operadoras_lista = []
        for operadora, total, exitosas in operadoras_exitosas:
            if total > 0:
                tasa_exito = (exitosas or 0) / total
                operadoras_lista.append({
                    'operadora': operadora.value if operadora else 'desconocida',
                    'total': total,
                    'exitosas': exitosas or 0,
                    'tasa_exito': tasa_exito
                })
        
        # Ordenar por taxa de sucesso
        operadoras_lista.sort(key=lambda x: x['tasa_exito'], reverse=True)
        
        return EstadisticasSeleccion(
            total_selecciones=total_selecciones,
            selecciones_exitosas=selecciones_exitosas,
            tasa_exito_global=tasa_exito_global,
            prefijos_mas_usados=prefijos_lista,
            operadoras_mas_exitosas=operadoras_lista[:10]
        )
    
    # ================== CONFIGURAÇÃO DO SISTEMA ==================
    
    def obter_configuracion(self) -> ConfiguracionSistemaResponse:
        """Obtém configuração atual do sistema"""
        # Por enquanto, retorna configuração padrão
        # Em uma implementação futura, poderia ser armazenada no banco
        config = ConfiguracionSistema()
        
        return ConfiguracionSistemaResponse(
            **config.dict(),
            fecha_actualizacion=datetime.now(),
            usuario_actualizacion="sistema"
        )
    
    def atualizar_configuracion(self, config: ConfiguracionSistema) -> ConfiguracionSistemaResponse:
        """
        Atualiza configuração do sistema
        
        Args:
            config: Nova configuração
            
        Returns:
            ConfiguracionSistemaResponse atualizada
        """
        # Validar soma dos pesos
        total_peso = (
            config.peso_geografia + 
            config.peso_calidad + 
            config.peso_tasa_exito + 
            config.peso_uso_reciente
        )
        
        if abs(total_peso - 1.0) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Soma dos pesos deve ser 1.0, atual: {total_peso}"
            )
        
        # Por enquanto, apenas retorna a configuração
        # Em uma implementação futura, seria armazenada no banco
        logger.info(f"Configuração atualizada: {config.dict()}")
        
        return ConfiguracionSistemaResponse(
            **config.dict(),
            fecha_actualizacion=datetime.now(),
            usuario_actualizacion="usuario"
        )
    
    # ================== TESTES E SIMULAÇÕES ==================
    
    def testar_sistema(self, request: TesteSistemaRequest) -> TesteSistemaResponse:
        """
        Testa o sistema com múltiplas simulações
        
        Args:
            request: Parâmetros do teste
            
        Returns:
            TesteSistemaResponse com resultados
        """
        from app.services.code2base_engine import Code2BaseEngine
        from app.schemas.code2base import SeleccionCliRequest
        
        engine = Code2BaseEngine(self.db)
        
        clis_seleccionados = []
        distribucion_prefijo = {}
        distribucion_operadora = {}
        scores_totales = []
        tiempos_totales = []
        
        for i in range(request.simulaciones):
            try:
                # Criar requisição de seleção
                seleccion_request = SeleccionCliRequest(
                    numero_destino=request.numero_destino,
                    campaña_id=request.campaña_id
                )
                
                # Executar seleção
                resultado = engine.seleccionar_cli_inteligente(seleccion_request)
                
                # Coletar estatísticas
                cli_info = {
                    'numero': resultado.cli_seleccionado.numero_normalizado,
                    'prefijo': resultado.cli_seleccionado.prefijo_codigo,
                    'operadora': resultado.cli_seleccionado.operadora.value if resultado.cli_seleccionado.operadora else 'desconocida',
                    'score': resultado.cli_seleccionado.score_seleccion,
                    'tiempo_ms': resultado.tiempo_seleccion_ms
                }
                
                clis_seleccionados.append(cli_info)
                scores_totales.append(resultado.cli_seleccionado.score_seleccion)
                tiempos_totales.append(resultado.tiempo_seleccion_ms)
                
                # Distribuição por prefixo
                prefijo = resultado.cli_seleccionado.prefijo_codigo
                distribucion_prefijo[prefijo] = distribucion_prefijo.get(prefijo, 0) + 1
                
                # Distribuição por operadora
                operadora = resultado.cli_seleccionado.operadora.value if resultado.cli_seleccionado.operadora else 'desconocida'
                distribucion_operadora[operadora] = distribucion_operadora.get(operadora, 0) + 1
                
            except Exception as e:
                logger.error(f"Erro na simulação {i}: {e}")
                continue
        
        # Calcular médias
        score_promedio = sum(scores_totales) / len(scores_totales) if scores_totales else 0.0
        tiempo_promedio = sum(tiempos_totales) / len(tiempos_totales) if tiempos_totales else 0.0
        
        # Gerar recomendações
        recomendaciones = self._gerar_recomendaciones(
            distribucion_prefijo, 
            distribucion_operadora, 
            score_promedio
        )
        
        return TesteSistemaResponse(
            numero_destino=request.numero_destino,
            total_simulaciones=len(clis_seleccionados),
            clis_seleccionados=clis_seleccionados,
            distribucion_por_prefijo=distribucion_prefijo,
            distribucion_por_operadora=distribucion_operadora,
            score_promedio=score_promedio,
            tiempo_promedio_ms=tiempo_promedio,
            recomendaciones=recomendaciones
        )
    
    def _gerar_recomendaciones(
        self, 
        distribucion_prefijo: Dict[str, int],
        distribucion_operadora: Dict[str, int],
        score_promedio: float
    ) -> List[str]:
        """
        Gera recomendações baseadas nos resultados dos testes
        
        Args:
            distribucion_prefijo: Distribuição por prefixo
            distribucion_operadora: Distribuição por operadora
            score_promedio: Score promédio
            
        Returns:
            Lista de recomendações
        """
        recomendaciones = []
        
        # Análise de diversidade de prefixos
        if len(distribucion_prefijo) == 1:
            recomendaciones.append("Sistema está selecionando sempre o mesmo prefixo. Considere adicionar mais CLIs ou ajustar regras.")
        elif len(distribucion_prefijo) > 5:
            recomendaciones.append("Boa diversidade de prefixos. Sistema está funcionando corretamente.")
        
        # Análise de operadoras
        if len(distribucion_operadora) == 1:
            recomendaciones.append("Sistema está usando apenas uma operadora. Considere diversificar CLIs.")
        
        # Análise de score
        if score_promedio < 0.5:
            recomendaciones.append("Score promédio baixo. Revise as regras de seleção e qualidade dos CLIs.")
        elif score_promedio > 0.8:
            recomendaciones.append("Excelente score promédio. Sistema otimizado.")
        
        # Análise de concentração
        total_selecciones = sum(distribucion_prefijo.values())
        prefijo_mais_usado = max(distribucion_prefijo.values()) if distribucion_prefijo else 0
        concentracao = prefijo_mais_usado / total_selecciones if total_selecciones > 0 else 0
        
        if concentracao > 0.7:
            recomendaciones.append("Alta concentração em um prefixo. Considere balancear a seleção.")
        
        if not recomendaciones:
            recomendaciones.append("Sistema funcionando dentro dos parâmetros esperados.")
        
        return recomendaciones 