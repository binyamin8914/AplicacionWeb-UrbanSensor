import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import UsersList from './pages/UsersList'
import './App.css'

export default function App() {
  return (
    <>
      <nav style={{ padding: 12 }}>
        <Link to="/">Usuarios</Link>
      </nav>
      <Routes>
        <Route path="/" element={<UsersList />} />
      </Routes>
    </>
  )
}
