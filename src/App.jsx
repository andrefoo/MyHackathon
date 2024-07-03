import React, { useState } from "react";
import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Root from "./routes/root";
import ErrorPage from "./error-page";
import VideoAnalyzer from "./routes/video";

function App() {
  const [count, setCount] = useState(0);

  const router = createBrowserRouter([
    {
      path: "/",
      element: <Root />,
      errorElement: <ErrorPage />,
      children: [{}],
    },
    {
      path: "/video",
      element: <VideoAnalyzer />,
      errorElement: <ErrorPage />,
    }
  ]);

  return <RouterProvider router={router} />;
}

export default App;
