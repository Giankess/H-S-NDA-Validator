import React, { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import axios from 'axios';

const DocumentUpload: React.FC = () => {
  const navigate = useNavigate();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast.success('Document uploaded successfully');
      navigate(`/document/${data.id}`);
    },
    onError: (error) => {
      toast.error('Error uploading document');
      console.error('Upload error:', error);
    },
  });

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        uploadMutation.mutate(file);
      }
    },
    [uploadMutation]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
  });

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
      }}
    >
      <Typography variant="h4" component="h1" gutterBottom>
        NDA Validator
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload your NDA document for analysis and validation
      </Typography>

      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mt: 4,
          width: '100%',
          maxWidth: 600,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          '&:hover': {
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        {uploadMutation.isPending ? (
          <CircularProgress />
        ) : (
          <>
            <CloudUploadIcon
              sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}
            />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop the NDA document here'
                : 'Drag and drop your NDA document here'}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              or
            </Typography>
            <Button variant="contained" component="span">
              Browse Files
            </Button>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block', mt: 2 }}
            >
              Only .docx files are supported
            </Typography>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default DocumentUpload; 