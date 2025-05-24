import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AppBar, Toolbar, Typography, Container, Button, Box } from '@mui/material';
import ModelTraining from './components/ModelTraining';

import Layout from './components/Layout';
import DocumentUpload from './components/DocumentUpload';
import DocumentAnalysis from './components/DocumentAnalysis';
import Feedback from './components/Feedback';
import DocumentView from './components/DocumentView';
import theme from './theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <Router>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                NDA Validator
              </Typography>
              <Button color="inherit" component={Link} to="/">
                Home
              </Button>
              <Button color="inherit" component={Link} to="/training">
                Model Training
              </Button>
            </Toolbar>
          </AppBar>

          <Container>
            <Box sx={{ my: 4 }}>
              <Routes>
                <Route path="/" element={<Layout>
                  <Routes>
                    <Route path="/" element={<DocumentUpload />} />
                    <Route path="/document/:id/analysis" element={<DocumentAnalysis />} />
                    <Route path="/document/:id/feedback" element={<Feedback />} />
                    <Route path="/document/:id/view" element={<DocumentView />} />
                  </Routes>
                </Layout>} />
                <Route path="/training" element={<ModelTraining />} />
              </Routes>
            </Box>
          </Container>
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App; 