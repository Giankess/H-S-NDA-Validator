import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
} from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import axios from 'axios';

interface AnalysisResult {
  id: number;
  clause_text: string;
  original_text: string;
  suggested_text: string;
  confidence_score: number;
  validation_score?: number;
}

const DocumentAnalysis: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: document, isLoading: isLoadingDocument } = useQuery({
    queryKey: ['document', id],
    queryFn: async () => {
      const response = await axios.get(`/api/documents/${id}`);
      return response.data;
    },
  });

  const { data: analysis, isLoading: isLoadingAnalysis } = useQuery({
    queryKey: ['analysis', id],
    queryFn: async () => {
      const response = await axios.post(`/api/documents/${id}/analyze`);
      return response.data;
    },
    enabled: !!document && document.status === 'UPLOADED',
  });

  const createCleanMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/documents/${id}/clean`);
      return response.data;
    },
    onSuccess: () => {
      toast.success('Clean document created successfully');
      navigate(`/document/${id}/view`);
    },
    onError: (error) => {
      toast.error('Error creating clean document');
      console.error('Clean document error:', error);
    },
  });

  const handleFeedback = () => {
    navigate(`/document/${id}/feedback`);
  };

  if (isLoadingDocument || isLoadingAnalysis) {
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
        Document Analysis
      </Typography>

      {analysis?.clauses && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Analysis Results
          </Typography>
          <List>
            {analysis.clauses.map((clause: AnalysisResult, index: number) => (
              <React.Fragment key={clause.id}>
                <ListItem alignItems="flex-start">
                  <ListItemText
                    primary={
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle1" component="span">
                          Clause {index + 1}
                        </Typography>
                        <Chip
                          label={`Confidence: ${clause.confidence_score}%`}
                          color={
                            clause.confidence_score >= 80
                              ? 'success'
                              : clause.confidence_score >= 60
                              ? 'warning'
                              : 'error'
                          }
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography
                          component="div"
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          Original:
                        </Typography>
                        <Typography
                          component="div"
                          variant="body1"
                          sx={{ mb: 2 }}
                        >
                          {clause.original_text}
                        </Typography>
                        <Typography
                          component="div"
                          variant="body2"
                          color="text.secondary"
                          sx={{ mb: 1 }}
                        >
                          Suggested:
                        </Typography>
                        <Typography component="div" variant="body1">
                          {clause.suggested_text}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
                {index < analysis.clauses.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleFeedback}
          disabled={!analysis}
        >
          Provide Feedback
        </Button>
        <Button
          variant="contained"
          color="secondary"
          onClick={() => createCleanMutation.mutate()}
          disabled={!analysis || createCleanMutation.isPending}
        >
          {createCleanMutation.isPending ? (
            <CircularProgress size={24} />
          ) : (
            'Accept Changes'
          )}
        </Button>
      </Box>
    </Box>
  );
};

export default DocumentAnalysis; 