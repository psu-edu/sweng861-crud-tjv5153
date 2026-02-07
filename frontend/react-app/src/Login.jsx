import React from 'react';
import './Login.css';

async function handleLogin() {
    alert('Redirecting to Okta login...');
    try 
    {
        const response = await fetch('http://localhost:8000/signin', {
            method: 'GET',
            redirect: 'follow',
            headers: {
                'Content-Type': 'application/json',
            },
        }); 
        if (response.ok) 
        {
            const data = await response.json();
            window.location.href = data.redirect_uri;
        }
    }
    catch (error) 
    {
        console.error('Login failed:', error);
    }
}

function Login() {
  return (
            <div className="login-card">
                <p>Please sign in to continue</p>
                <button className="okta-btn" onClick={() => handleLogin()}>
                    Login with Okta
                </button>
            </div>
    );
}

export default Login;