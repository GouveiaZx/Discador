import React, { useEffect, useState } from 'react';

const API_URL = '/api/monitoring/call_history';

function CallHistory() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCalls = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setCalls(data);
    } catch (err) {
      setError('Error al cargar historial de llamadas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCalls();
  }, []);

  return (
    <div className="p-4 bg-white rounded shadow mt-8">
      <h2 className="text-xl font-bold mb-4">Histórico de Chamadas</h2>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      {loading ? <div>Carregando...</div> : (
        <table className="w-full border">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nome</th>
              <th>Ramal</th>
              <th>Trunk</th>
              <th>Duração</th>
              <th>Status</th>
              <th>Campanha</th>
              <th>Agente</th>
              <th>Início</th>
              <th>Fim</th>
            </tr>
          </thead>
          <tbody>
            {calls.map(call => (
              <tr key={call.id}>
                <td>{call.phone_number}</td>
                <td>{call.name}</td>
                <td>{call.extension}</td>
                <td>{call.trunk}</td>
                <td>{call.duration}</td>
                <td>{call.status}</td>
                <td>{call.campaign}</td>
                <td>{call.agent}</td>
                <td>{call.start_time}</td>
                <td>{call.end_time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default CallHistory; 