import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

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
          <Layout>
            <Routes>
              <Route path="/" element={<DocumentUpload />} />
              <Route path="/document/:id/analysis" element={<DocumentAnalysis />} />
              <Route path="/document/:id/feedback" element={<Feedback />} />
              <Route path="/document/:id/view" element={<DocumentView />} />
            </Routes>
          </Layout>
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