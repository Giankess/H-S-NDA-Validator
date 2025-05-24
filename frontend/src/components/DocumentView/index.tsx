import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Divider,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import axios from 'axios';

interface CleanDocument {
  id: number;
  content: string;
  created_at: string;
  metadata: {
    original_filename: string;
    total_clauses: number;
    modified_clauses: number;
  };
}

const DocumentView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: cleanDocument, isLoading } = useQuery({
    queryKey: ['clean-document', id],
    queryFn: async () => {
      const response = await axios.get(`/api/documents/${id}/clean`);
      return response.data as CleanDocument;
    },
  });

  const handleDownload = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}/clean/download`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      if (typeof document !== 'undefined') {
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', cleanDocument?.metadata.original_filename || 'document.docx');
        document.body.appendChild(link);
        link.click();
        link.remove();
      }
    } catch (error) {
      toast.error('Error downloading document');
      console.error('Download error:', error);
    }
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Clean Document
      </Typography>

      {cleanDocument && (
        <>
          <Paper sx={{ p: 3, mb: 4 }}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Document Information
              </Typography>
              <Typography variant="body1">
                Original Filename: {cleanDocument.metadata.original_filename}
              </Typography>
              <Typography variant="body1">
                Total Clauses: {cleanDocument.metadata.total_clauses}
              </Typography>
              <Typography variant="body1">
                Modified Clauses: {cleanDocument.metadata.modified_clauses}
              </Typography>
              <Typography variant="body1">
                Created: {new Date(cleanDocument.created_at).toLocaleString()}
              </Typography>
            </Box>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom>
              Document Content
            </Typography>
            <Paper
              variant="outlined"
              sx={{
                p: 3,
                backgroundColor: 'background.default',
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
              }}
            >
              {cleanDocument.content}
            </Paper>
          </Paper>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="outlined"
              onClick={() => navigate(`/document/${id}/analysis`)}
            >
              Back to Analysis
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleDownload}
            >
              Download Document
            </Button>
          </Box>
        </>
      )}
    </Box>
  );
};

export default DocumentView; 