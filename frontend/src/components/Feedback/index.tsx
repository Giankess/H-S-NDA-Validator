import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Rating,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import axios from 'axios';

interface FeedbackData {
  clause_id: number;
  rating: number;
  comment: string;
}

interface AnalysisResult {
  id: number;
  clause_text: string;
  original_text: string;
  suggested_text: string;
  confidence_score: number;
}

const Feedback: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState<Record<number, FeedbackData>>({});

  const { data: analysis, isLoading } = useQuery({
    queryKey: ['analysis', id],
    queryFn: async () => {
      const response = await axios.get(`/api/documents/${id}/analysis`);
      return response.data;
    },
  });

  const submitFeedbackMutation = useMutation({
    mutationFn: async (feedbackData: FeedbackData[]) => {
      const response = await axios.post(`/api/documents/${id}/feedback`, {
        feedback: feedbackData,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success('Feedback submitted successfully');
      navigate(`/document/${id}/analysis`);
    },
    onError: (error) => {
      toast.error('Error submitting feedback');
      console.error('Feedback submission error:', error);
    },
  });

  const handleRatingChange = (clauseId: number, value: number) => {
    setFeedback((prev) => ({
      ...prev,
      [clauseId]: {
        ...prev[clauseId],
        clause_id: clauseId,
        rating: value,
      },
    }));
  };

  const handleCommentChange = (clauseId: number, comment: string) => {
    setFeedback((prev) => ({
      ...prev,
      [clauseId]: {
        ...prev[clauseId],
        clause_id: clauseId,
        comment,
      },
    }));
  };

  const handleSubmit = () => {
    const feedbackData = Object.values(feedback).filter(
      (f) => f.rating > 0 || f.comment
    );
    submitFeedbackMutation.mutate(feedbackData);
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
        Provide Feedback
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
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          Clause {index + 1}
                        </Typography>
                        <Typography variant="body1" sx={{ mb: 1 }}>
                          Original: {clause.original_text}
                        </Typography>
                        <Typography variant="body1" sx={{ mb: 2 }}>
                          Suggested: {clause.suggested_text}
                        </Typography>
                        <Box sx={{ mb: 2 }}>
                          <Typography component="legend" gutterBottom>
                            Rate this suggestion:
                          </Typography>
                          <Rating
                            value={feedback[clause.id]?.rating || 0}
                            onChange={(_, value) =>
                              handleRatingChange(clause.id, value || 0)
                            }
                          />
                        </Box>
                        <TextField
                          fullWidth
                          multiline
                          rows={2}
                          label="Comments"
                          value={feedback[clause.id]?.comment || ''}
                          onChange={(e) =>
                            handleCommentChange(clause.id, e.target.value)
                          }
                        />
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
          variant="outlined"
          onClick={() => navigate(`/document/${id}/analysis`)}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          disabled={submitFeedbackMutation.isPending}
        >
          {submitFeedbackMutation.isPending ? (
            <CircularProgress size={24} />
          ) : (
            'Submit Feedback'
          )}
        </Button>
      </Box>
    </Box>
  );
};

export default Feedback; 