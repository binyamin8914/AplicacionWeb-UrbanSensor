import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom' // Importación de BrowserRouter para el enrutamiento
import './index.css'
import App from './App.jsx'
import 'antd/dist/reset.css'; // Importación del archivo CSS de reinicio de Ant Design

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter> {/* Envolviendo la aplicación con BrowserRouter */}
      <App />
    </BrowserRouter>
  </StrictMode>,
)
