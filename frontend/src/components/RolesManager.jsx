import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const RolesManager = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permissions: [],
    active: true
  });

  const availablePermissions = [
    { id: 'campaigns_view', name: 'Visualizar Campanhas', category: 'Campanhas' },
    { id: 'campaigns_create', name: 'Criar Campanhas', category: 'Campanhas' },
    { id: 'campaigns_edit', name: 'Editar Campanhas', category: 'Campanhas' },
    { id: 'campaigns_delete', name: 'Deletar Campanhas', category: 'Campanhas' },
    { id: 'campaigns_start', name: 'Iniciar Campanhas', category: 'Campanhas' },
    { id: 'calls_view', name: 'Visualizar Chamadas', category: 'Chamadas' },
    { id: 'calls_manage', name: 'Gerenciar Chamadas', category: 'Chamadas' },
    { id: 'calls_reports', name: 'Relatórios de Chamadas', category: 'Chamadas' },
    { id: 'lists_view', name: 'Visualizar Listas', category: 'Listas' },
    { id: 'lists_create', name: 'Criar Listas', category: 'Listas' },
    { id: 'lists_edit', name: 'Editar Listas', category: 'Listas' },
    { id: 'lists_delete', name: 'Deletar Listas', category: 'Listas' },
    { id: 'blacklist_view', name: 'Visualizar Blacklist', category: 'DNC/Blacklist' },
    { id: 'blacklist_manage', name: 'Gerenciar Blacklist', category: 'DNC/Blacklist' },
    { id: 'dnc_view', name: 'Visualizar DNC', category: 'DNC/Blacklist' },
    { id: 'dnc_manage', name: 'Gerenciar DNC', category: 'DNC/Blacklist' },
    { id: 'audios_view', name: 'Visualizar Áudios', category: 'Mídia' },
    { id: 'audios_upload', name: 'Upload de Áudios', category: 'Mídia' },
    { id: 'audios_delete', name: 'Deletar Áudios', category: 'Mídia' },
    { id: 'trunks_view', name: 'Visualizar Trunks', category: 'Configuração' },
    { id: 'trunks_manage', name: 'Gerenciar Trunks', category: 'Configuração' },
    { id: 'monitoring_view', name: 'Visualizar Monitoramento', category: 'Sistema' },
    { id: 'monitoring_advanced', name: 'Monitoramento Avançado', category: 'Sistema' },
    { id: 'users_view', name: 'Visualizar Usuários', category: 'Administração' },
    { id: 'users_manage', name: 'Gerenciar Usuários', category: 'Administração' },
    { id: 'roles_view', name: 'Visualizar Roles', category: 'Administração' },
    { id: 'roles_manage', name: 'Gerenciar Roles', category: 'Administração' },
    { id: 'system_config', name: 'Configuração do Sistema', category: 'Administração' }
  ];

  const permissionCategories = [...new Set(availablePermissions.map(p => p.category))];

  const loadRoles = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/roles');
      setRoles(response.data || []);
    } catch (error) {
      setRoles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoles();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingRole) {
        await makeApiRequest(`/roles/${editingRole.id}`, {
          method: 'PUT',
          body: JSON.stringify(formData)
        });
      } else {
        await makeApiRequest('/roles', {
          method: 'POST',
          body: JSON.stringify(formData)
        });
      }
      
      setShowForm(false);
      setEditingRole(null);
      resetForm();
      loadRoles();
    } catch (error) {
      alert('Erro ao salvar role. Tente novamente.');
    }
  };

  const handleEdit = (role) => {
    setEditingRole(role);
    setFormData({
      name: role.name,
      description: role.description,
      permissions: role.permissions || [],
      active: role.active
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir este role?')) {
      try {
        await makeApiRequest(`/roles/${id}`, { method: 'DELETE' });
        loadRoles();
      } catch (error) {
      }
    }
  };

  const handleToggleActive = async (id, currentStatus) => {
    try {
      await makeApiRequest(`/roles/${id}/toggle`, {
        method: 'PATCH',
        body: JSON.stringify({ active: !currentStatus })
      });
      loadRoles();
    } catch (error) {
    }
  };

  const handlePermissionChange = (permissionId, checked) => {
    setFormData(prev => ({
      ...prev,
      permissions: checked 
        ? [...prev.permissions, permissionId]
        : prev.permissions.filter(p => p !== permissionId)
    }));
  };

  const handleSelectAllCategory = (category, checked) => {
    const categoryPermissions = availablePermissions
      .filter(p => p.category === category)
      .map(p => p.id);
    
    setFormData(prev => ({
      ...prev,
      permissions: checked 
        ? [...new Set([...prev.permissions, ...categoryPermissions])]
        : prev.permissions.filter(p => !categoryPermissions.includes(p))
    }));
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      permissions: [],
      active: true
    });
    setEditingRole(null);
  };

  const getPermissionsByCategory = (category) => {
    return availablePermissions.filter(p => p.category === category);
  };

  const isCategoryFullySelected = (category) => {
    const categoryPermissions = getPermissionsByCategory(category);
    return categoryPermissions.every(p => formData.permissions.includes(p.id));
  };

  const getPermissionDisplayNames = (permissions) => {
    return permissions.map(permId => {
      const perm = availablePermissions.find(p => p.id === permId);
      return perm ? perm.name : permId;
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Carregando roles...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Gerenciamento de Roles</h2>
          <p className="text-gray-600 mt-1">Configure perfis de usuário e permissões do sistema</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
          </svg>
          Novo Role
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              {editingRole ? 'Editar Role' : 'Novo Role'}
            </h3>
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Role</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Descrição do role e suas responsabilidades"
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="active"
                      checked={formData.active}
                      onChange={(e) => setFormData({...formData, active: e.target.checked})}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                      Role ativo
                    </label>
                  </div>

                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Permissões Selecionadas: {formData.permissions.length}
                    </p>
                    <div className="text-xs text-gray-600 max-h-20 overflow-y-auto">
                      {formData.permissions.length > 0 ? (
                        getPermissionDisplayNames(formData.permissions).join(', ')
                      ) : (
                        'Nenhuma permissão selecionada'
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Permissões</label>
                  <div className="border border-gray-300 rounded-lg p-4 max-h-96 overflow-y-auto">
                    {permissionCategories.map(category => (
                      <div key={category} className="mb-4">
                        <div className="flex items-center mb-2">
                          <input
                            type="checkbox"
                            id={`category-${category}`}
                            checked={isCategoryFullySelected(category)}
                            onChange={(e) => handleSelectAllCategory(category, e.target.checked)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <label 
                            htmlFor={`category-${category}`}
                            className="ml-2 text-sm font-semibold text-gray-800"
                          >
                            {category}
                          </label>
                        </div>
                        <div className="ml-6 space-y-2">
                          {getPermissionsByCategory(category).map(permission => (
                            <div key={permission.id} className="flex items-center">
                              <input
                                type="checkbox"
                                id={permission.id}
                                checked={formData.permissions.includes(permission.id)}
                                onChange={(e) => handlePermissionChange(permission.id, e.target.checked)}
                                className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                              <label 
                                htmlFor={permission.id}
                                className="ml-2 text-sm text-gray-700"
                              >
                                {permission.name}
                              </label>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editingRole ? 'Atualizar' : 'Criar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {roles.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum role configurado</h3>
            <p className="mt-1 text-sm text-gray-500">Comece criando seu primeiro perfil de usuário.</p>
          </div>
        ) : (
          roles.map((role) => (
            <div key={role.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-gray-800 truncate">{role.name}</h3>
                    <button
                      onClick={() => handleToggleActive(role.id, role.active)}
                      className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full transition-colors ${
                        role.active 
                          ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                          : 'bg-red-100 text-red-800 hover:bg-red-200'
                      }`}
                    >
                      {role.active ? 'Ativo' : 'Inativo'}
                    </button>
                  </div>
                  {role.description && (
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">{role.description}</p>
                  )}
                </div>
                <div className="flex space-x-1">
                  <button
                    onClick={() => handleEdit(role)}
                    className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="Editar"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(role.id)}
                    className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Excluir"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="mt-3">
                <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                  <span>Permissões: {role.permissions?.length || 0}</span>
                  <span>Usuários: {role.users_count || 0}</span>
                </div>
                <div className="text-xs text-gray-500">
                  <span>Criado: {new Date(role.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RolesManager;