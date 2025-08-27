// src/context/PdfContext.jsx
import React, { createContext, useState } from "react";

export const PdfContext = createContext();

export const PdfProvider = ({ children }) => {
  const [cases, setCases] = useState([
    { id: 1, title: "Case 1", pdf: null },
  ]);
  const [activeCase, setActiveCase] = useState(cases[0]?.id || null);

  const addNewCase = () => {
    const newCase = { id: Date.now(), title: `Case ${cases.length + 1}`, pdf: null };
    setCases([...cases, newCase]);
    setActiveCase(newCase.id);
  };

  return (
    <PdfContext.Provider value={{ cases, activeCase, setActiveCase, addNewCase }}>
      {children}
    </PdfContext.Provider>
  );
};
