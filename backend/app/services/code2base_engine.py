"""
Motor Principal do Sistema CODE2BASE Avancado
Responsavel pela selecao inteligente de CLIs baseada em regras geograficas e de campanha
"""

import re
import time
import math
import random
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from dataclasses import dataclass

from app.models.code2base import (
    Pais, Estado, Cidade, Prefijo, CliGeo, ReglaCli, 
    HistorialSeleccionCli, TipoOperadora, TipoRegra, TipoNumero
)
from app.models.cli import Cli
from app.schemas.lista_llamadas import validar_numero_telefone
from app.schemas.code2base import (
    SeleccionCliRequest, SeleccionCliResponse, CliSeleccionado,
    AnalisisDestinoRequest, AnalisisDestinoResponse,
    ConfiguracionSistema
)
from app.utils.logger import logger


@dataclass
class CliScore:
    """Estrutura para armazenar scores de CLIs durante selecao"""
    cli_geo: CliGeo
    score_geografia: float
    score_calidad: float
    score_tasa_exito: float
    score_uso_reciente: float
    score_total: float
    reglas_aplicadas: List[str]


class Code2BaseEngine:
    """Motor principal para selecao inteligente de CLIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config = ConfiguracionSistema()
        
    def seleccionar_cli_inteligente(
        self, 
        request: SeleccionCliRequest
    ) -> SeleccionCliResponse:
        """
        Seleciona o melhor CLI para um numero de destino baseado em regras inteligentes
        
        Args:
            request: Parametros da selecao
            
        Returns:
            SeleccionCliResponse com CLI selecionado e metadados
        """
        inicio_tiempo = time.time()
        
        # Validar e normalizar numero de destino
        validacao = validar_numero_telefone(request.numero_destino)
        if not validacao.valido:
            raise ValueError(f"Numero de destino invalido: {validacao.motivo_invalido}")
        
        numero_normalizado = validacao.numero_normalizado
        
        # Analisar destino para extrair informacoes geograficas
        analisis_destino = self._analisar_destino(numero_normalizado)
        
        # Obter CLIs candidatos
        clis_candidatos = self._obter_clis_candidatos(
            numero_normalizado, 
            request, 
            analisis_destino
        )
        
        if not clis_candidatos:
            raise ValueError("Nenhum CLI disponivel para o destino especificado")
        
        # Aplicar regras de selecao
        clis_com_score = self._calcular_scores(
            clis_candidatos, 
            numero_normalizado,
            request,
            analisis_destino
        )
        
        # Selecionar melhor CLI
        cli_selecionado = self._selecionar_melhor_cli(clis_com_score)
        
        # Registrar selecao no historico
        historial = self._registrar_seleccion(
            cli_selecionado,
            numero_normalizado,
            request,
            analisis_destino
        )
        
        # Atualizar estatisticas do CLI
        self._atualizar_estatisticas_cli(cli_selecionado.cli_geo)
        
        tempo_total = (time.time() - inicio_tiempo) * 1000
        
        # Construir resposta
        cli_response = CliSeleccionado(
            id=cli_selecionado.cli_geo.id,
            numero=cli_selecionado.cli_geo.numero,
            numero_normalizado=cli_selecionado.cli_geo.numero_normalizado,
            prefijo_codigo=cli_selecionado.cli_geo.prefijo.codigo,
            tipo_numero=cli_selecionado.cli_geo.tipo_numero,
            operadora=cli_selecionado.cli_geo.operadora,
            calidad=cli_selecionado.cli_geo.calidad,
            tasa_exito=cli_selecionado.cli_geo.tasa_exito,
            score_seleccion=cli_selecionado.score_total,
            reglas_aplicadas=cli_selecionado.reglas_aplicadas
        )
        
        return SeleccionCliResponse(
            cli_seleccionado=cli_response,
            numero_destino=request.numero_destino,
            numero_destino_normalizado=numero_normalizado,
            prefijo_destino=analisis_destino.get('prefijo_detectado'),
            total_clis_disponibles=len(clis_candidatos),
            tiempo_seleccion_ms=tempo_total,
            mensaje=f"CLI {cli_response.numero_normalizado} selecionado com score {cli_selecionado.score_total:.3f}"
        )
    
    def _analisar_destino(self, numero_normalizado: str) -> Dict[str, Any]:
        """
        Analisa numero de destino para extrair informacoes geograficas
        
        Args:
            numero_normalizado: Numero normalizado
            
        Returns:
            Dict com informacoes geograficas detectadas
        """
        # Detectar prefixo do numero
        prefijo_detectado = None
        for tam in range(4, 1, -1):  # Tentar prefixos de 4, 3, 2 digitos
            if len(numero_normalizado) >= tam:
                codigo_teste = numero_normalizado[:tam]
                prefijo = self.db.query(Prefijo).filter(
                    Prefijo.codigo == codigo_teste,
                    Prefijo.activo == True
                ).first()
                
                if prefijo:
                    prefijo_detectado = prefijo
                    break
        
        resultado = {
            'numero_normalizado': numero_normalizado,
            'prefijo_detectado': prefijo_detectado.codigo if prefijo_detectado else None,
            'pais_detectado': prefijo_detectado.pais.codigo if prefijo_detectado else None,
            'estado_detectado': prefijo_detectado.estado.codigo if prefijo_detectado and prefijo_detectado.estado else None,
            'cidade_detectada': prefijo_detectado.cidade.nome if prefijo_detectado and prefijo_detectado.cidade else None,
            'tipo_numero': prefijo_detectado.tipo_numero if prefijo_detectado else None,
            'operadora_detectada': prefijo_detectado.operadora if prefijo_detectado else None
        }
        
        logger.info(f"Analise de destino para {numero_normalizado}: {resultado}")
        return resultado
    
    def _obter_clis_candidatos(
        self, 
        numero_destino: str, 
        request: SeleccionCliRequest,
        analisis_destino: Dict[str, Any]
    ) -> List[CliGeo]:
        """
        Obtem lista de CLIs candidatos baseada em criterios iniciais
        
        Args:
            numero_destino: Numero de destino normalizado
            request: Parametros da selecao
            analisis_destino: Informacoes geograficas do destino
            
        Returns:
            Lista de CliGeo candidatos
        """
        query = self.db.query(CliGeo).join(
            Prefijo, CliGeo.prefijo_id == Prefijo.id
        ).join(
            Cli, CliGeo.cli_id == Cli.id
        ).filter(
            CliGeo.activo == True,
            Cli.activo == True,
            Prefijo.activo == True
        )
        
        # Excluir CLIs especificos se solicitado
        if request.excluir_clis:
            query = query.filter(
                ~CliGeo.numero_normalizado.in_(request.excluir_clis)
            )
        
        # Filtro por tipo de numero preferido
        if request.tipo_numero_preferido:
            query = query.filter(
                CliGeo.tipo_numero == request.tipo_numero_preferido
            )
        
        # Filtro por operadora preferida
        if request.operadora_preferida:
            query = query.filter(
                CliGeo.operadora == request.operadora_preferida
            )
        
        # Aplicar limite de uso diario
        if self.config.limite_selecciones_por_cli > 0:
            hoje = datetime.now().date()
            subquery = self.db.query(
                HistorialSeleccionCli.cli_geo_id,
                func.count(HistorialSeleccionCli.id).label('usos_hoje')
            ).filter(
                func.date(HistorialSeleccionCli.fecha_seleccion) == hoje
            ).group_by(
                HistorialSeleccionCli.cli_geo_id
            ).subquery()
            
            query = query.outerjoin(
                subquery, CliGeo.id == subquery.c.cli_geo_id
            ).filter(
                or_(
                    subquery.c.usos_hoje == None,
                    subquery.c.usos_hoje < self.config.limite_selecciones_por_cli
                )
            )
        
        clis_candidatos = query.all()
        
        logger.info(f"Encontrados {len(clis_candidatos)} CLIs candidatos para {numero_destino}")
        return clis_candidatos
    
    def _calcular_scores(
        self,
        clis_candidatos: List[CliGeo],
        numero_destino: str,
        request: SeleccionCliRequest,
        analisis_destino: Dict[str, Any]
    ) -> List[CliScore]:
        """
        Calcula scores para cada CLI candidato
        
        Args:
            clis_candidatos: Lista de CLIs candidatos
            numero_destino: Numero de destino
            request: Parametros da selecao
            analisis_destino: Informacoes geograficas do destino
            
        Returns:
            Lista de CliScore ordenados por score total
        """
        clis_com_score = []
        
        for cli_geo in clis_candidatos:
            score = self._calcular_score_individual(
                cli_geo, 
                numero_destino, 
                request, 
                analisis_destino
            )
            clis_com_score.append(score)
        
        # Ordenar por score total (descendente)
        clis_com_score.sort(key=lambda x: x.score_total, reverse=True)
        
        return clis_com_score
    
    def _calcular_score_individual(
        self,
        cli_geo: CliGeo,
        numero_destino: str,
        request: SeleccionCliRequest,
        analisis_destino: Dict[str, Any]
    ) -> CliScore:
        """
        Calcula score individual de um CLI
        
        Args:
            cli_geo: CLI para calcular score
            numero_destino: Numero de destino
            request: Parametros da selecao
            analisis_destino: Informacoes geograficas do destino
            
        Returns:
            CliScore com scores detalhados
        """
        reglas_aplicadas = []
        
        # Score geografia (0.0 a 1.0)
        score_geografia = self._calcular_score_geografia(
            cli_geo, analisis_destino, reglas_aplicadas
        )
        
        # Score qualidade (0.0 a 1.0)
        score_calidad = cli_geo.calidad
        
        # Score taxa de sucesso (0.0 a 1.0)
        score_tasa_exito = cli_geo.tasa_exito
        
        # Score uso recente (0.0 a 1.0, penaliza uso muito recente)
        score_uso_reciente = self._calcular_score_uso_reciente(cli_geo)
        
        # Aplicar regras especificas
        multiplicador_reglas = self._aplicar_reglas_especificas(
            cli_geo, request, analisis_destino, reglas_aplicadas
        )
        
        # Calcular score total ponderado
        score_total = (
            score_geografia * self.config.peso_geografia +
            score_calidad * self.config.peso_calidad +
            score_tasa_exito * self.config.peso_tasa_exito +
            score_uso_reciente * self.config.peso_uso_reciente
        ) * multiplicador_reglas
        
        return CliScore(
            cli_geo=cli_geo,
            score_geografia=score_geografia,
            score_calidad=score_calidad,
            score_tasa_exito=score_tasa_exito,
            score_uso_reciente=score_uso_reciente,
            score_total=score_total,
            reglas_aplicadas=reglas_aplicadas
        )
    
    def _calcular_score_geografia(
        self,
        cli_geo: CliGeo,
        analisis_destino: Dict[str, Any],
        reglas_aplicadas: List[str]
    ) -> float:
        """
        Calcula score baseado na proximidade geografica
        
        Args:
            cli_geo: CLI para avaliar
            analisis_destino: Informacoes do destino
            reglas_aplicadas: Lista para adicionar regras aplicadas
            
        Returns:
            Score geografia entre 0.0 e 1.0
        """
        prefijo_cli = cli_geo.prefijo
        prefijo_destino = analisis_destino.get('prefijo_detectado')
        
        if not prefijo_destino:
            reglas_aplicadas.append("geografia_sin_prefijo_destino")
            return 0.5  # Score neutro se nao detectar prefixo destino
        
        # Prefixo exato = score maximo
        if prefijo_cli.codigo == prefijo_destino:
            reglas_aplicadas.append("geografia_prefijo_exacto")
            return 1.0
        
        # Mesmo pais
        pais_destino = analisis_destino.get('pais_detectado')
        if pais_destino and prefijo_cli.pais.codigo == pais_destino:
            reglas_aplicadas.append("geografia_mismo_pais")
            
            # Mesmo estado = score alto
            estado_destino = analisis_destino.get('estado_detectado')
            if estado_destino and prefijo_cli.estado and prefijo_cli.estado.codigo == estado_destino:
                reglas_aplicadas.append("geografia_mismo_estado")
                return 0.8
            
            # Mesmo pais mas estado diferente = score medio
            return 0.6
        
        # Paises diferentes = score baixo
        reglas_aplicadas.append("geografia_pais_diferente")
        return 0.2
    
    def _calcular_score_uso_reciente(self, cli_geo: CliGeo) -> float:
        """
        Calcula score baseado no uso recente (penaliza uso muito recente)
        
        Args:
            cli_geo: CLI para avaliar
            
        Returns:
            Score uso recente entre 0.0 e 1.0
        """
        if not cli_geo.ultima_vez_usado:
            return 1.0  # Nunca usado = score maximo
        
        agora = datetime.now()
        tempo_desde_uso = agora - cli_geo.ultima_vez_usado
        horas_desde_uso = tempo_desde_uso.total_seconds() / 3600
        
        # Penalizar uso nas ultimas 24 horas
        if horas_desde_uso < 1:
            return 0.3  # Usado ha menos de 1 hora
        elif horas_desde_uso < 6:
            return 0.6  # Usado ha menos de 6 horas
        elif horas_desde_uso < 24:
            return 0.8  # Usado ha menos de 24 horas
        else:
            return 1.0  # Usado ha mais de 24 horas
    
    def _aplicar_reglas_especificas(
        self,
        cli_geo: CliGeo,
        request: SeleccionCliRequest,
        analisis_destino: Dict[str, Any],
        reglas_aplicadas: List[str]
    ) -> float:
        """
        Aplica reglas especificas configuradas no sistema
        
        Args:
            cli_geo: CLI para avaliar
            request: Parametros da selecao
            analisis_destino: Informacoes do destino
            reglas_aplicadas: Lista para adicionar regras aplicadas
            
        Returns:
            Multiplicador para aplicar ao score (0.0 a 2.0)
        """
        # Obter regras ativas ordenadas por prioridade
        query = self.db.query(ReglaCli).filter(
            ReglaCli.activo == True
        ).order_by(ReglaCli.prioridad)
        
        # Filtrar por campanha se especificada
        if request.campana_id:
            query = query.filter(
                or_(
                    ReglaCli.aplica_a_campana == False,
                    and_(
                        ReglaCli.aplica_a_campana == True,
                        ReglaCli.campana_ids.contains([request.campana_id])
                    )
                )
            )
        
        reglas = query.all()
        multiplicador_total = 1.0
        
        for regla in reglas:
            if self._evaluar_regla(regla, cli_geo, request, analisis_destino):
                multiplicador_total *= regla.peso
                reglas_aplicadas.append(f"regla_{regla.nome}")
        
        return max(0.0, min(2.0, multiplicador_total))  # Limitar entre 0.0 e 2.0
    
    def _evaluar_regla(
        self,
        regla: ReglaCli,
        cli_geo: CliGeo,
        request: SeleccionCliRequest,
        analisis_destino: Dict[str, Any]
    ) -> bool:
        """
        Avalia se uma regra se aplica ao CLI atual
        
        Args:
            regla: Regra a avaliar
            cli_geo: CLI para avaliar
            request: Parametros da selecao
            analisis_destino: Informacoes do destino
            
        Returns:
            True se a regra se aplica
        """
        try:
            condiciones = regla.condiciones
            
            # Avaliar condicoes de geografia
            if 'pais' in condiciones:
                if cli_geo.prefijo.pais.codigo != condiciones['pais']:
                    return False
            
            if 'estado' in condiciones:
                if not cli_geo.prefijo.estado or cli_geo.prefijo.estado.codigo != condiciones['estado']:
                    return False
            
            if 'prefijo' in condiciones:
                if cli_geo.prefijo.codigo != condiciones['prefijo']:
                    return False
            
            # Avaliar condicoes de tipo
            if 'tipo_numero' in condiciones:
                if cli_geo.tipo_numero.value != condiciones['tipo_numero']:
                    return False
            
            if 'operadora' in condiciones:
                if cli_geo.operadora.value != condiciones['operadora']:
                    return False
            
            # Avaliar condicoes de qualidade
            if 'calidad_minima' in condiciones:
                if cli_geo.calidad < condiciones['calidad_minima']:
                    return False
            
            if 'tasa_exito_minima' in condiciones:
                if cli_geo.tasa_exito < condiciones['tasa_exito_minima']:
                    return False
            
            # Avaliar condicoes de horario
            if 'horario' in condiciones:
                agora = datetime.now()
                hora_atual = agora.strftime('%H:%M')
                horario = condiciones['horario']
                
                if 'inicio' in horario and 'fim' in horario:
                    if not (horario['inicio'] <= hora_atual <= horario['fim']):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao avaliar regra {regla.nome}: {e}")
            return False
    
    def _selecionar_melhor_cli(self, clis_com_score: List[CliScore]) -> CliScore:
        """
        Seleciona o melhor CLI da lista de candidatos com score
        
        Args:
            clis_com_score: Lista de CLIs com scores calculados
            
        Returns:
            CliScore do CLI selecionado
        """
        if not clis_com_score:
            raise ValueError("Nenhum CLI candidato disponivel")
        
        # Usar algoritmo configurado
        if self.config.algoritmo_seleccion == "highest_score":
            return clis_com_score[0]  # Ja ordenado por score descendente
        
        elif self.config.algoritmo_seleccion == "weighted_random":
            # Selecao aleatoria ponderada pelos scores
            scores = [cli.score_total for cli in clis_com_score]
            pesos = [max(0.1, score) for score in scores]  # Evitar pesos zero
            
            return random.choices(clis_com_score, weights=pesos, k=1)[0]
        
        else:  # weighted_score (padrao)
            # Combinar score mais alto com aleatoriedade
            top_10_percent = max(1, len(clis_com_score) // 10)
            candidatos_top = clis_com_score[:top_10_percent]
            
            return random.choice(candidatos_top)
    
    def _registrar_seleccion(
        self,
        cli_selecionado: CliScore,
        numero_destino: str,
        request: SeleccionCliRequest,
        analisis_destino: Dict[str, Any]
    ) -> HistorialSeleccionCli:
        """
        Registra a selecao no historico para auditoria
        
        Args:
            cli_selecionado: CLI selecionado
            numero_destino: Numero de destino
            request: Parametros da selecao
            analisis_destino: Informacoes do destino
            
        Returns:
            HistorialSeleccionCli criado
        """
        historial = HistorialSeleccionCli(
            numero_destino=request.numero_destino,
            numero_destino_normalizado=numero_destino,
            campana_id=request.campana_id,
            cli_geo_id=cli_selecionado.cli_geo.id,
            cli_numero=cli_selecionado.cli_geo.numero_normalizado,
            prefijo_destino=analisis_destino.get('prefijo_detectado'),
            reglas_aplicadas=cli_selecionado.reglas_aplicadas,
            score_seleccion=cli_selecionado.score_total
        )
        
        self.db.add(historial)
        self.db.commit()
        self.db.refresh(historial)
        
        return historial
    
    def _atualizar_estatisticas_cli(self, cli_geo: CliGeo) -> None:
        """
        Atualiza estatisticas do CLI selecionado
        
        Args:
            cli_geo: CLI a atualizar
        """
        cli_geo.veces_usado += 1
        cli_geo.ultima_vez_usado = func.now()
        
        # Atualizar CLI original tambem
        cli_original = self.db.query(Cli).filter(Cli.id == cli_geo.cli_id).first()
        if cli_original:
            cli_original.veces_usado += 1
            cli_original.ultima_vez_usado = func.now()
        
        self.db.commit()
    
    def atualizar_resultado_llamada(
        self, 
        numero_destino: str, 
        cli_numero: str, 
        exitosa: bool, 
        duracion: Optional[int] = None
    ) -> bool:
        """
        Atualiza o resultado de uma chamada para melhorar os scores futuros
        
        Args:
            numero_destino: Numero de destino da chamada
            cli_numero: CLI utilizado
            exitosa: Se a chamada foi exitosa
            duracion: Duracao da chamada em segundos
            
        Returns:
            True se atualizou com sucesso
        """
        try:
            validacao = validar_numero_telefone(numero_destino)
            if not validacao.valido:
                return False
            
            numero_normalizado = validacao.numero_normalizado
            
            # Buscar historico mais recente
            historial = self.db.query(HistorialSeleccionCli).filter(
                HistorialSeleccionCli.numero_destino_normalizado == numero_normalizado,
                HistorialSeleccionCli.cli_numero == cli_numero,
                HistorialSeleccionCli.llamada_exitosa == None
            ).order_by(desc(HistorialSeleccionCli.fecha_seleccion)).first()
            
            if not historial:
                return False
            
            # Atualizar historico
            historial.llamada_exitosa = exitosa
            historial.duracion_llamada = duracion
            historial.fecha_resultado = func.now()
            
            # Atualizar taxa de sucesso do CLI
            cli_geo = historial.cli_geo
            if cli_geo:
                self._recalcular_tasa_exito_cli(cli_geo)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar resultado da chamada: {e}")
            self.db.rollback()
            return False
    
    def _recalcular_tasa_exito_cli(self, cli_geo: CliGeo) -> None:
        """
        Recalcula a taxa de sucesso de um CLI baseada no historico
        
        Args:
            cli_geo: CLI para recalcular
        """
        # Buscar historico dos ultimos 30 dias
        data_limite = datetime.now() - timedelta(days=30)
        
        historiales = self.db.query(HistorialSeleccionCli).filter(
            HistorialSeleccionCli.cli_geo_id == cli_geo.id,
            HistorialSeleccionCli.llamada_exitosa != None,
            HistorialSeleccionCli.fecha_resultado >= data_limite
        ).all()
        
        if historiales:
            exitosas = sum(1 for h in historiales if h.llamada_exitosa)
            tasa_exito = exitosas / len(historiales)
            cli_geo.tasa_exito = tasa_exito 