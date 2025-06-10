"""
Serviço de Gestão Geográfica do Sistema CODE2BASE
Responsável por gerenciar países, estados, cidades, prefixos e CLIs geográficos
"""

import csv
import json
import base64
from io import StringIO
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException

from app.models.code2base import (
    Pais, Estado, Cidade, Prefijo, CliGeo, 
    TipoOperadora, TipoNumero
)
from app.models.cli import Cli
from app.schemas.code2base import (
    PaisCreate, PaisUpdate, PaisResponse,
    EstadoCreate, EstadoUpdate, EstadoResponse,
    CidadeCreate, CidadeUpdate, CidadeResponse,
    PrefijoCreate, PrefijoUpdate, PrefijoResponse,
    CliGeoCreate, CliGeoUpdate, CliGeoResponse,
    ImportarPrefijosRequest, ImportarPrefijosResponse,
    AnalisisDestinoRequest, AnalisisDestinoResponse,
    EstadisticasCli
)
from app.schemas.lista_llamadas import validar_numero_telefone
from app.utils.logger import logger


class Code2BaseGeoService:
    """Serviço para gestão de dados geográficos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ================== GESTÃO DE PAÍSES ==================
    
    def criar_pais(self, pais_data: PaisCreate) -> PaisResponse:
        """
        Cria um novo país
        
        Args:
            pais_data: Dados do país
            
        Returns:
            PaisResponse com dados do país criado
        """
        # Verificar se já existe
        existente = self.db.query(Pais).filter(
            Pais.codigo == pais_data.codigo.upper()
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"País com código {pais_data.codigo} já existe"
            )
        
        novo_pais = Pais(
            codigo=pais_data.codigo.upper(),
            nome=pais_data.nome,
            codigo_telefone=pais_data.codigo_telefone,
            activo=pais_data.activo
        )
        
        try:
            self.db.add(novo_pais)
            self.db.commit()
            self.db.refresh(novo_pais)
            
            logger.info(f"País {novo_pais.codigo} criado")
            return PaisResponse.from_orm(novo_pais)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Erro ao criar país"
            )
    
    def listar_paises(self, skip: int = 0, limit: int = 100, apenas_ativos: bool = True) -> List[PaisResponse]:
        """Lista países"""
        query = self.db.query(Pais)
        
        if apenas_ativos:
            query = query.filter(Pais.activo == True)
        
        paises = query.offset(skip).limit(limit).all()
        return [PaisResponse.from_orm(p) for p in paises]
    
    def obter_pais(self, pais_id: int) -> PaisResponse:
        """Obtém país por ID"""
        pais = self.db.query(Pais).filter(Pais.id == pais_id).first()
        if not pais:
            raise HTTPException(status_code=404, detail="País não encontrado")
        
        return PaisResponse.from_orm(pais)
    
    def atualizar_pais(self, pais_id: int, pais_data: PaisUpdate) -> PaisResponse:
        """Atualiza país"""
        pais = self.db.query(Pais).filter(Pais.id == pais_id).first()
        if not pais:
            raise HTTPException(status_code=404, detail="País não encontrado")
        
        for field, value in pais_data.dict(exclude_unset=True).items():
            setattr(pais, field, value)
        
        pais.fecha_actualizacion = func.now()
        
        try:
            self.db.commit()
            self.db.refresh(pais)
            return PaisResponse.from_orm(pais)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao atualizar país")
    
    # ================== GESTÃO DE ESTADOS ==================
    
    def criar_estado(self, estado_data: EstadoCreate) -> EstadoResponse:
        """Cria um novo estado"""
        # Verificar se país existe
        pais = self.db.query(Pais).filter(Pais.id == estado_data.pais_id).first()
        if not pais:
            raise HTTPException(status_code=404, detail="País não encontrado")
        
        # Verificar se já existe
        existente = self.db.query(Estado).filter(
            Estado.codigo == estado_data.codigo.upper(),
            Estado.pais_id == estado_data.pais_id
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Estado com código {estado_data.codigo} já existe neste país"
            )
        
        novo_estado = Estado(
            codigo=estado_data.codigo.upper(),
            nome=estado_data.nome,
            pais_id=estado_data.pais_id,
            activo=estado_data.activo
        )
        
        try:
            self.db.add(novo_estado)
            self.db.commit()
            self.db.refresh(novo_estado)
            
            logger.info(f"Estado {novo_estado.codigo} criado")
            return EstadoResponse.from_orm(novo_estado)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao criar estado")
    
    def listar_estados(self, pais_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[EstadoResponse]:
        """Lista estados, opcionalmente filtrados por país"""
        query = self.db.query(Estado).filter(Estado.activo == True)
        
        if pais_id:
            query = query.filter(Estado.pais_id == pais_id)
        
        estados = query.offset(skip).limit(limit).all()
        return [EstadoResponse.from_orm(e) for e in estados]
    
    # ================== GESTÃO DE CIDADES ==================
    
    def criar_cidade(self, cidade_data: CidadeCreate) -> CidadeResponse:
        """Cria uma nova cidade"""
        # Verificar se estado existe
        estado = self.db.query(Estado).filter(Estado.id == cidade_data.estado_id).first()
        if not estado:
            raise HTTPException(status_code=404, detail="Estado não encontrado")
        
        nova_cidade = Cidade(
            nome=cidade_data.nome,
            codigo_postal=cidade_data.codigo_postal,
            estado_id=cidade_data.estado_id,
            activo=cidade_data.activo
        )
        
        try:
            self.db.add(nova_cidade)
            self.db.commit()
            self.db.refresh(nova_cidade)
            
            logger.info(f"Cidade {nova_cidade.nome} criada")
            return CidadeResponse.from_orm(nova_cidade)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao criar cidade")
    
    def listar_cidades(self, estado_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[CidadeResponse]:
        """Lista cidades, opcionalmente filtradas por estado"""
        query = self.db.query(Cidade).filter(Cidade.activo == True)
        
        if estado_id:
            query = query.filter(Cidade.estado_id == estado_id)
        
        cidades = query.offset(skip).limit(limit).all()
        return [CidadeResponse.from_orm(c) for c in cidades]
    
    # ================== GESTÃO DE PREFIXOS ==================
    
    def criar_prefijo(self, prefijo_data: PrefijoCreate) -> PrefijoResponse:
        """Cria um novo prefixo"""
        # Verificar se país existe
        pais = self.db.query(Pais).filter(Pais.id == prefijo_data.pais_id).first()
        if not pais:
            raise HTTPException(status_code=404, detail="País não encontrado")
        
        # Verificar se estado existe (se especificado)
        if prefijo_data.estado_id:
            estado = self.db.query(Estado).filter(Estado.id == prefijo_data.estado_id).first()
            if not estado:
                raise HTTPException(status_code=404, detail="Estado não encontrado")
        
        # Verificar se cidade existe (se especificada)
        if prefijo_data.cidade_id:
            cidade = self.db.query(Cidade).filter(Cidade.id == prefijo_data.cidade_id).first()
            if not cidade:
                raise HTTPException(status_code=404, detail="Cidade não encontrada")
        
        # Verificar se já existe
        existente = self.db.query(Prefijo).filter(
            Prefijo.codigo == prefijo_data.codigo
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Prefixo {prefijo_data.codigo} já existe"
            )
        
        novo_prefijo = Prefijo(
            codigo=prefijo_data.codigo,
            tipo_numero=prefijo_data.tipo_numero,
            operadora=prefijo_data.operadora,
            pais_id=prefijo_data.pais_id,
            estado_id=prefijo_data.estado_id,
            cidade_id=prefijo_data.cidade_id,
            descripcion=prefijo_data.descripcion,
            activo=prefijo_data.activo,
            prioridad=prefijo_data.prioridad
        )
        
        try:
            self.db.add(novo_prefijo)
            self.db.commit()
            self.db.refresh(novo_prefijo)
            
            logger.info(f"Prefixo {novo_prefijo.codigo} criado")
            return PrefijoResponse.from_orm(novo_prefijo)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao criar prefixo")
    
    def listar_prefijos(
        self, 
        pais_id: Optional[int] = None,
        estado_id: Optional[int] = None,
        tipo_numero: Optional[TipoNumero] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[PrefijoResponse]:
        """Lista prefixos com filtros opcionais"""
        query = self.db.query(Prefijo).filter(Prefijo.activo == True)
        
        if pais_id:
            query = query.filter(Prefijo.pais_id == pais_id)
        
        if estado_id:
            query = query.filter(Prefijo.estado_id == estado_id)
        
        if tipo_numero:
            query = query.filter(Prefijo.tipo_numero == tipo_numero)
        
        prefijos = query.order_by(Prefijo.prioridad, Prefijo.codigo).offset(skip).limit(limit).all()
        return [PrefijoResponse.from_orm(p) for p in prefijos]
    
    def atualizar_prefijo(self, prefijo_id: int, prefijo_data: PrefijoUpdate) -> PrefijoResponse:
        """Atualiza prefixo"""
        prefijo = self.db.query(Prefijo).filter(Prefijo.id == prefijo_id).first()
        if not prefijo:
            raise HTTPException(status_code=404, detail="Prefixo não encontrado")
        
        for field, value in prefijo_data.dict(exclude_unset=True).items():
            setattr(prefijo, field, value)
        
        prefijo.fecha_actualizacao = func.now()
        
        try:
            self.db.commit()
            self.db.refresh(prefijo)
            return PrefijoResponse.from_orm(prefijo)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao atualizar prefixo")
    
    # ================== GESTÃO DE CLIS GEOGRÁFICOS ==================
    
    def criar_cli_geo(self, cli_geo_data: CliGeoCreate) -> CliGeoResponse:
        """Cria um novo CLI geográfico"""
        # Verificar se CLI original existe
        cli_original = self.db.query(Cli).filter(Cli.id == cli_geo_data.cli_id).first()
        if not cli_original:
            raise HTTPException(status_code=404, detail="CLI original não encontrado")
        
        # Verificar se prefixo existe
        prefijo = self.db.query(Prefijo).filter(Prefijo.id == cli_geo_data.prefijo_id).first()
        if not prefijo:
            raise HTTPException(status_code=404, detail="Prefixo não encontrado")
        
        # Validar e normalizar número
        validacao = validar_numero_telefone(cli_geo_data.numero)
        if not validacao.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Número CLI inválido: {validacao.motivo_invalido}"
            )
        
        # Verificar se já existe
        existente = self.db.query(CliGeo).filter(
            or_(
                CliGeo.numero_normalizado == validacao.numero_normalizado,
                CliGeo.cli_id == cli_geo_data.cli_id
            )
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=400,
                detail="CLI geográfico já existe"
            )
        
        novo_cli_geo = CliGeo(
            numero=cli_geo_data.numero,
            numero_normalizado=validacao.numero_normalizado,
            cli_id=cli_geo_data.cli_id,
            prefijo_id=cli_geo_data.prefijo_id,
            tipo_numero=cli_geo_data.tipo_numero,
            operadora=cli_geo_data.operadora,
            calidad=cli_geo_data.calidad,
            activo=cli_geo_data.activo
        )
        
        try:
            self.db.add(novo_cli_geo)
            self.db.commit()
            self.db.refresh(novo_cli_geo)
            
            logger.info(f"CLI geográfico {novo_cli_geo.numero_normalizado} criado")
            return CliGeoResponse.from_orm(novo_cli_geo)
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao criar CLI geográfico")
    
    def listar_clis_geo(
        self,
        prefijo_id: Optional[int] = None,
        tipo_numero: Optional[TipoNumero] = None,
        operadora: Optional[TipoOperadora] = None,
        apenas_ativos: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[CliGeoResponse]:
        """Lista CLIs geográficos com filtros opcionais"""
        query = self.db.query(CliGeo)
        
        if apenas_ativos:
            query = query.filter(CliGeo.activo == True)
        
        if prefijo_id:
            query = query.filter(CliGeo.prefijo_id == prefijo_id)
        
        if tipo_numero:
            query = query.filter(CliGeo.tipo_numero == tipo_numero)
        
        if operadora:
            query = query.filter(CliGeo.operadora == operadora)
        
        clis_geo = query.order_by(CliGeo.calidad.desc(), CliGeo.tasa_exito.desc()).offset(skip).limit(limit).all()
        return [CliGeoResponse.from_orm(c) for c in clis_geo]
    
    def sincronizar_clis_existentes(self) -> Dict[str, int]:
        """
        Sincroniza CLIs existentes com a estrutura geográfica
        
        Returns:
            Dict com estatísticas da sincronização
        """
        clis_sincronizados = 0
        clis_erro = 0
        clis_sem_prefijo = 0
        
        # Buscar CLIs que não estão na tabela geográfica
        clis_existentes = self.db.query(Cli).filter(
            Cli.activo == True,
            ~Cli.id.in_(
                self.db.query(CliGeo.cli_id)
            )
        ).all()
        
        for cli in clis_existentes:
            try:
                # Detectar prefixo do CLI
                prefijo_detectado = self._detectar_prefijo_cli(cli.numero_normalizado)
                
                if not prefijo_detectado:
                    clis_sem_prefijo += 1
                    logger.warning(f"Não foi possível detectar prefixo para CLI {cli.numero_normalizado}")
                    continue
                
                # Criar CLI geográfico
                novo_cli_geo = CliGeo(
                    numero=cli.numero,
                    numero_normalizado=cli.numero_normalizado,
                    cli_id=cli.id,
                    prefijo_id=prefijo_detectado.id,
                    tipo_numero=prefijo_detectado.tipo_numero,
                    operadora=prefijo_detectado.operadora or TipoOperadora.DESCONOCIDA,
                    calidad=1.0,
                    activo=cli.activo,
                    veces_usado=cli.veces_usado,
                    ultima_vez_usado=cli.ultima_vez_usado
                )
                
                self.db.add(novo_cli_geo)
                clis_sincronizados += 1
                
            except Exception as e:
                clis_erro += 1
                logger.error(f"Erro ao sincronizar CLI {cli.numero_normalizado}: {e}")
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao confirmar sincronização: {e}")
            raise HTTPException(status_code=500, detail="Erro ao sincronizar CLIs")
        
        resultado = {
            'clis_sincronizados': clis_sincronizados,
            'clis_erro': clis_erro,
            'clis_sem_prefijo': clis_sem_prefijo,
            'total_processados': len(clis_existentes)
        }
        
        logger.info(f"Sincronização de CLIs concluída: {resultado}")
        return resultado
    
    def _detectar_prefijo_cli(self, numero_normalizado: str) -> Optional[Prefijo]:
        """
        Detecta o prefixo de um número CLI
        
        Args:
            numero_normalizado: Número normalizado
            
        Returns:
            Prefijo detectado ou None
        """
        # Tentar prefixos de diferentes tamanhos
        for tam in range(4, 1, -1):
            if len(numero_normalizado) >= tam:
                codigo_teste = numero_normalizado[:tam]
                prefijo = self.db.query(Prefijo).filter(
                    Prefijo.codigo == codigo_teste,
                    Prefijo.activo == True
                ).first()
                
                if prefijo:
                    return prefijo
        
        return None
    
    # ================== IMPORTAÇÃO DE DADOS ==================
    
    def importar_prefijos_csv(self, request: ImportarPrefijosRequest) -> ImportarPrefijosResponse:
        """
        Importa prefixos de um arquivo CSV
        
        Args:
            request: Dados da importação
            
        Returns:
            ImportarPrefijosResponse com resultados
        """
        prefijos_importados = 0
        prefijos_actualizados = 0
        prefijos_errores = 0
        errores = []
        
        try:
            # Decodificar dados CSV
            if request.archivo_csv.startswith('data:'):
                # Remover header data:text/csv;base64,
                csv_content = request.archivo_csv.split(',', 1)[1]
                csv_data = base64.b64decode(csv_content).decode('utf-8')
            else:
                csv_data = request.archivo_csv
            
            # Processar CSV
            csv_reader = csv.DictReader(StringIO(csv_data))
            
            for i, row in enumerate(csv_reader, 1):
                try:
                    # Validar campos obrigatórios
                    if not all(k in row for k in ['codigo', 'pais_codigo', 'tipo_numero']):
                        errores.append(f"Linha {i}: Campos obrigatórios ausentes")
                        prefijos_errores += 1
                        continue
                    
                    # Buscar país
                    pais = self.db.query(Pais).filter(
                        Pais.codigo == row['pais_codigo'].upper()
                    ).first()
                    
                    if not pais:
                        errores.append(f"Linha {i}: País {row['pais_codigo']} não encontrado")
                        prefijos_errores += 1
                        continue
                    
                    # Buscar estado (opcional)
                    estado_id = None
                    if row.get('estado_codigo'):
                        estado = self.db.query(Estado).filter(
                            Estado.codigo == row['estado_codigo'].upper(),
                            Estado.pais_id == pais.id
                        ).first()
                        
                        if estado:
                            estado_id = estado.id
                    
                    # Buscar cidade (opcional)
                    cidade_id = None
                    if row.get('cidade_nome') and estado_id:
                        cidade = self.db.query(Cidade).filter(
                            Cidade.nome.ilike(f"%{row['cidade_nome']}%"),
                            Cidade.estado_id == estado_id
                        ).first()
                        
                        if cidade:
                            cidade_id = cidade.id
                    
                    # Verificar se prefixo já existe
                    prefijo_existente = self.db.query(Prefijo).filter(
                        Prefijo.codigo == row['codigo']
                    ).first()
                    
                    if prefijo_existente:
                        if request.sobrescribir:
                            # Atualizar prefixo existente
                            prefijo_existente.tipo_numero = TipoNumero(row['tipo_numero'])
                            prefijo_existente.operadora = TipoOperadora(row.get('operadora', 'desconocida'))
                            prefijo_existente.pais_id = pais.id
                            prefijo_existente.estado_id = estado_id
                            prefijo_existente.cidade_id = cidade_id
                            prefijo_existente.descripcion = row.get('descripcion')
                            prefijo_existente.prioridad = int(row.get('prioridad', 1))
                            prefijo_existente.fecha_actualizacao = func.now()
                            
                            prefijos_actualizados += 1
                        else:
                            errores.append(f"Linha {i}: Prefixo {row['codigo']} já existe")
                            prefijos_errores += 1
                            continue
                    else:
                        # Criar novo prefixo
                        novo_prefijo = Prefijo(
                            codigo=row['codigo'],
                            tipo_numero=TipoNumero(row['tipo_numero']),
                            operadora=TipoOperadora(row.get('operadora', 'desconocida')),
                            pais_id=pais.id,
                            estado_id=estado_id,
                            cidade_id=cidade_id,
                            descripcion=row.get('descripcion'),
                            prioridad=int(row.get('prioridad', 1)),
                            activo=True
                        )
                        
                        self.db.add(novo_prefijo)
                        prefijos_importados += 1
                
                except Exception as e:
                    errores.append(f"Linha {i}: {str(e)}")
                    prefijos_errores += 1
            
            # Confirmar mudanças
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao processar CSV: {str(e)}"
            )
        
        return ImportarPrefijosResponse(
            prefijos_importados=prefijos_importados,
            prefijos_actualizados=prefijos_actualizados,
            prefijos_errores=prefijos_errores,
            errores=errores[:50],  # Limitar a 50 erros
            mensaje=f"Importação concluída: {prefijos_importados} criados, {prefijos_actualizados} atualizados, {prefijos_errores} erros"
        )
    
    # ================== ANÁLISE E ESTATÍSTICAS ==================
    
    def analisar_destino(self, request: AnalisisDestinoRequest) -> AnalisisDestinoResponse:
        """
        Analisa um número de destino para mostrar informações geográficas e CLIs compatíveis
        
        Args:
            request: Dados da análise
            
        Returns:
            AnalisisDestinoResponse com informações detectadas
        """
        # Validar e normalizar número
        validacao = validar_numero_telefone(request.numero_destino)
        if not validacao.valido:
            raise HTTPException(
                status_code=400,
                detail=f"Número inválido: {validacao.motivo_invalido}"
            )
        
        numero_normalizado = validacao.numero_normalizado
        
        # Detectar prefixo
        prefijo_detectado = self._detectar_prefijo_cli(numero_normalizado)
        
        # Buscar CLIs compatíveis
        clis_compatibles = []
        if prefijo_detectado:
            # CLIs do mesmo prefixo
            clis_mismo_prefijo = self.db.query(CliGeo).filter(
                CliGeo.prefijo_id == prefijo_detectado.id,
                CliGeo.activo == True
            ).all()
            
            clis_compatibles.extend(clis_mismo_prefijo)
            
            # CLIs do mesmo país se não houver do mesmo prefixo
            if not clis_compatibles:
                clis_mismo_pais = self.db.query(CliGeo).join(
                    Prefijo, CliGeo.prefijo_id == Prefijo.id
                ).filter(
                    Prefijo.pais_id == prefijo_detectado.pais_id,
                    CliGeo.activo == True
                ).limit(10).all()
                
                clis_compatibles.extend(clis_mismo_pais)
        
        return AnalisisDestinoResponse(
            numero_normalizado=numero_normalizado,
            pais_detectado=prefijo_detectado.pais.codigo if prefijo_detectado else None,
            estado_detectado=prefijo_detectado.estado.codigo if prefijo_detectado and prefijo_detectado.estado else None,
            cidade_detectada=prefijo_detectado.cidade.nome if prefijo_detectado and prefijo_detectado.cidade else None,
            prefijo_detectado=prefijo_detectado.codigo if prefijo_detectado else None,
            tipo_numero=prefijo_detectado.tipo_numero if prefijo_detectado else None,
            operadora_detectada=prefijo_detectado.operadora if prefijo_detectado else None,
            clis_compatibles=[CliGeoResponse.from_orm(c) for c in clis_compatibles],
            total_clis_compatibles=len(clis_compatibles)
        )
    
    def obter_estatisticas_cli(self) -> EstadisticasCli:
        """
        Obtém estatísticas dos CLIs geográficos
        
        Returns:
            EstadisticasCli com estatísticas
        """
        # Contadores básicos
        total_clis = self.db.query(CliGeo).count()
        clis_ativos = self.db.query(CliGeo).filter(CliGeo.activo == True).count()
        
        # CLIs por tipo
        clis_por_tipo = {}
        tipos = self.db.query(CliGeo.tipo_numero, func.count(CliGeo.id)).group_by(CliGeo.tipo_numero).all()
        for tipo, count in tipos:
            clis_por_tipo[tipo.value] = count
        
        # CLIs por operadora
        clis_por_operadora = {}
        operadoras = self.db.query(CliGeo.operadora, func.count(CliGeo.id)).group_by(CliGeo.operadora).all()
        for operadora, count in operadoras:
            clis_por_operadora[operadora.value if operadora else 'desconocida'] = count
        
        # CLIs por país
        clis_por_pais = {}
        paises = self.db.query(
            Pais.codigo, 
            func.count(CliGeo.id)
        ).join(
            Prefijo, Pais.id == Prefijo.pais_id
        ).join(
            CliGeo, Prefijo.id == CliGeo.prefijo_id
        ).group_by(Pais.codigo).all()
        
        for pais, count in paises:
            clis_por_pais[pais] = count
        
        # Taxa de sucesso promédio
        tasa_exito_promedio = self.db.query(func.avg(CliGeo.tasa_exito)).filter(
            CliGeo.activo == True
        ).scalar() or 0.0
        
        return EstadisticasCli(
            total_clis=total_clis,
            clis_ativos=clis_ativos,
            clis_por_tipo=clis_por_tipo,
            clis_por_operadora=clis_por_operadora,
            clis_por_pais=clis_por_pais,
            tasa_exito_promedio=float(tasa_exito_promedio)
        ) 