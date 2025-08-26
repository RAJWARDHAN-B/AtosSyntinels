import React from "react";  // ✅ Add this if missing
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";  // ✅ Ensure Tailwind is correctly imported


ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
