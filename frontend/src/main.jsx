// React Router setup for future multi-page support.
// The app currently is using one main page but routing setup is here so
// additional pages can be added easily.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

import { createBrowserRouter, RouterProvider } from "react-router-dom";

import Root from "./layouts/Root.jsx";
import Chat from "./components/Chat.jsx";
import Settings from "./components/Settings.jsx";
import About from "./components/About.jsx";
import NotFoundPage from "./components/NotFoundPage.jsx";

const router = createBrowserRouter([
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
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router = {router} />
  </StrictMode>,
)