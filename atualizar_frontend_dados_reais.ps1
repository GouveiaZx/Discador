# ================================
# ATUALIZAR FRONTEND PARA DADOS REAIS
# PowerShell para Windows  
# ================================

Write-Host "🎨 ATUALIZANDO FRONTEND PARA DADOS REAIS" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Yellow

# Verificar se está na pasta correta
if (!(Test-Path "main.py")) {
    Write-Host "❌ Execute este script na pasta do projeto (onde está o main.py)" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pasta do projeto detectada" -ForegroundColor Green

# Verificar se pasta frontend existe
if (!(Test-Path "frontend")) {
    Write-Host "⚠️ Pasta frontend não encontrada. Criando estrutura..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "frontend" -Force | Out-Null
    New-Item -ItemType Directory -Path "frontend/src" -Force | Out-Null
    New-Item -ItemType Directory -Path "frontend/src/components" -Force | Out-Null
    New-Item -ItemType Directory -Path "frontend/src/services" -Force | Out-Null
}

Write-Host "`n📋 ETAPA 1: CRIANDO SERVIÇO DE API REAL" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Yellow

# Criar serviço de API para dados reais
$apiServiceContent = @"
// ================================
// SERVIÇO DE API PARA DADOS REAIS
// ================================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://web-production-c192b.up.railway.app';

class DiscadorApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${"${this.baseUrl}${endpoint}"}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${"${response.status}"}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Error for ${"${endpoint}"}:`, error);
            throw error;
        }
    }

    // ===========================
    // ENDPOINTS DO DISCADOR REAL
    // ===========================

    async getDashboardRealStats() {
        return this.request('/api/v1/dashboard/real-stats');
    }

    async getCampaignStats() {
        return this.request('/api/v1/campaigns/stats');
    }

    async getActiveCalls() {
        return this.request('/api/v1/campaigns/active-calls');
    }

    async getDiscadorStatus() {
        return this.request('/api/v1/discador/status');
    }

    async startCampaign(campaignId) {
        return this.request(`/api/v1/campaigns/${"${campaignId}"}/start`, {
            method: 'POST'
        });
    }

    async stopCampaign(campaignId) {
        return this.request(`/api/v1/campaigns/${"${campaignId}"}/stop`, {
            method: 'POST'
        });
    }

    // ===========================
    // ENDPOINTS EXISTENTES
    // ===========================

    async getCampaigns() {
        return this.request('/api/v1/campaigns');
    }

    async getCallHistory() {
        return this.request('/api/v1/llamadas/historico');
    }

    async getActiveCallsCompat() {
        return this.request('/api/v1/llamadas/en-progreso');
    }
}

export default new DiscadorApiService();
"@

$apiServiceContent | Out-File -FilePath "frontend/src/services/discadorApi.js" -Encoding UTF8
Write-Host "✅ Arquivo criado: frontend/src/services/discadorApi.js" -ForegroundColor Green

Write-Host "`n📊 ETAPA 2: COMPONENTE DE DASHBOARD REAL" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Yellow

# Criar componente de dashboard com dados reais
$dashboardRealContent = @"
// ================================
// DASHBOARD COM DADOS REAIS
// ================================

import React, { useState, useEffect } from 'react';
import discadorApi from '../services/discadorApi';

const DashboardReal = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeCalls, setActiveCalls] = useState([]);
    const [discadorStatus, setDiscadorStatus] = useState(null);

    useEffect(() => {
        loadDashboardData();
        
        // Atualizar dados a cada 5 segundos
        const interval = setInterval(loadDashboardData, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            
            // Carregar dados em paralelo
            const [dashboardData, campaignStats, activeCallsData, statusData] = await Promise.all([
                discadorApi.getDashboardRealStats(),
                discadorApi.getCampaignStats(),
                discadorApi.getActiveCalls(),
                discadorApi.getDiscadorStatus()
            ]);

            setStats(dashboardData.data);
            setActiveCalls(activeCallsData.data || []);
            setDiscadorStatus(statusData.data);
            setError(null);
            
        } catch (err) {
            console.error('Erro ao carregar dados:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleStartCampaign = async () => {
        try {
            await discadorApi.startCampaign(1); // Campaign ID padrão
            loadDashboardData();
        } catch (err) {
            alert(`Erro ao iniciar campanha: ${"${err.message}"}`);
        }
    };

    const handleStopCampaign = async () => {
        try {
            await discadorApi.stopCampaign(1);
            loadDashboardData();
        } catch (err) {
            alert(`Erro ao parar campanha: ${"${err.message}"}`);
        }
    };

    if (loading && !stats) {
        return (
            <div className="dashboard-loading">
                <div className="loading-spinner"></div>
                <p>Carregando dados reais...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="dashboard-error">
                <h3>❌ Erro ao carregar dados</h3>
                <p>{error}</p>
                <button onClick={loadDashboardData}>Tentar Novamente</button>
            </div>
        );
    }

    return (
        <div className="dashboard-real">
            <div className="dashboard-header">
                <h2>📊 Dashboard - Dados Reais</h2>
                <div className="dashboard-controls">
                    {discadorStatus?.discador_active ? (
                        <button 
                            className="btn btn-danger"
                            onClick={handleStopCampaign}
                        >
                            🛑 Parar Discador
                        </button>
                    ) : (
                        <button 
                            className="btn btn-success"
                            onClick={handleStartCampaign}
                        >
                            🚀 Iniciar Discador
                        </button>
                    )}
                </div>
            </div>

            {/* KPIs Principais */}
            <div className="kpis-grid">
                <div className="kpi-card">
                    <h3>📞 Chamadas Ativas</h3>
                    <div className="kpi-value">{stats?.kpis?.active_calls || 0}</div>
                </div>
                <div className="kpi-card">
                    <h3>📈 Chamadas Hoje</h3>
                    <div className="kpi-value">{stats?.kpis?.calls_today || 0}</div>
                </div>
                <div className="kpi-card">
                    <h3>🎯 Taxa de Sucesso</h3>
                    <div className="kpi-value">{stats?.kpis?.effectiveness || 0}%</div>
                </div>
                <div className="kpi-card">
                    <h3>🏃 Campanhas Ativas</h3>
                    <div className="kpi-value">{stats?.kpis?.active_campaigns || 0}</div>
                </div>
            </div>

            {/* Status do Sistema */}
            <div className="system-status">
                <h3>🔧 Status do Sistema</h3>
                <div className="status-grid">
                    <div className={`status-item ${"${stats?.system_status?.discador_running ? 'status-ok' : 'status-warning'}"}`}>
                        <span>Discador:</span>
                        <span>{stats?.system_status?.discador_running ? '🟢 Ativo' : '🟡 Parado'}</span>
                    </div>
                    <div className={`status-item ${"${stats?.system_status?.database_connected ? 'status-ok' : 'status-error'}"}`}>
                        <span>Database:</span>
                        <span>{stats?.system_status?.database_connected ? '🟢 Conectado' : '🔴 Erro'}</span>
                    </div>
                    <div className={`status-item ${"${stats?.system_status?.api_responsive ? 'status-ok' : 'status-error'}"}`}>
                        <span>API:</span>
                        <span>{stats?.system_status?.api_responsive ? '🟢 Responsiva' : '🔴 Erro'}</span>
                    </div>
                </div>
            </div>

            {/* Chamadas Ativas */}
            <div className="active-calls-section">
                <h3>📞 Chamadas em Progresso ({activeCalls.length})</h3>
                {activeCalls.length > 0 ? (
                    <div className="calls-list">
                        {activeCalls.map((call, index) => (
                            <div key={index} className="call-item">
                                <span className="call-phone">{call.phone_number}</span>
                                <span className="call-duration">{call.duration}s</span>
                                <span className="call-status">🔄 Em progresso</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p>Nenhuma chamada ativa no momento</p>
                )}
            </div>

            {/* Gráfico de Estados das Chamadas */}
            {stats?.call_states && (
                <div className="call-states-chart">
                    <h3>📊 Estados das Chamadas</h3>
                    <div className="states-grid">
                        <div className="state-item">
                            <span>✅ Conectadas:</span>
                            <span>{stats.call_states.conectadas}</span>
                        </div>
                        <div className="state-item">
                            <span>📵 Sem Resposta:</span>
                            <span>{stats.call_states.sem_resposta}</span>
                        </div>
                        <div className="state-item">
                            <span>📞 Transferidas:</span>
                            <span>{stats.call_states.transferidas}</span>
                        </div>
                        <div className="state-item">
                            <span>📵 Ocupado:</span>
                            <span>{stats.call_states.ocupado}</span>
                        </div>
                    </div>
                </div>
            )}

            <div className="dashboard-footer">
                <p>🕒 Última atualização: {new Date().toLocaleTimeString()}</p>
                <p>🔄 Atualização automática a cada 5 segundos</p>
            </div>
        </div>
    );
};

export default DashboardReal;
"@

$dashboardRealContent | Out-File -FilePath "frontend/src/components/DashboardReal.jsx" -Encoding UTF8
Write-Host "✅ Arquivo criado: frontend/src/components/DashboardReal.jsx" -ForegroundColor Green

Write-Host "`n🎨 ETAPA 3: ESTILOS CSS PARA DADOS REAIS" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Yellow

# Criar CSS para o dashboard real
$cssContent = @"
/* ================================
   ESTILOS DASHBOARD DADOS REAIS
   ================================ */

.dashboard-real {
    padding: 20px;
    background: #f5f5f5;
    min-height: 100vh;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.dashboard-controls .btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-success {
    background: #28a745;
    color: white;
}

.btn-success:hover {
    background: #218838;
    transform: translateY(-2px);
}

.btn-danger {
    background: #dc3545;
    color: white;
}

.btn-danger:hover {
    background: #c82333;
    transform: translateY(-2px);
}

.kpis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.kpi-card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.kpi-card:hover {
    transform: translateY(-5px);
}

.kpi-card h3 {
    margin: 0 0 15px 0;
    color: #666;
    font-size: 16px;
}

.kpi-value {
    font-size: 2.5em;
    font-weight: bold;
    color: #333;
    margin: 10px 0;
}

.system-status {
    background: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.status-item {
    display: flex;
    justify-content: space-between;
    padding: 15px;
    border-radius: 8px;
    font-weight: bold;
}

.status-ok {
    background: #d4edda;
    color: #155724;
}

.status-warning {
    background: #fff3cd;
    color: #856404;
}

.status-error {
    background: #f8d7da;
    color: #721c24;
}

.active-calls-section {
    background: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.calls-list {
    max-height: 300px;
    overflow-y: auto;
}

.call-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid #eee;
    transition: background 0.3s ease;
}

.call-item:hover {
    background: #f8f9fa;
}

.call-phone {
    font-weight: bold;
    color: #007bff;
}

.call-duration {
    color: #666;
    font-family: monospace;
}

.call-status {
    color: #28a745;
}

.call-states-chart {
    background: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.states-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.state-item {
    display: flex;
    justify-content: space-between;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #007bff;
}

.dashboard-footer {
    text-align: center;
    color: #666;
    margin-top: 30px;
    padding: 20px;
    background: white;
    border-radius: 10px;
}

.dashboard-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.dashboard-error {
    text-align: center;
    padding: 50px;
    background: white;
    border-radius: 15px;
    margin: 20px;
}

.dashboard-error h3 {
    color: #dc3545;
    margin-bottom: 15px;
}

.dashboard-error button {
    padding: 12px 24px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-top: 15px;
}

/* Responsivo para mobile */
@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
        gap: 15px;
    }
    
    .kpis-grid {
        grid-template-columns: 1fr;
    }
    
    .status-grid,
    .states-grid {
        grid-template-columns: 1fr;
    }
    
    .call-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
}
"@

$cssContent | Out-File -FilePath "frontend/src/components/DashboardReal.css" -Encoding UTF8
Write-Host "✅ Arquivo criado: frontend/src/components/DashboardReal.css" -ForegroundColor Green

Write-Host "`n📱 ETAPA 4: COMPONENTE DE CONTROLE DE CAMPANHAS" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Yellow

# Criar componente de controle de campanhas
$campaignControlContent = @"
// ================================
// CONTROLE DE CAMPANHAS REAL
// ================================

import React, { useState, useEffect } from 'react';
import discadorApi from '../services/discadorApi';

const CampaignControl = () => {
    const [campaigns, setCampaigns] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadCampaigns();
        loadStats();
        
        // Atualizar stats a cada 3 segundos
        const interval = setInterval(loadStats, 3000);
        return () => clearInterval(interval);
    }, []);

    const loadCampaigns = async () => {
        try {
            const response = await discadorApi.getCampaigns();
            setCampaigns(response.campaigns || []);
        } catch (error) {
            console.error('Erro ao carregar campanhas:', error);
        }
    };

    const loadStats = async () => {
        try {
            const response = await discadorApi.getCampaignStats();
            setStats(response.data);
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    };

    const handleStartCampaign = async (campaignId) => {
        setLoading(true);
        try {
            await discadorApi.startCampaign(campaignId);
            alert('Campanha iniciada com sucesso!');
            loadStats();
        } catch (error) {
            alert(`Erro ao iniciar campanha: ${"${error.message}"}`);
        } finally {
            setLoading(false);
        }
    };

    const handleStopCampaign = async (campaignId) => {
        setLoading(true);
        try {
            await discadorApi.stopCampaign(campaignId);
            alert('Campanha parada com sucesso!');
            loadStats();
        } catch (error) {
            alert(`Erro ao parar campanha: ${"${error.message}"}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="campaign-control">
            <div className="control-header">
                <h2>🎯 Controle de Campanhas</h2>
                {stats && (
                    <div className="quick-stats">
                        <span>📞 Total: {stats.total_calls}</span>
                        <span>✅ Sucessos: {stats.successful_calls}</span>
                        <span>📈 Taxa: {stats.success_rate}%</span>
                        <span className={stats.is_running ? 'status-running' : 'status-stopped'}>
                            {stats.is_running ? '🟢 Rodando' : '🔴 Parado'}
                        </span>
                    </div>
                )}
            </div>

            <div className="campaigns-grid">
                {campaigns.length > 0 ? (
                    campaigns.map(campaign => (
                        <div key={campaign.id} className="campaign-card">
                            <div className="campaign-info">
                                <h3>{campaign.name}</h3>
                                <p>{campaign.description}</p>
                                <div className="campaign-stats">
                                    <span>📊 {campaign.total_contacts || 0} contatos</span>
                                    <span>✅ {campaign.success_count || 0} sucessos</span>
                                </div>
                            </div>
                            <div className="campaign-controls">
                                <button
                                    className="btn btn-start"
                                    onClick={() => handleStartCampaign(campaign.id)}
                                    disabled={loading || (stats && stats.is_running)}
                                >
                                    🚀 Iniciar
                                </button>
                                <button
                                    className="btn btn-stop"
                                    onClick={() => handleStopCampaign(campaign.id)}
                                    disabled={loading || (stats && !stats.is_running)}
                                >
                                    🛑 Parar
                                </button>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="no-campaigns">
                        <p>📭 Nenhuma campanha encontrada</p>
                        <button className="btn btn-primary">➕ Criar Campanha</button>
                    </div>
                )}
            </div>

            {stats && (
                <div className="detailed-stats">
                    <h3>📊 Estatísticas Detalhadas</h3>
                    <div className="stats-grid">
                        <div className="stat-item">
                            <span>Total de Chamadas:</span>
                            <span>{stats.total_calls}</span>
                        </div>
                        <div className="stat-item">
                            <span>Chamadas com Sucesso:</span>
                            <span>{stats.successful_calls}</span>
                        </div>
                        <div className="stat-item">
                            <span>Pressionaram 1:</span>
                            <span>{stats.pressed_1_calls}</span>
                        </div>
                        <div className="stat-item">
                            <span>Sem Resposta:</span>
                            <span>{stats.no_answer_calls}</span>
                        </div>
                        <div className="stat-item">
                            <span>Linha Ocupada:</span>
                            <span>{stats.busy_calls}</span>
                        </div>
                        <div className="stat-item">
                            <span>Taxa de Sucesso:</span>
                            <span>{stats.success_rate}%</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CampaignControl;
"@

$campaignControlContent | Out-File -FilePath "frontend/src/components/CampaignControl.jsx" -Encoding UTF8
Write-Host "✅ Arquivo criado: frontend/src/components/CampaignControl.jsx" -ForegroundColor Green

Write-Host "`n🎉 CONFIGURAÇÃO DO FRONTEND CONCLUÍDA!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

Write-Host @"
📋 ARQUIVOS CRIADOS:
✅ frontend/src/services/discadorApi.js (Serviço de API)
✅ frontend/src/components/DashboardReal.jsx (Dashboard com dados reais)
✅ frontend/src/components/DashboardReal.css (Estilos modernos)
✅ frontend/src/components/CampaignControl.jsx (Controle de campanhas)

🚀 FUNCIONALIDADES IMPLEMENTADAS:
✅ Dashboard com dados reais do discador
✅ Controles para iniciar/parar campanhas
✅ Monitoramento de chamadas ativas
✅ Estatísticas em tempo real
✅ Status do sistema
✅ Interface responsiva

📱 PRÓXIMOS PASSOS:
1. Integre os novos componentes no seu App.js principal
2. Importe os estilos CSS
3. Configure as variáveis de ambiente
4. Teste a integração com a API real

💡 EXEMPLO DE INTEGRAÇÃO NO APP.JS:
import DashboardReal from './components/DashboardReal';
import CampaignControl from './components/CampaignControl';
import './components/DashboardReal.css';

🎯 RESULTADO: FRONTEND INTEGRADO COM DADOS REAIS!
"@ -ForegroundColor White

Write-Host "`nPressione ENTER para continuar..." -ForegroundColor Yellow
Read-Host 