import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import { PdfProvider } from "./context/PdfContext";
import Home from "./pages/Home";
import Login from "./pages/Login";
import "./index.css";
import { ToastContainer } from "react-toastify";

function App() {
  return (
    <ThemeProvider>
    <PdfProvider>
    <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/home" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/home" element={<Home />} />
        </Routes>
      </Router>
      <ToastContainer />
    </PdfProvider>
    </ThemeProvider>
  );
}

export default App;
