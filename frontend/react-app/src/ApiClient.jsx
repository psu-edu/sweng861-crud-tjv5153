const API_URL = "http://localhost:8000";

async function ApiFetch(endpoint) 
{
    try 
    {
        const response = await fetch(`${API_URL}${endpoint}`, {credentials: 'include'});
        if (!response.ok) 
        {
            throw new Error(`API request failed: ${response.statusText}`);
        }
        if (response.status === 401 || response.status === 403)
        {
            console.log("User is not authenticated. Redirecting to login page...");
            window.location.href = "/login";
            return;
        }
        return await response.json();
    } 
    catch (error) 
    {
        console.error("API error:", error);
        throw error;
    }
}

async function GetUserInfo() 
{
    return await ApiFetch("/userinfo");
}

function ApiClientFetch(endpoint) {
  return ApiFetch(endpoint);
}

function ApiClientGetUserInfo() {
  return GetUserInfo();
}
export default ApiClientFetch;
export { ApiClientGetUserInfo };