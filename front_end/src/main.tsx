import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { Auth0Provider } from "@auth0/auth0-react";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Auth0Provider
      domain="dev-wt0zci4ynfbqzxos.us.auth0.com"
      clientId="LpxnYgirAye57HxI2yAYpLJdEt5BauI8"
      authorizationParams={{ redirect_uri: window.location.origin,audience: "https://api.hiresight.local"}}
    >
      <App />
    </Auth0Provider>
  </StrictMode>,
)
