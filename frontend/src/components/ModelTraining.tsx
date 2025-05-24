import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  TextField,
  Paper,
} from '@mui/material';
import { styled } from '@mui/material/styles';

const Input = styled('input')({
  display: 'none',
});

const ModelTraining: React.FC = () => {
  const [trainingFiles, setTrainingFiles] = useState<File[]>([]);
  const [testFile, setTestFile] = useState<File | null>(null);
  const [isTraining, setIsTraining] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrainingFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setTrainingFiles(Array.from(event.target.files));
    }
  };

  const handleTestFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setTestFile(event.target.files[0]);
    }
  };

  const trainModels = async () => {
    setIsTraining(true);
    setError(null);
    setTrainingStatus(null);

    try {
      const formData = new FormData();
      trainingFiles.forEach((file) => {
        formData.append('redline_files', file);
      });

      const response = await fetch('http://localhost:8000/api/training/train-from-files', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Training failed');
      }

      const result = await response.json();
      setTrainingStatus(`Training completed successfully! Trained on ${result.training_samples} samples.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during training');
    } finally {
      setIsTraining(false);
    }
  };

  const testModel = async () => {
    if (!testFile) return;

    setIsTesting(true);
    setError(null);
    setTestResults(null);

    try {
      const formData = new FormData();
      formData.append('file', testFile);

      const response = await fetch('http://localhost:8000/api/documents/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Testing failed');
      }

      const result = await response.json();
      setTestResults(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during testing');
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Model Training and Testing
      </Typography>

      <Grid container spacing={3}>
        {/* Training Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Train Models
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Upload redline versions of your documents to train the models.
              </Typography>

              <Box sx={{ mb: 2 }}>
                <label htmlFor="training-files">
                  <Input
                    id="training-files"
                    type="file"
                    multiple
                    accept=".docx"
                    onChange={handleTrainingFileChange}
                  />
                  <Button variant="contained" component="span">
                    Select Training Files
                  </Button>
                </label>
                {trainingFiles.length > 0 && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {trainingFiles.length} file(s) selected
                  </Typography>
                )}
              </Box>

              <Button
                variant="contained"
                color="primary"
                onClick={trainModels}
                disabled={isTraining || trainingFiles.length === 0}
                startIcon={isTraining ? <CircularProgress size={20} /> : null}
              >
                {isTraining ? 'Training...' : 'Train Models'}
              </Button>

              {trainingStatus && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  {trainingStatus}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Testing Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Models
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Upload a document to test the trained models.
              </Typography>

              <Box sx={{ mb: 2 }}>
                <label htmlFor="test-file">
                  <Input
                    id="test-file"
                    type="file"
                    accept=".docx"
                    onChange={handleTestFileChange}
                  />
                  <Button variant="contained" component="span">
                    Select Test File
                  </Button>
                </label>
                {testFile && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {testFile.name} selected
                  </Typography>
                )}
              </Box>

              <Button
                variant="contained"
                color="primary"
                onClick={testModel}
                disabled={isTesting || !testFile}
                startIcon={isTesting ? <CircularProgress size={20} /> : null}
              >
                {isTesting ? 'Testing...' : 'Test Model'}
              </Button>

              {testResults && (
                <Paper sx={{ mt: 2, p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Test Results
                  </Typography>
                  <pre style={{ whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(testResults, null, 2)}
                  </pre>
                </Paper>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default ModelTraining; 