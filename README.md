# sweng861-crud-tjv5153
**Timothy Volkar**  
SWENG 861 – Software Construction  
Campus Transit CRUD App  
**Tech Stack:**  
- Backend: Python FastAPI  
- Frontend: TBD
- Database: TBD  

# Authentication Strategy
**Option C: Enterprise SSO**  
This option was chosen because the Campus Transit project is an internal tool that will be used by enforcement officers and students. Using enterprise SSO for internal tools streamlines the login process for a better use experience. Additionally, this keeps the application secure by utilizing the same policies as the rest of the organization.  

**Application Flow**
The user clicks "Sign in using Okta" button and is then redirected to Okta login page. Once Okta authenticates, the user is redirected back to the application with an access token. The backend uses the token to get some user info and then displays an authenticated page.  

**Client → Login button → Okta Auth → Callback → Backend → Token → Authenticated Page**