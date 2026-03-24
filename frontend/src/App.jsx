import { useState } from "react";
import Login from "./components/Login.jsx";

import { createBrowserRouter, RouterProvider } from "react-router-dom";

import Root from "./layouts/Root.jsx";
import Chat from "./components/Chat.jsx";
import Settings from "./components/Settings.jsx";
import About from "./components/About.jsx";
import NotFoundPage from "./components/NotFoundPage.jsx";


export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <>
      {isAuthenticated ? (
        <Chat />
      ) : (
        <Login onLogin={() => setIsAuthenticated(true)} />
      )}
    </>
  );
}


const router = createBrowserRouter(
  [
    {
      path: "/",
      element: <Root />,
      children: [
        { index: true, element: <Chat /> },
        { path: "/settings", element: <Settings /> },
        { path: "/about", element: <About /> },
      ],
    },
    { path: "*", element: <NotFoundPage /> },
  ],
  {
    basename: "/bearcat-brain",
  }
);

export default function App() {
  const [token, setToken] = useState(null);

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    setToken(null);
  };

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return <RouterProvider router={router} />;
}