import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_BASE_URL}/doc`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data; // { document_id }
  } catch (error) {
    console.error("Error uploading document:", error.response?.data || error.message);
    throw error;
  }
};

export const getUserDocuments = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/docs`);
    return response.data.docs; // List of document IDs
  } catch (error) {
    console.error("Error fetching user documents:", error.response?.data || error.message);
    throw error;
  }
};

export const getDocumentReport = async (docId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/docs/${docId}`);

    if (response.status === 204) {
      return { processing: true }; // Document is still being processed
    }
    return response.data;
  } catch (error) {
    console.error("Error fetching document report:", error.response?.data || error.message);
    throw error;
  }
};
