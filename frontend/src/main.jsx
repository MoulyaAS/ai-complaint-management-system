// main.jsx
// The entry point - React starts here.
// We wrap <App /> inside <Provider store={store}> so EVERY component
// in the app can read/write the Redux memory box.

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { store } from './store'
import App from './App.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </StrictMode>,
)