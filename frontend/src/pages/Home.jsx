import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import Chatbot from "../components/Chatbot";
import { toast } from "react-toastify";
import { API_BASE_URL, extractKeyDetails, getSummary } from "../api";

const Home = () => {
  const [pdfFile, setPdfFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [documentIds, setDocumentIds] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [activeOption, setActiveOption] = useState("summary");
  const [keyDetails, setKeyDetails] = useState("");
  const [isLoadingKeyDetails, setIsLoadingKeyDetails] = useState(false);

  // Backend base URL
  const BASE_URL = API_BASE_URL;

  // Load document history from local storage on mount
  useEffect(() => {
    const storedDocs = JSON.parse(localStorage.getItem("uploadedDocs")) || [];
    setDocumentIds(storedDocs);
  }, []);

  // Fetch document summary from backend
  const fetchDocumentSummary = async (docId) => {
    try {
      setIsLoadingSummary(true);
      const res = await getSummary(docId);
      setSummary(res.answer || "");
    } catch (error) {
      console.error("Error fetching summary:", error.message);
      toast.error("Failed to fetch summary.");
      setSummary("");
    } finally {
      setIsLoadingSummary(false);
    }
  };
  
  
  

  // Handle file selection from sidebar
  const handleSelectDoc = (doc) => {
    setSelectedDoc(doc);
    setPdfUrl(`${BASE_URL}/doc/${doc.id}/view`);
    fetchDocumentSummary(doc.id);
  };

  const handleSelectOption = (option) => {
    setActiveOption(option);
    if (option === "key_details" && selectedDoc?.id) {
      setIsLoadingKeyDetails(true);
      extractKeyDetails(selectedDoc.id)
        .then((res) => setKeyDetails(res.answer || ""))
        .catch(() => setKeyDetails("Failed to extract key details."))
        .finally(() => setIsLoadingKeyDetails(false));
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files ? e.target.files[0] : e.dataTransfer.files[0];

    if (!file || file.type !== "application/pdf") {
      toast.error("Failed to upload. Please select a valid PDF.");
      return;
    }

    setPdfFile(file);
    setPdfUrl(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append("file", file);

    setIsUploading(true);
    try {
      const response = await fetch(`${BASE_URL}/doc`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      const newDoc = { id: data.document_id, name: file.name };

      // Prevent duplicate entries
      const updatedDocs = [...documentIds, newDoc].filter(
        (doc, index, self) => index === self.findIndex((d) => d.id === doc.id)
      );

      // Store document ID and name in local storage
      localStorage.setItem("uploadedDocs", JSON.stringify(updatedDocs));
      setDocumentIds(updatedDocs);
      setSelectedDoc(newDoc); // Auto-select new file

      fetchDocumentSummary(newDoc.id); // Fetch summary after upload

      toast.success("PDF uploaded successfully!");
    } catch (error) {
      console.error("Upload failed:", error);
      toast.error("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-b from-[#1F2430] to-[#12171D] text-slate-100">
      {/* Sidebar with document history */}
      <Sidebar onSelectDoc={handleSelectDoc} onSelectOption={handleSelectOption} />

      <div className="flex-1 flex flex-col p-6 relative">
        <h1 className="text-3xl font-bold tracking-wide text-[#64FFDA] mb-6">
          Welcome to Glean
        </h1>

        <div className="mb-16 flex flex-1 space-x-6">
          {/* PDF Viewer */}
          <div className="w-1/2 h-full border border-slate-700 rounded-lg overflow-hidden shadow-md bg-[rgba(255,255,255,0.04)] backdrop-blur-sm">
            {pdfUrl ? (
              <iframe src={pdfUrl} className="w-full h-full" title="PDF Viewer" />
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400">
                No PDF uploaded
              </div>
            )}
          </div>

          {/* Right Panel controlled by activeOption */}
          <div className="w-1/2 h-full border border-slate-700 rounded-lg p-0 overflow-hidden shadow-md bg-[rgba(255,255,255,0.04)] backdrop-blur-sm">
            <div className="h-full flex flex-col">
              <div className="p-4 border-b border-slate-700">
                {activeOption === "summary" && (
                  <h2 className="text-xl font-semibold">Summary</h2>
                )}
                {activeOption === "key_details" && (
                  <h2 className="text-xl font-semibold">Key Details</h2>
                )}
                {activeOption === "chat" && (
                  <h2 className="text-xl font-semibold">Chat</h2>
                )}
                {activeOption === "history" && (
                  <h2 className="text-xl font-semibold">Chat History</h2>
                )}
              </div>
              <div className="flex-1 p-6 overflow-auto">
                {activeOption === "summary" && (
                  <>
                    {selectedDoc ? (
                      <div className="text-base leading-relaxed text-slate-300 whitespace-pre-wrap break-words">
                        <div className="mb-2"><strong>Title:</strong> {selectedDoc.name}</div>
                        {isLoadingSummary ? (
                          <span className="text-gray-400">Loading...</span>
                        ) : (
                          <span>{summary}</span>
                        )}
                      </div>
                    ) : (
                      <p className="italic text-slate-400">Select a PDF to view details.</p>
                    )}
                  </>
                )}

                {activeOption === "key_details" && (
                  <>
                    {!selectedDoc ? (
                      <p className="italic text-slate-400">Select a PDF to view details.</p>
                    ) : isLoadingKeyDetails ? (
                      <p className="text-gray-400">Extracting...</p>
                    ) : (
                      <pre className="whitespace-pre-wrap break-words text-slate-300 max-h-full">{keyDetails}</pre>
                    )}
                  </>
                )}

                {activeOption === "chat" && (
                  <>
                    <p className="text-slate-400">Use the chat widget at bottom-right.</p>
                  </>
                )}

                {activeOption === "history" && (
                  <>
                    <p className="text-slate-400">Open the chat widget to load conversation history.</p>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Upload PDF Button */}
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2">
          <div
            className="w-80 h-12 p-3 border border-dashed border-slate-600 rounded-lg text-center cursor-pointer transition-colors duration-200 bg-[rgba(255,255,255,0.03)] backdrop-blur-sm hover:border-[#64FFDA] hover:bg-[rgba(100,255,218,0.08)]"
            onDragOver={(e) => {
              e.preventDefault();
            }}
            onDrop={(e) => {
              e.preventDefault();
              handleFileUpload(e);
            }}
            onClick={() => document.getElementById("pdfUpload").click()}
          >
            <input
              type="file"
              id="pdfUpload"
              accept="application/pdf"
              className="hidden"
              onChange={handleFileUpload}
            />
            <p className="text-base">
              {isUploading ? (
                <span className="text-[#64FFDA]">Uploading...</span>
              ) : pdfFile ? (
                <span className="text-[#64FFDA]">Uploaded: {pdfFile.name}</span>
              ) : (
                "Upload or Drag & Drop PDF here"
              )}
            </p>
          </div>
        </div>
      </div>

      <Chatbot activeDocId={selectedDoc?.id} />
    </div>
  );
};

export default Home;
