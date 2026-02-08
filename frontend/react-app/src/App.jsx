import './App.css'
import MenuBar from './MenuBar';
import './MenuBar.css'
import { Route, Routes } from 'react-router-dom';
import Login from './Login';
import Cars from './Cars';
import CatFacts from './CatFacts';
import { ApiClientGetUserInfo } from './apiClient';


function Greeting() {
  return (<div>
            <h1>Welcome to Tim Volkar's App!</h1>
            <h2>Use the menu bar to navigate to different pages.</h2>
          </div>
    );
}

function Home() {
  return (
    <div>
      <Greeting />
    </div>
  );
}


function App() {
  return (
    <div>
      <MenuBar />
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/login" element={<Login/>}/>
        <Route path="/cars" element={<Cars/>}/>
        <Route path="/catFacts" element={<CatFacts/>}/>
        <Route path="*" element={<h1>Error 404 Page Not Found</h1>}/>
      </Routes>
    </div>
  );
}

export default App
