# sweng861-crud-tjv5153

**Timothy Volkar**  
SWENG 861 – Software Construction  
CRUD App  
**Tech Stack:**

- Backend: Python FastAPI
- Frontend: TBD
- Database: SQL using SQLite

# Authentication Strategy

**Option C: Enterprise SSO**  
This option was chosen because the Campus Transit project is an internal tool that will be used by enforcement officers and students. Using enterprise SSO for internal tools streamlines the login process for a better use experience. Additionally, this keeps the application secure by utilizing the same policies as the rest of the organization.

**Application Flow**
The user clicks "Sign in using Okta" button and is then redirected to Okta login page. Once Okta authenticates, the user is redirected back to the application with an access token. The backend uses the token to get some user info and then displays an authenticated page.

**Client → Login button → Okta Auth → Callback → Backend → Token → Authenticated Page**

**Protected Endpoint Description**  
The secured endpoint is /api/hello. RequireAuth is a feature in JavaScript that checks if a user is authenticated before accessing protected endpoints. The protected endpoint in my application is protected in a similar way to a JavaScript endpoint using requireAuth. The application middleware runs on every http request including the ones to the protected endpoint. Additionally, fastAPI Depends feature is used. The token is validated before allowing access to the protected endpoint.

**OWASP Practices**

- BOLA was mitigated by only using data from the current token
- Excessive data exposure was avoided by not returning entire user objects or sensitive claims from the token. Only the required data is returned.
- Security misconfiguration was avoided by not returning stack traces in client responses. Specific JSON responses were chosen for all cases including auth failure. Errors are logged on the backend only.

**Bonus**  
 Rate limited was implemented in the Okta admin console. The requests / minute were limited for authentication attempts.

**Running Backend**  
`cd backend`  
`uvicorn main:app --reload --ssl-certfile ../cert.pem --ssl-keyfile ../key.pem`  
Backend runs on port 8000

**Running Frontend**
`cd frontend/react-app`  
`npm run dev`  
Frontend runs on port 5173
