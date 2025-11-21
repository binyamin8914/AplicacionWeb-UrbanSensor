import React, { useEffect, useState } from 'react'
import { Table, Button, Space, message } from 'antd'
import api, { setCSRFCookieHeader } from '../api'

export default function UsersList() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setCSRFCookieHeader()
    fetchUsers()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const res = await api.get('/administracion/usuarios/')
      const items = res.data.results ?? res.data ?? []
      setData(items)
    } catch (err) {
      console.error('Error al cargar usuarios', err)
      message.error('Error cargando usuarios. Mira la consola del navegador y del backend.')
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
      title: 'Activo',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (v) => (v ? <span style={{ color: 'green' }}>Activo</span> : <span style={{ color: 'red' }}>Bloqueado</span>),
    },
    {
      title: 'Acciones',
      key: 'acciones',
      render: (_, record) => (
        <Space>
          <Button onClick={() => console.log('Ver', record.id)}>Ver</Button>
          <Button onClick={() => console.log('Editar', record.id)}>Editar</Button>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: 16 }}>
      <h2>Usuarios</h2>
      <Table rowKey="id" columns={columns} dataSource={data} loading={loading} />
    </div>
  )
}