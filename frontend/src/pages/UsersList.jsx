import React, { useEffect, useState } from 'react'
import { Table, Button, Space, message, Modal, Form, Input, Select, Tag, Row, Col } from 'antd'
import api, { setCSRFCookieHeader } from '../api'

const { Option } = Select

export default function UsersList() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 })
  const [editingUser, setEditingUser] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [form] = Form.useForm()
  const [groupsOptions, setGroupsOptions] = useState([])
  const [direccionesOptions, setDireccionesOptions] = useState([])
  const [currentProfile, setCurrentProfile] = useState(null)
  const [filterPerfil, setFilterPerfil] = useState(null)

  useEffect(() => {
    setCSRFCookieHeader()
    fetchGroups()
    fetchDirecciones()
    fetchCurrentProfile()
    fetchUsers(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchGroups = async () => {
    try {
      console.log('Fetching groups...')
      const res = await api.get('/administracion/groups/')
      console.log('Groups response:', res.data)
      
      // Manejar diferentes formatos de respuesta
      const groups = Array.isArray(res.data) ? res.data : (res.data.results || [])
      console.log('Groups parsed:', groups)
      
      setGroupsOptions(groups)
      
      if (groups.length === 0) {
        console.warn('No se encontraron grupos en la base de datos')
        message.warning('No hay grupos configurados en el sistema')
      }
    } catch (err) {
      console.error('Error fetching groups:', err)
      console.error('Error details:', err.response?.data)
      message.error('Error cargando grupos: ' + (err.response?.data?.detail || err.message))
    }
  }

  const fetchDirecciones = async () => {
    try {
      console.log('Fetching direcciones...')
      const res = await api.get('/direcciones/')  // Cambiar a /direcciones/ directamente
      console.log('Direcciones response:', res.data)
      
      // Manejar diferentes formatos de respuesta
      const direcciones = Array.isArray(res.data) ? res.data : (res.data.results || [])
      console.log('Direcciones parsed:', direcciones)
      
      setDireccionesOptions(direcciones)
    } catch (err) {
      console.error('Error fetching direcciones:', err)
      console.error('Error details:', err.response?.data)
      message.warning('Error cargando direcciones: ' + (err.response?.data?.detail || err.message))
    }
  }

  const fetchCurrentProfile = async () => {
    try {
      console.log('Fetching current profile...')
      const res = await api.get('/administracion/profile/me/')
      console.log('Current profile:', res.data)
      setCurrentProfile(res.data)
    } catch (err) {
      console.warn('No se pudo cargar perfil actual', err)
      // Para desarrollo: simular usuario SECPLA
      console.log('Setting default SECPLA profile for development')
      setCurrentProfile({ group: 'SECPLA' })
    }
  }

  const fetchUsers = async (page = 1, perfil = null) => {
    setLoading(true)
    try {
      const perfilToUse = perfil !== null ? perfil : filterPerfil
      console.log('Fetching users, page:', page, 'filter:', perfilToUse)
      
      const params = { page }
      if (perfilToUse) {
        params.perfil = perfilToUse
      }
      
      const res = await api.get('/administracion/usuarios/', { params })
      console.log('Users response:', res.data)
      
      const items = res.data.results ?? res.data ?? []
      setData(items)
      setPagination({
        current: page,
        pageSize: res.data?.page_size || 10,
        total: res.data?.count ?? items.length ?? 0
      })
    } catch (err) {
      console.error('Error fetching users:', err)
      console.error('Error details:', err.response?.data)
      message.error('Error cargando usuarios: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleTableChange = (pag) => {
    fetchUsers(pag.current)
  }

  const handleToggleActive = async (record) => {
    try {
      setLoading(true)
      setCSRFCookieHeader()
      await api.post(`/administracion/usuarios/${record.id}/toggle_active/`)
      message.success('Estado actualizado')
      fetchUsers(pagination.current)
    } catch (err) {
      console.error('Error toggling user:', err)
      message.error('Error al cambiar estado: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (record) => {
    console.log('Opening edit modal for user:', record)
    setEditingUser(record)
    setIsModalOpen(true)
    
    // Esperar a que el modal se renderice y luego establecer los valores
    setTimeout(() => {
      if (record) {
        const formValues = {
          username: record.username || '',
          first_name: record.first_name || '',
          last_name: record.last_name || '',
          email: record.email || '',
          profile: {
            group: record.profile?.group || null,
            telefono: record.profile?.telefono || '',
            direccion: record.profile?.direccion || null
          }
        }
        
        console.log('Setting form values:', formValues)
        form.setFieldsValue(formValues)
        
        // Forzar actualización del formulario para que aparezca el campo de dirección si es necesario
        form.validateFields().catch(() => {})
      }
    }, 100)
  }

  const openCreateModal = () => {
    setEditingUser(null)
    setIsModalOpen(true)
    
    // Resetear el formulario después de abrir el modal
    setTimeout(() => {
      form.resetFields()
    }, 0)
  }

  const handleModalCancel = () => {
    setIsModalOpen(false)
    setTimeout(() => {
      setEditingUser(null)
      form.resetFields()
    }, 300) // Esperar a que se cierre la animación del modal
  }

  const handleFormFinish = async (values) => {
    console.log('Form submitted with values:', values)
    
    try {
      setLoading(true)
      setCSRFCookieHeader()
      
      const payload = {
        username: values.username,
        first_name: values.first_name || '',
        last_name: values.last_name || '',
        email: values.email || '',
        profile: values.profile
      }
      
      // Solo incluir password si se proporcionó
      if (values.password) {
        payload.password = values.password
      }
      
      console.log('Sending payload:', payload)
      
      if (editingUser) {
        const res = await api.put(`/administracion/usuarios/${editingUser.id}/`, payload)
        console.log('Update response:', res.data)
        message.success('Usuario actualizado')
      } else {
        const res = await api.post(`/administracion/usuarios/`, payload)
        console.log('Create response:', res.data)
        message.success('Usuario creado')
      }
      
      handleModalCancel()
      fetchUsers(pagination.current)
    } catch (err) {
      console.error('Error saving user:', err)
      console.error('Error response:', err.response?.data)
      
      const errorMsg = err.response?.data?.detail || 
                      JSON.stringify(err.response?.data) || 
                      err.message ||
                      'Error guardando usuario'
      message.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
    { title: 'Usuario', dataIndex: 'username', key: 'username' },
    { title: 'Nombre', dataIndex: 'first_name', key: 'first_name' },
    { title: 'Apellido', dataIndex: 'last_name', key: 'last_name' },
    { title: 'Correo', dataIndex: 'email', key: 'email' },
    {
      title: 'Perfil',
      dataIndex: ['profile','group'],
      key: 'perfil',
      render: (v) => v || '-'
    },
    {
      title: 'Activo',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (v) => (v ? <Tag color="green">Activo</Tag> : <Tag color="red">Bloqueado</Tag>)
    },
    {
      title: 'Acciones',
      key: 'acciones',
      render: (_, record) => (
        <Space>
          <Button onClick={() => openEditModal(record)}>Editar</Button>
          <Button onClick={() => handleToggleActive(record)}>
            {record.is_active ? 'Bloquear' : 'Activar'}
          </Button>
        </Space>
      )
    }
  ]

  console.log('Render - groupsOptions:', groupsOptions)
  console.log('Render - direccionesOptions:', direccionesOptions)
  console.log('Render - currentProfile:', currentProfile)

  return (
    <div style={{ padding: 16 }}>
      <Row justify="space-between" style={{ marginBottom: 12 }}>
        <Col>
          <h2>Usuarios</h2>
        </Col>
        <Col>
          {currentProfile?.group === 'SECPLA' && (
            <Button 
              type="primary" 
              onClick={openCreateModal}
            >
              Nuevo Usuario
            </Button>
          )}
        </Col>
      </Row>

      <Row style={{ marginBottom: 12 }} gutter={8}>
        <Col>
          <Select
            placeholder="Filtrar por perfil"
            style={{ width: 200 }}
            allowClear
            value={filterPerfil}
            onChange={(val) => { 
              console.log('Filter changed to:', val)
              setFilterPerfil(val)
              setPagination(prev => ({ ...prev, current: 1 })) // Resetear a página 1
              fetchUsers(1, val) // Pasar el filtro directamente
            }}
          >
            {groupsOptions.map(g => (
              <Option key={g.id || g.name} value={g.name}>
                {g.name}
              </Option>
            ))}
          </Select>
        </Col>
      </Row>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{ 
          current: pagination.current, 
          pageSize: pagination.pageSize, 
          total: pagination.total 
        }}
        onChange={handleTableChange}
      />

      <Modal
        title={editingUser ? 'Editar usuario' : 'Crear usuario'}
        open={isModalOpen}
        onCancel={handleModalCancel}
        onOk={() => form.submit()}
        width={800}
      >
        <Form 
          form={form} 
          layout="vertical" 
          onFinish={handleFormFinish}
          initialValues={{
            username: '',
            first_name: '',
            last_name: '',
            email: '',
            profile: {
              group: null,
              telefono: '',
              direccion: null
            }
          }}
        >
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item 
                name="username" 
                label="Usuario" 
                rules={[{ required: true, message: 'El usuario es requerido' }]}
              >
                <Input disabled={!!editingUser} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                name="email" 
                label="Correo" 
                rules={[{ type: 'email', message: 'Correo inválido' }]}
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="first_name" label="Nombre">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="last_name" label="Apellido">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item 
                name={['profile','group']} 
                label="Perfil" 
                rules={[{ required: true, message: 'El perfil es requerido' }]}
              >
                <Select placeholder="Seleccione un perfil">
                  {groupsOptions.length > 0 ? (
                    groupsOptions.map(g => (
                      <Option key={g.id || g.name} value={g.name}>
                        {g.name}
                      </Option>
                    ))
                  ) : (
                    <Option disabled>No hay grupos disponibles</Option>
                  )}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name={['profile','telefono']} label="Teléfono">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item 
            noStyle 
            shouldUpdate={(prev, current) => 
              prev.profile?.group !== current.profile?.group
            }
          >
            {() => {
              const selectedGroup = form.getFieldValue(['profile','group'])
              const currentDireccion = form.getFieldValue(['profile','direccion'])
              console.log('Selected group in form:', selectedGroup)
              console.log('Current direccion in form:', currentDireccion)
              console.log('Direcciones options:', direccionesOptions)
              
              return selectedGroup === 'Territorial' ? (
                <Form.Item 
                  name={['profile','direccion']} 
                  label="Dirección" 
                  rules={[{ required: true, message: 'La dirección es requerida' }]}
                >
                  <Select placeholder="Seleccione dirección">
                    {direccionesOptions.length > 0 ? (
                      direccionesOptions.map(d => (
                        <Option key={d.id} value={d.id}>
                          {d.nombre || `Dirección ${d.id}`}
                        </Option>
                      ))
                    ) : (
                      <Option disabled>No hay direcciones disponibles</Option>
                    )}
                  </Select>
                </Form.Item>
              ) : null
            }}
          </Form.Item>

          <Form.Item 
            name="password" 
            label="Contraseña" 
            rules={[{ 
              required: !editingUser, 
              message: 'La contraseña es requerida' 
            }]}
          >
            <Input.Password 
              placeholder={editingUser ? 'Dejar vacío para no cambiar' : 'Ingrese contraseña'} 
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}