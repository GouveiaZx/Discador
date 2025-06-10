"""
APIs REST para o Sistema CODE2BASE Avançado
Endpoints para seleção inteligente de CLIs baseada em geografia e regras
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.code2base_engine import Code2BaseEngine
from app.services.code2base_geo_service import Code2BaseGeoService
from app.services.code2base_rules_service import Code2BaseRulesService
from app.models.code2base import TipoOperadora, TipoRegra, TipoNumero
from app.schemas.code2base import (
    # Esquemas de países
    PaisCreate, PaisUpdate, PaisResponse,
    # Esquemas de estados
    EstadoCreate, EstadoUpdate, EstadoResponse,
    # Esquemas de cidades
    CidadeCreate, CidadeUpdate, CidadeResponse,
    # Esquemas de prefixos
    PrefijoCreate, PrefijoUpdate, PrefijoResponse,
    # Esquemas de CLIs geográficos
    CliGeoCreate, CliGeoUpdate, CliGeoResponse,
    # Esquemas de regras
    ReglaCliCreate, ReglaCliUpdate, ReglaCliResponse,
    # Esquemas de seleção
    SeleccionCliRequest, SeleccionCliResponse,
    # Esquemas de análise
    AnalisisDestinoRequest, AnalisisDestinoResponse,
    # Esquemas de importação
    ImportarPrefijosRequest, ImportarPrefijosResponse,
    # Esquemas de estatísticas
    EstadisticasCli, EstadisticasSeleccion, ReporteSistemaResponse,
    # Esquemas de configuração
    ConfiguracionSistema, ConfiguracionSistemaResponse,
    # Esquemas de teste
    TesteSistemaRequest, TesteSistemaResponse
)
from app.utils.logger import logger

router = APIRouter(prefix="/code2base", tags=["CODE2BASE - Sistema CLI Inteligente"])


# ================== SELEÇÃO INTELIGENTE DE CLI ==================

@router.post("/seleccionar-cli", response_model=SeleccionCliResponse)
async def seleccionar_cli_inteligente(
    request: SeleccionCliRequest,
    db: Session = Depends(get_db)
):
    """
    Seleciona o melhor CLI para um número de destino usando inteligência artificial
    
    - **numero_destino**: Número de telefone de destino
    - **campaña_id**: ID da campanha (opcional)
    - **tipo_numero_preferido**: Tipo de número preferido (opcional)
    - **operadora_preferida**: Operadora preferida (opcional)
    - **excluir_clis**: Lista de CLIs a excluir (opcional)
    """
    try:
        engine = Code2BaseEngine(db)
        resultado = engine.seleccionar_cli_inteligente(request)
        
        logger.info(f"CLI selecionado para {request.numero_destino}: {resultado.cli_seleccionado.numero_normalizado}")
        return resultado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro na seleção de CLI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na seleção de CLI"
        )


@router.post("/analizar-destino", response_model=AnalisisDestinoResponse)
async def analisar_destino(
    request: AnalisisDestinoRequest,
    db: Session = Depends(get_db)
):
    """
    Analisa um número de destino para mostrar informações geográficas e CLIs compatíveis
    
    - **numero_destino**: Número de telefone a analisar
    """
    try:
        service = Code2BaseGeoService(db)
        resultado = service.analisar_destino(request)
        
        logger.info(f"Análise de destino para {request.numero_destino} concluída")
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise de destino: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na análise de destino"
        )


@router.post("/atualizar-resultado-llamada")
async def atualizar_resultado_llamada(
    numero_destino: str,
    cli_numero: str,
    exitosa: bool,
    duracion: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Atualiza o resultado de uma chamada para melhorar as seleções futuras
    
    - **numero_destino**: Número de destino da chamada
    - **cli_numero**: CLI utilizado na chamada
    - **exitosa**: Se a chamada foi exitosa
    - **duracion**: Duração da chamada em segundos (opcional)
    """
    try:
        engine = Code2BaseEngine(db)
        resultado = engine.atualizar_resultado_llamada(
            numero_destino, cli_numero, exitosa, duracion
        )
        
        if resultado:
            return {"message": "Resultado da chamada atualizado com sucesso"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro da chamada não encontrado"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar resultado da chamada: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar resultado"
        )


# ================== GESTÃO DE PAÍSES ==================

@router.post("/paises", response_model=PaisResponse)
async def criar_pais(
    pais: PaisCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo país"""
    service = Code2BaseGeoService(db)
    return service.criar_pais(pais)


@router.get("/paises", response_model=List[PaisResponse])
async def listar_paises(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    apenas_ativos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Lista países com paginação"""
    service = Code2BaseGeoService(db)
    return service.listar_paises(skip, limit, apenas_ativos)


@router.get("/paises/{pais_id}", response_model=PaisResponse)
async def obter_pais(
    pais_id: int,
    db: Session = Depends(get_db)
):
    """Obtém país por ID"""
    service = Code2BaseGeoService(db)
    return service.obter_pais(pais_id)


@router.put("/paises/{pais_id}", response_model=PaisResponse)
async def atualizar_pais(
    pais_id: int,
    pais: PaisUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza país"""
    service = Code2BaseGeoService(db)
    return service.atualizar_pais(pais_id, pais)


# ================== GESTÃO DE ESTADOS ==================

@router.post("/estados", response_model=EstadoResponse)
async def criar_estado(
    estado: EstadoCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo estado"""
    service = Code2BaseGeoService(db)
    return service.criar_estado(estado)


@router.get("/estados", response_model=List[EstadoResponse])
async def listar_estados(
    pais_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista estados, opcionalmente filtrados por país"""
    service = Code2BaseGeoService(db)
    return service.listar_estados(pais_id, skip, limit)


# ================== GESTÃO DE CIDADES ==================

@router.post("/cidades", response_model=CidadeResponse)
async def criar_cidade(
    cidade: CidadeCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova cidade"""
    service = Code2BaseGeoService(db)
    return service.criar_cidade(cidade)


@router.get("/cidades", response_model=List[CidadeResponse])
async def listar_cidades(
    estado_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista cidades, opcionalmente filtradas por estado"""
    service = Code2BaseGeoService(db)
    return service.listar_cidades(estado_id, skip, limit)


# ================== GESTÃO DE PREFIXOS ==================

@router.post("/prefijos", response_model=PrefijoResponse)
async def criar_prefijo(
    prefijo: PrefijoCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo prefixo telefônico"""
    service = Code2BaseGeoService(db)
    return service.criar_prefijo(prefijo)


@router.get("/prefijos", response_model=List[PrefijoResponse])
async def listar_prefijos(
    pais_id: Optional[int] = Query(None),
    estado_id: Optional[int] = Query(None),
    tipo_numero: Optional[TipoNumero] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista prefixos com filtros opcionais"""
    service = Code2BaseGeoService(db)
    return service.listar_prefijos(pais_id, estado_id, tipo_numero, skip, limit)


@router.put("/prefijos/{prefijo_id}", response_model=PrefijoResponse)
async def atualizar_prefijo(
    prefijo_id: int,
    prefijo: PrefijoUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza prefixo"""
    service = Code2BaseGeoService(db)
    return service.atualizar_prefijo(prefijo_id, prefijo)


@router.post("/prefijos/importar", response_model=ImportarPrefijosResponse)
async def importar_prefijos(
    request: ImportarPrefijosRequest,
    db: Session = Depends(get_db)
):
    """
    Importa prefixos de um arquivo CSV
    
    Formato CSV esperado:
    ```
    codigo,pais_codigo,tipo_numero,operadora,estado_codigo,cidade_nome,descripcion,prioridad
    91,ES,fijo,movistar,MD,Madrid,Prefixo Madrid,1
    93,ES,fijo,movistar,CT,Barcelona,Prefixo Barcelona,1
    ```
    """
    service = Code2BaseGeoService(db)
    return service.importar_prefijos_csv(request)


# ================== GESTÃO DE CLIS GEOGRÁFICOS ==================

@router.post("/clis-geo", response_model=CliGeoResponse)
async def criar_cli_geo(
    cli_geo: CliGeoCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo CLI geográfico"""
    service = Code2BaseGeoService(db)
    return service.criar_cli_geo(cli_geo)


@router.get("/clis-geo", response_model=List[CliGeoResponse])
async def listar_clis_geo(
    prefijo_id: Optional[int] = Query(None),
    tipo_numero: Optional[TipoNumero] = Query(None),
    operadora: Optional[TipoOperadora] = Query(None),
    apenas_ativos: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista CLIs geográficos com filtros opcionais"""
    service = Code2BaseGeoService(db)
    return service.listar_clis_geo(prefijo_id, tipo_numero, operadora, apenas_ativos, skip, limit)


@router.post("/clis-geo/sincronizar")
async def sincronizar_clis_existentes(db: Session = Depends(get_db)):
    """
    Sincroniza CLIs existentes com a estrutura geográfica
    
    Este endpoint analisa todos os CLIs existentes e os associa automaticamente
    com os prefixos geográficos correspondentes.
    """
    try:
        service = Code2BaseGeoService(db)
        resultado = service.sincronizar_clis_existentes()
        
        logger.info(f"Sincronização de CLIs concluída: {resultado}")
        return {
            "message": "Sincronização concluída",
            "resultado": resultado
        }
        
    except Exception as e:
        logger.error(f"Erro na sincronização de CLIs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na sincronização"
        )


# ================== GESTÃO DE REGRAS ==================

@router.post("/regras", response_model=ReglaCliResponse)
async def criar_regra(
    regra: ReglaCliCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova regra de seleção de CLI
    
    Exemplo de condições:
    ```json
    {
      "pais": "ES",
      "tipo_numero": "movil",
      "calidad_minima": 0.7,
      "horario": {"inicio": "09:00", "fim": "18:00"}
    }
    ```
    """
    service = Code2BaseRulesService(db)
    return service.criar_regra(regra)


@router.get("/regras", response_model=List[ReglaCliResponse])
async def listar_regras(
    tipo_regra: Optional[TipoRegra] = Query(None),
    apenas_ativas: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista regras com filtros opcionais"""
    service = Code2BaseRulesService(db)
    return service.listar_regras(tipo_regra, apenas_ativas, skip, limit)


@router.get("/regras/{regra_id}", response_model=ReglaCliResponse)
async def obter_regra(
    regra_id: int,
    db: Session = Depends(get_db)
):
    """Obtém regra por ID"""
    service = Code2BaseRulesService(db)
    return service.obter_regra(regra_id)


@router.put("/regras/{regra_id}", response_model=ReglaCliResponse)
async def atualizar_regra(
    regra_id: int,
    regra: ReglaCliUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza regra"""
    service = Code2BaseRulesService(db)
    return service.atualizar_regra(regra_id, regra)


@router.delete("/regras/{regra_id}")
async def remover_regra(
    regra_id: int,
    db: Session = Depends(get_db)
):
    """Remove regra (soft delete)"""
    service = Code2BaseRulesService(db)
    resultado = service.remover_regra(regra_id)
    
    if resultado:
        return {"message": "Regra removida com sucesso"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )


@router.post("/regras/padrao")
async def criar_regras_padrao(db: Session = Depends(get_db)):
    """
    Cria regras padrão do sistema
    
    Este endpoint cria um conjunto de regras pré-configuradas para:
    - Priorizar mesmo prefixo
    - Qualidade mínima para móveis
    - Horário comercial para operadoras específicas
    - Taxa de sucesso mínima
    - Fallback geral
    """
    service = Code2BaseRulesService(db)
    regras_criadas = service.criar_regras_padrao()
    
    return {
        "message": f"{len(regras_criadas)} regras padrão criadas",
        "regras": regras_criadas
    }


# ================== ESTATÍSTICAS E RELATÓRIOS ==================

@router.get("/estatisticas/clis", response_model=EstadisticasCli)
async def obter_estatisticas_cli(db: Session = Depends(get_db)):
    """Obtém estatísticas dos CLIs geográficos"""
    service = Code2BaseGeoService(db)
    return service.obter_estatisticas_cli()


@router.get("/estatisticas/selecciones", response_model=EstadisticasSeleccion)
async def obter_estatisticas_seleccion(db: Session = Depends(get_db)):
    """Obtém estatísticas das seleções de CLI"""
    service = Code2BaseRulesService(db)
    return service.obter_estatisticas_seleccion()


@router.get("/relatorio-sistema", response_model=ReporteSistemaResponse)
async def obter_relatorio_sistema(db: Session = Depends(get_db)):
    """Obtém relatório completo do sistema"""
    geo_service = Code2BaseGeoService(db)
    rules_service = Code2BaseRulesService(db)
    
    return ReporteSistemaResponse(
        estadisticas_cli=geo_service.obter_estatisticas_cli(),
        estadisticas_seleccion=rules_service.obter_estatisticas_seleccion(),
        fecha_reporte=datetime.now()
    )


# ================== CONFIGURAÇÃO DO SISTEMA ==================

@router.get("/configuracion", response_model=ConfiguracionSistemaResponse)
async def obter_configuracion(db: Session = Depends(get_db)):
    """Obtém configuração atual do sistema"""
    service = Code2BaseRulesService(db)
    return service.obter_configuracion()


@router.put("/configuracion", response_model=ConfiguracionSistemaResponse)
async def atualizar_configuracion(
    config: ConfiguracionSistema,
    db: Session = Depends(get_db)
):
    """
    Atualiza configuração do sistema
    
    - **algoritmo_seleccion**: Algoritmo de seleção (weighted_score, highest_score, weighted_random)
    - **peso_geografia**: Peso da geografia na seleção (0.0-1.0)
    - **peso_calidad**: Peso da qualidade na seleção (0.0-1.0)
    - **peso_tasa_exito**: Peso da taxa de sucesso na seleção (0.0-1.0)
    - **peso_uso_reciente**: Peso do uso recente na seleção (0.0-1.0)
    
    Nota: A soma dos pesos deve ser 1.0
    """
    service = Code2BaseRulesService(db)
    return service.atualizar_configuracion(config)


# ================== TESTES E SIMULAÇÕES ==================

@router.post("/testar-sistema", response_model=TesteSistemaResponse)
async def testar_sistema(
    request: TesteSistemaRequest,
    db: Session = Depends(get_db)
):
    """
    Testa o sistema com múltiplas simulações
    
    Este endpoint executa várias seleções para o mesmo número de destino
    para analisar a consistência e distribuição das seleções.
    
    - **numero_destino**: Número para testar
    - **campaña_id**: ID da campanha (opcional)
    - **simulaciones**: Número de simulações (1-100)
    """
    try:
        service = Code2BaseRulesService(db)
        resultado = service.testar_sistema(request)
        
        logger.info(f"Teste do sistema para {request.numero_destino} concluído com {resultado.total_simulaciones} simulações")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro no teste do sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no teste do sistema"
        )


# ================== UTILITÁRIOS ==================

@router.get("/status")
async def status_sistema(db: Session = Depends(get_db)):
    """
    Verifica o status do sistema CODE2BASE
    
    Retorna informações sobre:
    - Total de países, estados e cidades cadastrados
    - Total de prefixos ativos
    - Total de CLIs geográficos
    - Total de regras ativas
    - Últimas seleções realizadas
    """
    try:
        geo_service = Code2BaseGeoService(db)
        rules_service = Code2BaseRulesService(db)
        
        # Estatísticas básicas
        estatisticas_cli = geo_service.obter_estatisticas_cli()
        
        # Contagem de registros geográficos
        from app.models.code2base import Pais, Estado, Cidade, Prefijo, ReglaCli
        
        total_paises = db.query(Pais).filter(Pais.activo == True).count()
        total_estados = db.query(Estado).filter(Estado.activo == True).count()
        total_cidades = db.query(Cidade).filter(Cidade.activo == True).count()
        total_prefijos = db.query(Prefijo).filter(Prefijo.activo == True).count()
        total_regras = db.query(ReglaCli).filter(ReglaCli.activo == True).count()
        
        return {
            "status": "ativo",
            "sistema": "CODE2BASE Avançado",
            "version": "1.0.0",
            "geografia": {
                "paises": total_paises,
                "estados": total_estados,
                "cidades": total_cidades,
                "prefijos": total_prefijos
            },
            "clis": {
                "total": estatisticas_cli.total_clis,
                "ativos": estatisticas_cli.clis_ativos,
                "tasa_exito_promedio": estatisticas_cli.tasa_exito_promedio
            },
            "regras": {
                "total": total_regras
            },
            "message": "Sistema CODE2BASE funcionando corretamente"
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar status do sistema: {e}")
        return {
            "status": "erro",
            "message": f"Erro ao verificar status: {str(e)}"
        }


@router.get("/setup")
async def setup_inicial(db: Session = Depends(get_db)):
    """
    Executa setup inicial do sistema CODE2BASE
    
    Este endpoint:
    1. Cria o país Espanha se não existir
    2. Cria alguns estados e prefixos básicos
    3. Cria regras padrão
    4. Sincroniza CLIs existentes
    """
    try:
        geo_service = Code2BaseGeoService(db)
        rules_service = Code2BaseRulesService(db)
        
        resultados = []
        
        # 1. Criar país Espanha
        try:
            from app.schemas.code2base import PaisCreate
            pais_es = PaisCreate(
                codigo="ES",
                nome="España",
                codigo_telefone="+34",
                activo=True
            )
            espanha = geo_service.criar_pais(pais_es)
            resultados.append(f"País {espanha.nome} criado")
        except HTTPException as e:
            if "já existe" in str(e.detail):
                resultados.append("País Espanha já existe")
            else:
                resultados.append(f"Erro ao criar país: {e.detail}")
        
        # 2. Criar regras padrão
        regras_criadas = rules_service.criar_regras_padrao()
        if regras_criadas:
            resultados.append(f"{len(regras_criadas)} regras padrão criadas")
        else:
            resultados.append("Regras padrão já existem")
        
        # 3. Sincronizar CLIs existentes
        try:
            sincronizacao = geo_service.sincronizar_clis_existentes()
            resultados.append(f"Sincronização: {sincronizacao['clis_sincronizados']} CLIs processados")
        except Exception as e:
            resultados.append(f"Erro na sincronização: {str(e)}")
        
        return {
            "message": "Setup inicial concluído",
            "resultados": resultados
        }
        
    except Exception as e:
        logger.error(f"Erro no setup inicial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no setup inicial"
        )
