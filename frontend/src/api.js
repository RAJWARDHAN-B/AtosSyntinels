import axios from "axios";

const API_BASE_URL = "https://glean.onrender.com";

export const uploadDocument = async (file, token) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_BASE_URL}/doc`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data; // { document_id }
  } catch (error) {
    console.error("Error uploading document:", error.response?.data || error.message);
    throw error;
  }
};

export const getUserDocuments = async (token) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/docs`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data.docs; // List of document IDs
  } catch (error) {
    console.error("Error fetching user documents:", error.response?.data || error.message);
    throw error;
  }
};

export const getDocumentReport = async (docId, token) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/docs/${docId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 204) {
      return { processing: true }; // Document is still being processed
    }
    return response.data;
  } catch (error) {
    console.error("Error fetching document report:", error.response?.data || error.message);
    throw error;
  }
};
