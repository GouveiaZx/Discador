"""
APIs REST para o Sistema CODE2BASE Avancado
Endpoints para selecao inteligente de CLIs baseada em geografia e regras
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.code2base_engine import Code2BaseEngine
from app.services.code2base_geo_service import Code2BaseGeoService
from app.services.code2base_rules_service import Code2BaseRulesService
from app.schemas.code2base import (
    # Enums
    TipoOperadoraEnum, TipoReglaEnum, TipoNumeroEnum,
    # Esquemas de paises
    PaisCreate, PaisUpdate, PaisResponse,
    # Esquemas de estados
    EstadoCreate, EstadoUpdate, EstadoResponse,
    # Esquemas de cidades
    CidadeCreate, CidadeUpdate, CidadeResponse,
    # Esquemas de prefixos
    PrefijoCreate, PrefijoUpdate, PrefijoResponse,
    # Esquemas de CLIs geograficos
    CliGeoCreate, CliGeoUpdate, CliGeoResponse,
    # Esquemas de regras
    ReglaCliCreate, ReglaCliUpdate, ReglaCliResponse,
    # Esquemas de selecao
    SeleccionCliRequest, SeleccionCliResponse,
    # Esquemas de analise
    AnalisisDestinoRequest, AnalisisDestinoResponse,
    # Esquemas de importacao
    ImportarPrefijosRequest, ImportarPrefijosResponse,
    # Esquemas de estatisticas
    EstadisticasCli, EstadisticasSeleccion, ReporteSistemaResponse,
    # Esquemas de configuracao
    ConfiguracionSistema, ConfiguracionSistemaResponse,
    # Esquemas de teste
    TesteSistemaRequest, TesteSistemaResponse
)
from app.utils.logger import logger

router = APIRouter(prefix="/code2base", tags=["CODE2BASE - Sistema CLI Inteligente"])


# ================== SELECAO INTELIGENTE DE CLI ==================

@router.post("/seleccionar-cli", response_model=SeleccionCliResponse)
async def seleccionar_cli_inteligente(
    request: SeleccionCliRequest,
    db: Session = Depends(get_db)
):
    """
    Seleciona o melhor CLI para um numero de destino usando inteligencia artificial
    
    - **numero_destino**: Numero de telefone de destino
    - **campana_id**: ID da campanha (opcional)
    - **tipo_numero_preferido**: Tipo de numero preferido (opcional)
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
        logger.error(f"Erro na selecao de CLI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na selecao de CLI"
        )


@router.post("/analizar-destino", response_model=AnalisisDestinoResponse)
async def analisar_destino(
    request: AnalisisDestinoRequest,
    db: Session = Depends(get_db)
):
    """
    Analisa um numero de destino para mostrar informacoes geograficas e CLIs compativeis
    
    - **numero_destino**: Numero de telefone a analisar
    """
    try:
        service = Code2BaseGeoService(db)
        resultado = service.analisar_destino(request)
        
        logger.info(f"Analise de destino para {request.numero_destino} concluida")
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na analise de destino: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na analise de destino"
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
    Atualiza o resultado de uma chamada para melhorar as selecoes futuras
    
    - **numero_destino**: Numero de destino da chamada
    - **cli_numero**: CLI utilizado na chamada
    - **exitosa**: Se a chamada foi exitosa
    - **duracion**: Duracao da chamada em segundos (opcional)
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
                detail="Registro da chamada nao encontrado"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar resultado da chamada: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar resultado"
        )


# ================== GESTAO DE PAISES ==================

@router.post("/paises", response_model=PaisResponse)
async def criar_pais(
    pais: PaisCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo pais"""
    service = Code2BaseGeoService(db)
    return service.criar_pais(pais)


@router.get("/paises", response_model=List[PaisResponse])
async def listar_paises(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    apenas_ativos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Lista paises com paginacao"""
    service = Code2BaseGeoService(db)
    return service.listar_paises(skip, limit, apenas_ativos)


@router.get("/paises/{pais_id}", response_model=PaisResponse)
async def obter_pais(
    pais_id: int,
    db: Session = Depends(get_db)
):
    """Obtem pais por ID"""
    service = Code2BaseGeoService(db)
    return service.obter_pais(pais_id)


@router.put("/paises/{pais_id}", response_model=PaisResponse)
async def atualizar_pais(
    pais_id: int,
    pais: PaisUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza pais"""
    service = Code2BaseGeoService(db)
    return service.atualizar_pais(pais_id, pais)


# ================== GESTAO DE ESTADOS ==================

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
    """Lista estados, opcionalmente filtrados por pais"""
    service = Code2BaseGeoService(db)
    return service.listar_estados(pais_id, skip, limit)


# ================== GESTAO DE CIDADES ==================

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


# ================== GESTAO DE PREFIXOS ==================

@router.post("/prefijos", response_model=PrefijoResponse)
async def criar_prefijo(
    prefijo: PrefijoCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo prefixo telefonico"""
    service = Code2BaseGeoService(db)
    return service.criar_prefijo(prefijo)


@router.get("/prefijos", response_model=List[PrefijoResponse])
async def listar_prefijos(
    pais_id: Optional[int] = Query(None),
    estado_id: Optional[int] = Query(None),
    tipo_numero: Optional[TipoNumeroEnum] = Query(None),
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


# ================== GESTAO DE CLIS GEOGRAFICOS ==================

@router.post("/clis-geo", response_model=CliGeoResponse)
async def criar_cli_geo(
    cli_geo: CliGeoCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo CLI geografico"""
    service = Code2BaseGeoService(db)
    return service.criar_cli_geo(cli_geo)


@router.get("/clis-geo", response_model=List[CliGeoResponse])
async def listar_clis_geo(
    prefijo_id: Optional[int] = Query(None),
    tipo_numero: Optional[TipoNumeroEnum] = Query(None),
    operadora: Optional[TipoOperadoraEnum] = Query(None),
    apenas_ativos: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lista CLIs geograficos com filtros opcionais"""
    service = Code2BaseGeoService(db)
    return service.listar_clis_geo(prefijo_id, tipo_numero, operadora, apenas_ativos, skip, limit)


@router.post("/clis-geo/sincronizar")
async def sincronizar_clis_existentes(db: Session = Depends(get_db)):
    """
    Sincroniza CLIs existentes com a estrutura geografica
    
    Este endpoint analisa todos os CLIs existentes e os associa automaticamente
    com os prefixos geograficos correspondentes.
    """
    try:
        service = Code2BaseGeoService(db)
        resultado = service.sincronizar_clis_existentes()
        
        logger.info(f"Sincronizacao de CLIs concluida: {resultado}")
        return {
            "message": "Sincronizacao concluida",
            "resultado": resultado
        }
        
    except Exception as e:
        logger.error(f"Erro na sincronizacao de CLIs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno na sincronizacao"
        )


# ================== GESTAO DE REGRAS ==================

@router.post("/regras", response_model=ReglaCliResponse)
async def criar_regra(
    regra: ReglaCliCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova regra de selecao de CLI
    
    Exemplo de condicoes:
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
    tipo_regra: Optional[TipoReglaEnum] = Query(None),
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
    """Obtem regra por ID"""
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
            detail="Regra nao encontrada"
        )


@router.post("/regras/padrao")
async def criar_regras_padrao(db: Session = Depends(get_db)):
    """
    Cria regras padrao do sistema
    
    Este endpoint cria um conjunto de regras pre-configuradas para:
    - Priorizar mesmo prefixo
    - Qualidade minima para moveis
    - Horario comercial para operadoras especificas
    - Taxa de sucesso minima
    - Fallback geral
    """
    service = Code2BaseRulesService(db)
    regras_criadas = service.criar_regras_padrao()
    
    return {
        "message": f"{len(regras_criadas)} regras padrao criadas",
        "regras": regras_criadas
    }


# ================== ESTATISTICAS E RELATORIOS ==================

@router.get("/estatisticas/clis", response_model=EstadisticasCli)
async def obter_estatisticas_cli(db: Session = Depends(get_db)):
    """Obtem estatisticas dos CLIs geograficos"""
    service = Code2BaseGeoService(db)
    return service.obter_estatisticas_cli()


@router.get("/estatisticas/selecciones", response_model=EstadisticasSeleccion)
async def obter_estatisticas_seleccion(db: Session = Depends(get_db)):
    """Obtem estatisticas das selecoes de CLI"""
    service = Code2BaseRulesService(db)
    return service.obter_estatisticas_seleccion()


@router.get("/relatorio-sistema", response_model=ReporteSistemaResponse)
async def obter_relatorio_sistema(db: Session = Depends(get_db)):
    """Obtem relatorio completo do sistema"""
    geo_service = Code2BaseGeoService(db)
    rules_service = Code2BaseRulesService(db)
    
    return ReporteSistemaResponse(
        estadisticas_cli=geo_service.obter_estatisticas_cli(),
        estadisticas_seleccion=rules_service.obter_estatisticas_seleccion(),
        fecha_reporte=datetime.now()
    )


# ================== CONFIGURACAO DO SISTEMA ==================

@router.get("/configuracion", response_model=ConfiguracionSistemaResponse)
async def obter_configuracion(db: Session = Depends(get_db)):
    """Obtem configuracao atual do sistema"""
    service = Code2BaseRulesService(db)
    return service.obter_configuracion()


@router.put("/configuracion", response_model=ConfiguracionSistemaResponse)
async def atualizar_configuracion(
    config: ConfiguracionSistema,
    db: Session = Depends(get_db)
):
    """
    Atualiza configuracao do sistema
    
    - **algoritmo_seleccion**: Algoritmo de selecao (weighted_score, highest_score, weighted_random)
    - **peso_geografia**: Peso da geografia na selecao (0.0-1.0)
    - **peso_calidad**: Peso da qualidade na selecao (0.0-1.0)
    - **peso_tasa_exito**: Peso da taxa de sucesso na selecao (0.0-1.0)
    - **peso_uso_reciente**: Peso do uso recente na selecao (0.0-1.0)
    
    Nota: A soma dos pesos deve ser 1.0
    """
    service = Code2BaseRulesService(db)
    return service.atualizar_configuracion(config)


# ================== TESTES E SIMULACOES ==================

@router.post("/testar-sistema", response_model=TesteSistemaResponse)
async def testar_sistema(
    request: TesteSistemaRequest,
    db: Session = Depends(get_db)
):
    """
    Testa o sistema com multiplas simulacoes
    
    Este endpoint executa varias selecoes para o mesmo numero de destino
    para analisar a consistencia e distribuicao das selecoes.
    
    - **numero_destino**: Numero para testar
    - **campana_id**: ID da campanha (opcional)
    - **simulaciones**: Numero de simulacoes (1-100)
    """
    try:
        service = Code2BaseRulesService(db)
        resultado = service.testar_sistema(request)
        
        logger.info(f"Teste do sistema para {request.numero_destino} concluido com {resultado.total_simulaciones} simulacoes")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro no teste do sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no teste do sistema"
        )


# ================== UTILITARIOS ==================

@router.get("/status")
async def status_sistema(db: Session = Depends(get_db)):
    """
    Verifica o status do sistema CODE2BASE
    
    Retorna informacoes sobre:
    - Total de paises, estados e cidades cadastrados
    - Total de prefixos ativos
    - Total de CLIs geograficos
    - Total de regras ativas
    - Ultimas selecoes realizadas
    """
    try:
        geo_service = Code2BaseGeoService(db)
        rules_service = Code2BaseRulesService(db)
        
        # Estatisticas basicas
        estatisticas_cli = geo_service.obter_estatisticas_cli()
        
        # Contagem de registros geograficos
        from app.models.code2base import Pais, Estado, Cidade, Prefijo, ReglaCli
        
        total_paises = db.query(Pais).filter(Pais.activo == True).count()
        total_estados = db.query(Estado).filter(Estado.activo == True).count()
        total_cidades = db.query(Cidade).filter(Cidade.activo == True).count()
        total_prefijos = db.query(Prefijo).filter(Prefijo.activo == True).count()
        total_regras = db.query(ReglaCli).filter(ReglaCli.activo == True).count()
        
        return {
            "status": "ativo",
            "sistema": "CODE2BASE Avancado",
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
    1. Cria o pais Espanha se nao existir
    2. Cria alguns estados e prefixos basicos
    3. Cria regras padrao
    4. Sincroniza CLIs existentes
    """
    try:
        geo_service = Code2BaseGeoService(db)
        rules_service = Code2BaseRulesService(db)
        
        resultados = []
        
        # 1. Criar pais Espanha
        try:
            from app.schemas.code2base import PaisCreate
            pais_es = PaisCreate(
                codigo="ES",
                nome="Espana",
                codigo_telefone="+34",
                activo=True
            )
            espanha = geo_service.criar_pais(pais_es)
            resultados.append(f"Pais {espanha.nome} criado")
        except HTTPException as e:
            if "ja existe" in str(e.detail):
                resultados.append("Pais Espanha ja existe")
            else:
                resultados.append(f"Erro ao criar pais: {e.detail}")
        
        # 2. Criar regras padrao
        regras_criadas = rules_service.criar_regras_padrao()
        if regras_criadas:
            resultados.append(f"{len(regras_criadas)} regras padrao criadas")
        else:
            resultados.append("Regras padrao ja existem")
        
        # 3. Sincronizar CLIs existentes
        try:
            sincronizacao = geo_service.sincronizar_clis_existentes()
            resultados.append(f"Sincronizacao: {sincronizacao['clis_sincronizados']} CLIs processados")
        except Exception as e:
            resultados.append(f"Erro na sincronizacao: {str(e)}")
        
        return {
            "message": "Setup inicial concluido",
            "resultados": resultados
        }
        
    except Exception as e:
        logger.error(f"Erro no setup inicial: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no setup inicial"
        )
