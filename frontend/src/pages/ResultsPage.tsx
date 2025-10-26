import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Paper,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Download,
  Home,
  CloudUpload,
  Person,
  School,
  CalendarToday,
  Assessment,
  PictureAsPdf,
} from '@mui/icons-material';

import { apiService, EvaluationResults } from '../services/api';
import { PDFGenerator } from '../components/PDFGenerator';

const ResultsPage: React.FC = () => {
  const { uploadId } = useParams<{ uploadId: string }>();
  const [results, setResults] = useState<EvaluationResults | null>(null);
  const [aiToolsResults, setAiToolsResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const printRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (uploadId) {
      setLoading(true);
      Promise.all([
        fetchResults(uploadId),
        fetchAIToolsResults(uploadId)
      ]).finally(() => {
        setLoading(false);
      });
    }
  }, [uploadId]);

  const fetchResults = async (id: string) => {
    try {
      const data = await apiService.getEvaluationResults(id);
      setResults(data);
    } catch (err: any) {
      // Don't set error for missing evaluation results, AI tools might exist
      console.log('No evaluation results found (this is OK if using AI tools only)');
    }
  };
  
  const fetchAIToolsResults = async (id: string) => {
    try {
      const url = `http://localhost:8000/api/v1/peer-review/submissions/${id}/ai-tools-results`;
      console.log('🔍 Fetching from URL:', url);
      const response = await fetch(url);
      console.log('📡 Response:', response.status, response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ AI Tools Results fetched successfully!');
        console.log('📦 Data:', data);
        console.log('📦 Keys:', Object.keys(data));
        setAiToolsResults(data);
        console.log('✅ State updated with AI tools results');
      } else {
        console.log('❌ Response not OK:', response.status);
      }
    } catch (err: any) {
      console.log('❌ Error fetching AI tools results:', err);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getPercentageColor = (percentage: number) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'warning';
    return 'error';
  };

  const generatePDF = async () => {
    if (!results) return;

    try {
      setIsGeneratingPdf(true);
      await PDFGenerator.generatePDFReport(results);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  // Debug logging
  console.log('=== RENDER STATE ===');
  console.log('loading:', loading);
  console.log('error:', error);  
  console.log('results:', results);
  console.log('aiToolsResults:', aiToolsResults);
  console.log('aiToolsResults is null?', aiToolsResults === null);
  console.log('aiToolsResults keys:', aiToolsResults ? Object.keys(aiToolsResults) : 'N/A');
  console.log('==================');

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading evaluation results...
        </Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert
          severity="error"
          action={
            <Button component={Link} to="/upload" color="inherit" size="small">
              Upload New
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  if (!results && !aiToolsResults) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="info">No results found for this upload.</Alert>
      </Container>
    );
  }

  // Show AI tools results even if there's no evaluation
  if (aiToolsResults && Object.keys(aiToolsResults).length > 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <div ref={printRef}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              AI Writing Assistance Results
            </Typography>
            <Chip
              icon={<CheckCircle />}
              label="Analysis Complete"
              color="success"
              size="medium"
            />
          </Box>

          {/* AI Tools Results */}
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                AI Tools Output
              </Typography>
              
              {/* Paraphraser Results */}
              {aiToolsResults.paraphraser && aiToolsResults.paraphraser.success && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                    ✍️ Paraphraser
                  </Typography>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Original Text:
                    </Typography>
                    <Box sx={{ maxHeight: 200, overflow: 'auto', mb: 2 }}>
                      <Typography variant="body1">
                        {aiToolsResults.paraphraser.original}
                      </Typography>
                    </Box>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="body2" color="primary" gutterBottom>
                      Paraphrased Text ({aiToolsResults.paraphraser.style_applied} style):
                    </Typography>
                    <Box sx={{ maxHeight: 200, overflow: 'auto', mb: 2 }}>
                      <Typography variant="body1">
                        {aiToolsResults.paraphraser.paraphrased}
                      </Typography>
                    </Box>
                    
                    {aiToolsResults.paraphraser.changes_summary && (
                      <Alert severity="info" sx={{ mt: 2 }}>
                        {aiToolsResults.paraphraser.changes_summary}
                      </Alert>
                    )}
                  </Paper>
                </Box>
              )}

              {/* Grammar Checker Results */}
              {aiToolsResults.grammar && aiToolsResults.grammar.success && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                    📝 Grammar Checker
                  </Typography>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Original Text:
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body1">
                        {aiToolsResults.grammar.original}
                      </Typography>
                    </Box>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="body2" color="success.main" gutterBottom>
                      Corrected Text:
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body1">
                        {aiToolsResults.grammar.corrected}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                      <Chip label={`${aiToolsResults.grammar.error_count} errors found`} color="warning" size="small" />
                      <Chip label={`Quality: ${aiToolsResults.grammar.overall_quality}`} color="info" size="small" />
                    </Box>
                  </Paper>
                </Box>
              )}

              {/* AI Humanizer Results */}
              {aiToolsResults.humanizer && aiToolsResults.humanizer.success && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                    👤 AI Humanizer
                  </Typography>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Original Text (AI Score: {aiToolsResults.humanizer.ai_score_before}%):
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body1">
                        {aiToolsResults.humanizer.original}
                      </Typography>
                    </Box>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Typography variant="body2" color="success.main" gutterBottom>
                      Humanized Text (AI Score: {aiToolsResults.humanizer.ai_score_after}%):
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body1">
                        {aiToolsResults.humanizer.humanized}
                      </Typography>
                    </Box>
                    
                    {aiToolsResults.humanizer.changes_made && aiToolsResults.humanizer.changes_made.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          Changes Made:
                        </Typography>
                        <List dense>
                          {aiToolsResults.humanizer.changes_made.map((change: string, idx: number) => (
                            <ListItem key={idx}>
                              <ListItemText primary={`• ${change}`} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                  </Paper>
                </Box>
              )}

              {/* AI Detector Results */}
              {aiToolsResults.ai_detector && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                    🤖 AI Detector
                  </Typography>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Chip 
                        label={aiToolsResults.ai_detector.is_ai_generated ? 'AI Generated' : 'Human Written'} 
                        color={aiToolsResults.ai_detector.is_ai_generated ? 'error' : 'success'}
                      />
                      <Chip 
                        label={`${aiToolsResults.ai_detector.confidence}% Confidence`} 
                        color={aiToolsResults.ai_detector.confidence_level === 'high' ? 'error' : 'warning'}
                      />
                    </Box>
                    <Typography variant="body2">
                      {aiToolsResults.ai_detector.explanation}
                    </Typography>
                  </Paper>
                </Box>
              )}

              {/* Plagiarism Quick Check Results */}
              {aiToolsResults.plagiarism_quick && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                    📋 Quick Plagiarism Check
                  </Typography>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Chip 
                        label={`${aiToolsResults.plagiarism_quick.originality_score}% Original`} 
                        color={aiToolsResults.plagiarism_quick.originality_score >= 80 ? 'success' : 'warning'}
                      />
                      <Chip 
                        label={`${aiToolsResults.plagiarism_quick.ai_confidence}% AI Detected`} 
                        color="info"
                      />
                    </Box>
                    <Typography variant="body2">
                      {aiToolsResults.plagiarism_quick.summary}
                    </Typography>
                  </Paper>
                </Box>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button
            component={Link}
            to="/"
            variant="outlined"
            startIcon={<Home />}
            sx={{ mr: 2 }}
          >
            Home
          </Button>
          <Button
            component={Link}
            to="/upload"
            variant="contained"
            startIcon={<CloudUpload />}
          >
            Upload Another
          </Button>
        </Box>
      </Container>
    );
  }

  // If no AI tools results but has evaluation results, show old format
  if (!results) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="info">
          Analysis reports are not yet available. They may still be processing.
        </Alert>
      </Container>
    );
  }

  const evaluation = results.evaluation_results;
  const percentage = evaluation.percentage || 0;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <div ref={printRef}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            ProctorIQ Evaluation Results
          </Typography>
          <Chip
            icon={<CheckCircle />}
            label="Evaluation Complete"
            color="success"
            size="medium"
          />
        </Box>

      {/* Student Information */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            Student Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Person sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary">
                  Student Name
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight={500}>
                {results.student_info.name}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <School sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary">
                  Exam ID
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight={500}>
                {results.student_info.exam_id}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CalendarToday sx={{ mr: 1, color: 'text.secondary' }} />
                <Typography variant="body2" color="text.secondary">
                  Evaluated On
                </Typography>
              </Box>
              <Typography variant="body1" fontWeight={500}>
                {formatDate(results.processing_info.processing_timestamp)}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Overall Score */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            Overall Score
          </Typography>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h2" component="div" color={`${getPercentageColor(percentage)}.main`}>
                  {percentage.toFixed(1)}%
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {evaluation.total_marks_awarded} / {evaluation.total_possible_marks} marks
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="body2" gutterBottom>
                  Performance Distribution
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={percentage}
                  color={getPercentageColor(percentage)}
                  sx={{ height: 12, borderRadius: 6, mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Grade: {percentage >= 80 ? 'A' : percentage >= 60 ? 'B' : percentage >= 40 ? 'C' : 'D'}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Section-wise Results */}
      {evaluation.section_wise_marks && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Section-wise Performance
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(evaluation.section_wise_marks).map(([section, marks]: [string, any]) => (
                <Grid item xs={12} sm={6} md={4} key={section}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {section.replace('_', ' ').toUpperCase()}
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {marks.awarded} / {marks.total}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {((marks.awarded / marks.total) * 100).toFixed(1)}%
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Detailed Question Results */}
      {evaluation.question_evaluations && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Question-wise Evaluation
            </Typography>
            <List>
              {evaluation.question_evaluations.map((question: any, index: number) => (
                <React.Fragment key={index}>
                  <ListItem sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <Box sx={{ width: '100%', mb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          Question {question.question_id}
                        </Typography>
                        <Chip
                          label={`${question.marks_awarded}/${question.total_marks}`}
                          color={question.marks_awarded === question.total_marks ? 'success' : 'warning'}
                          size="small"
                        />
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {question.feedback}
                    </Typography>
                    {question.missing_elements && question.missing_elements.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="error.main">
                          Missing elements: {question.missing_elements.join(', ')}
                        </Typography>
                      </Box>
                    )}
                  </ListItem>
                  {index < evaluation.question_evaluations.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Overall Feedback */}
      {evaluation.overall_feedback && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Overall Feedback
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
              {evaluation.overall_feedback}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* AI Tools Results */}
      {aiToolsResults && Object.keys(aiToolsResults).length > 0 && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              AI Writing Assistance Results
            </Typography>
            
            {/* Paraphraser Results */}
            {aiToolsResults.paraphraser && aiToolsResults.paraphraser.success && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  ✍️ Paraphraser
                </Typography>
                <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Original Text:
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {aiToolsResults.paraphraser.original}
                  </Typography>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="body2" color="primary" gutterBottom>
                    Paraphrased Text ({aiToolsResults.paraphraser.style_applied} style):
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {aiToolsResults.paraphraser.paraphrased}
                  </Typography>
                  
                  {aiToolsResults.paraphraser.changes_summary && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      {aiToolsResults.paraphraser.changes_summary}
                    </Alert>
                  )}
                </Paper>
              </Box>
            )}

            {/* Grammar Checker Results */}
            {aiToolsResults.grammar && aiToolsResults.grammar.success && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  📝 Grammar Checker
                </Typography>
                <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Original Text:
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {aiToolsResults.grammar.original}
                  </Typography>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="body2" color="success.main" gutterBottom>
                    Corrected Text:
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {aiToolsResults.grammar.corrected}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                    <Chip label={`${aiToolsResults.grammar.error_count} errors found`} color="warning" size="small" />
                    <Chip label={`Quality: ${aiToolsResults.grammar.overall_quality}`} color="info" size="small" />
                  </Box>
                </Paper>
              </Box>
            )}

            {/* AI Humanizer Results */}
            {aiToolsResults.humanizer && aiToolsResults.humanizer.success && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  👤 AI Humanizer
                </Typography>
                <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Original Text (AI Score: {aiToolsResults.humanizer.ai_score_before}%):
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {aiToolsResults.humanizer.original}
                  </Typography>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="body2" color="success.main" gutterBottom>
                    Humanized Text (AI Score: {aiToolsResults.humanizer.ai_score_after}%):
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {aiToolsResults.humanizer.humanized}
                  </Typography>
                  
                  {aiToolsResults.humanizer.changes_made && aiToolsResults.humanizer.changes_made.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Changes Made:
                      </Typography>
                      <List dense>
                        {aiToolsResults.humanizer.changes_made.map((change: string, idx: number) => (
                          <ListItem key={idx}>
                            <ListItemText primary={`• ${change}`} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Paper>
              </Box>
            )}

            {/* AI Detector Results */}
            {aiToolsResults.ai_detector && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  🤖 AI Detector
                </Typography>
                <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Chip 
                      label={aiToolsResults.ai_detector.is_ai_generated ? 'AI Generated' : 'Human Written'} 
                      color={aiToolsResults.ai_detector.is_ai_generated ? 'error' : 'success'}
                    />
                    <Chip 
                      label={`${aiToolsResults.ai_detector.confidence}% Confidence`} 
                      color={aiToolsResults.ai_detector.confidence_level === 'high' ? 'error' : 'warning'}
                    />
                  </Box>
                  <Typography variant="body2">
                    {aiToolsResults.ai_detector.explanation}
                  </Typography>
                </Paper>
              </Box>
            )}

            {/* Plagiarism Quick Check Results */}
            {aiToolsResults.plagiarism_quick && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                  📋 Quick Plagiarism Check
                </Typography>
                <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Chip 
                      label={`${aiToolsResults.plagiarism_quick.originality_score}% Original`} 
                      color={aiToolsResults.plagiarism_quick.originality_score >= 80 ? 'success' : 'warning'}
                    />
                    <Chip 
                      label={`${aiToolsResults.plagiarism_quick.ai_confidence}% AI Detected`} 
                      color="info"
                    />
                  </Box>
                  <Typography variant="body2">
                    {aiToolsResults.plagiarism_quick.summary}
                  </Typography>
                </Paper>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
      </div>

      {/* Action Buttons */}
      <Box id="action-buttons" sx={{ textAlign: 'center', mt: 4 }}>
        <Button
          onClick={generatePDF}
          variant="contained"
          startIcon={isGeneratingPdf ? <CircularProgress size={20} /> : <PictureAsPdf />}
          disabled={isGeneratingPdf}
          sx={{ mr: 2 }}
        >
          {isGeneratingPdf ? 'Generating PDF...' : 'Download PDF Report'}
        </Button>
        <Button
          component={Link}
          to="/"
          variant="outlined"
          startIcon={<Home />}
          sx={{ mr: 2 }}
        >
          Home
        </Button>
        <Button
          component={Link}
          to="/upload"
          variant="contained"
          startIcon={<CloudUpload />}
        >
          Upload Another
        </Button>
      </Box>
    </Container>
  );
};

export default ResultsPage;
