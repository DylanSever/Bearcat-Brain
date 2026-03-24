import { useState } from "react";
import Login from "./components/Login.jsx";

import { createBrowserRouter, RouterProvider } from "react-router-dom";

import Root from "./layouts/Root.jsx";
import Chat from "./components/Chat.jsx";
import Settings from "./components/Settings.jsx";
import About from "./components/About.jsx";
import NotFoundPage from "./components/NotFoundPage.jsx";


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
  const [isAuthenticated, setIsAuthenticated] = useState(null);

 
  useEffect(() => {
    fetch("/bearcat-brain/api/chat", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: "auth check" }),
    })
      .then((res) => {
        if (res.status === 401) {
          setIsAuthenticated(false);
        } else {
          setIsAuthenticated(true);
        }
      })
      .catch(() => setIsAuthenticated(false));
  }, []);


  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return <RouterProvider router={router} />;
}