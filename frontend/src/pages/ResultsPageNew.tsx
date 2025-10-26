import React, { useState, useEffect } from 'react';
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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Home,
  CloudUpload,
  Person,
  CalendarToday,
  Assessment,
  Code,
  Security,
  ExpandMore,
} from '@mui/icons-material';

import { apiService, type Submission, type CodeAnalysisReport, type PlagiarismReport } from '../services/api';

const ResultsPageNew: React.FC = () => {
  const { uploadId } = useParams<{ uploadId: string }>();
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [codeAnalysis, setCodeAnalysis] = useState<CodeAnalysisReport | null>(null);
  const [plagiarismReport, setPlagiarismReport] = useState<PlagiarismReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (uploadId) {
      fetchResults(uploadId);
    }
  }, [uploadId]);

  const fetchResults = async (id: string) => {
    try {
      setLoading(true);
      
      // Get submission details
      const submissionData = await apiService.getSubmission(id);
      setSubmission(submissionData.submission);

      // Get code analysis if available
      if (submissionData.has_code_analysis) {
        try {
          const analysisData = await apiService.getCodeAnalysisReport(id);
          setCodeAnalysis(analysisData);
        } catch (err) {
          console.log('Code analysis not yet available');
        }
      }

      // Get plagiarism report if available
      if (submissionData.has_plagiarism_report) {
        try {
          const plagiarismData = await apiService.getPlagiarismReport(id);
          setPlagiarismReport(plagiarismData);
        } catch (err) {
          console.log('Plagiarism report not yet available');
        }
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch results');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getGradeColor = (grade: string) => {
    if (grade === 'A' || grade === 'A+') return 'success';
    if (grade === 'B' || grade === 'B+') return 'info';
    if (grade === 'C') return 'warning';
    return 'error';
  };

  const getRiskColor = (risk: string) => {
    if (risk === 'low') return 'success';
    if (risk === 'medium') return 'warning';
    if (risk === 'high') return 'error';
    return 'error';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading submission results...
        </Typography>
      </Container>
    );
  }

  if (error || !submission) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="error">
          <Typography variant="h6">{error || 'Submission not found'}</Typography>
          <Button component={Link} to="/upload" variant="contained" sx={{ mt: 2 }}>
            Upload New Submission
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Submission Results
          </Typography>
          <Box>
            <Button
              component={Link}
              to="/history"
              startIcon={<Home />}
              variant="outlined"
              sx={{ mr: 1 }}
            >
              Back to History
            </Button>
            <Button
              component={Link}
              to="/upload"
              startIcon={<CloudUpload />}
              variant="contained"
            >
              New Submission
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Submission Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assessment sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">{submission.metadata.title}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Person sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                <Typography variant="body2">
                  <strong>Student:</strong> {submission.student_name}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CalendarToday sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                <Typography variant="body2">
                  <strong>Submitted:</strong> {formatDate(submission.metadata.submission_date)}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                <strong>Type:</strong>{' '}
                <Chip
                  label={submission.submission_type.toUpperCase()}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Files:</strong> {submission.files.length} file(s)
              </Typography>
              {submission.metadata.programming_languages && (
                <Typography variant="body2" gutterBottom>
                  <strong>Languages:</strong> {submission.metadata.programming_languages.join(', ')}
                </Typography>
              )}
              {submission.metadata.tags && submission.metadata.tags.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  {submission.metadata.tags.map((tag, idx) => (
                    <Chip key={idx} label={tag} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </Box>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Code Analysis Results */}
      {codeAnalysis && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Code sx={{ mr: 1, color: 'primary.main', fontSize: 32 }} />
              <Typography variant="h5">Code Quality Analysis</Typography>
            </Box>

            {/* Overall Score */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'success.light' }}>
                  <Typography variant="h3" color="success.dark">
                    {codeAnalysis.average_overall_score.toFixed(1)}
                  </Typography>
                  <Typography variant="body1" color="success.dark">
                    Overall Score / 100
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={8}>
                <Typography variant="body1" paragraph>
                  Your submission has been analyzed for code quality, complexity, style, and security.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {codeAnalysis.total_files_analyzed} file(s) analyzed on {formatDate(codeAnalysis.analysis_date)}
                </Typography>
              </Grid>
            </Grid>

            {/* File Reports */}
            {codeAnalysis.file_reports.map((fileReport, idx) => (
              <Accordion key={idx} sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
                    <Typography><strong>{fileReport.file_name}</strong></Typography>
                    <Box sx={{ display: 'flex', gap: 1, mr: 2 }}>
                      {fileReport.quality_score?.grade && (
                        <Chip
                          label={`Grade: ${fileReport.quality_score.grade}`}
                          color={getGradeColor(fileReport.quality_score.grade)}
                          size="small"
                        />
                      )}
                      <Chip
                        label={`${fileReport.overall_score?.toFixed(1) || 0}/100`}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {/* Metrics */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        📊 Code Metrics
                      </Typography>
                      <List dense>
                        <ListItem>
                          <ListItemText
                            primary="Lines of Code"
                            secondary={fileReport.metrics?.lines_of_code || 'N/A'}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Cyclomatic Complexity"
                            secondary={fileReport.metrics?.cyclomatic_complexity || 'N/A'}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Maintainability Index"
                            secondary={fileReport.metrics?.maintainability_index 
                              ? `${fileReport.metrics.maintainability_index.toFixed(1)}/100`
                              : 'N/A'
                            }
                          />
                        </ListItem>
                      </List>
                    </Grid>

                    {/* Issues */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        ⚠️ Issues Found
                      </Typography>
                      {fileReport.style_issues?.length > 0 && (
                        <Alert severity="warning" sx={{ mb: 1 }}>
                          <Typography variant="body2">
                            <strong>{fileReport.style_issues.length} Style Issue(s)</strong>
                          </Typography>
                          {fileReport.style_issues.slice(0, 3).map((issue, i) => (
                            <Typography key={i} variant="caption" display="block">
                              Line {issue.line_number}: {issue.message}
                            </Typography>
                          ))}
                        </Alert>
                      )}
                      {fileReport.security_issues?.length > 0 && (
                        <Alert severity="error" sx={{ mb: 1 }}>
                          <Typography variant="body2">
                            <strong>{fileReport.security_issues.length} Security Issue(s)</strong>
                          </Typography>
                          {fileReport.security_issues.slice(0, 3).map((issue, i) => (
                            <Typography key={i} variant="caption" display="block">
                              Line {issue.line_number}: {issue.description}
                            </Typography>
                          ))}
                        </Alert>
                      )}
                      {(!fileReport.style_issues || fileReport.style_issues.length === 0) && 
                       (!fileReport.security_issues || fileReport.security_issues.length === 0) && (
                        <Alert severity="success">
                          <Typography variant="body2">No issues found! ✨</Typography>
                        </Alert>
                      )}
                    </Grid>

                    {/* AI Feedback */}
                    {fileReport.ai_feedback && (
                      <Grid item xs={12}>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="subtitle2" gutterBottom>
                          🤖 AI Feedback
                        </Typography>
                        <Typography variant="body2" paragraph>
                          {fileReport.ai_feedback.summary || 'No summary available'}
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" display="block" color="success.main">
                              <strong>Strengths:</strong>
                            </Typography>
                            <List dense>
                              {fileReport.ai_feedback.strengths?.map((strength, i) => (
                                <ListItem key={i}>
                                  <ListItemText
                                    primary={<Typography variant="caption">• {strength}</Typography>}
                                  />
                                </ListItem>
                              )) || <Typography variant="caption">No strengths listed</Typography>}
                            </List>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="caption" display="block" color="warning.main">
                              <strong>Improvements:</strong>
                            </Typography>
                            <List dense>
                              {fileReport.ai_feedback.improvements?.map((improvement, i) => (
                                <ListItem key={i}>
                                  <ListItemText
                                    primary={<Typography variant="caption">• {improvement}</Typography>}
                                  />
                                </ListItem>
                              )) || <Typography variant="caption">No improvements suggested</Typography>}
                            </List>
                          </Grid>
                        </Grid>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Plagiarism Report */}
      {plagiarismReport && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Security sx={{ mr: 1, color: 'primary.main', fontSize: 32 }} />
              <Typography variant="h5">Plagiarism Detection</Typography>
            </Box>

            {/* Originality Score */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <Paper
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    bgcolor: plagiarismReport.overall_originality_score >= 80 ? 'success.light' : 
                             plagiarismReport.overall_originality_score >= 60 ? 'warning.light' : 'error.light'
                  }}
                >
                  <Typography
                    variant="h3"
                    color={plagiarismReport.overall_originality_score >= 80 ? 'success.dark' : 
                           plagiarismReport.overall_originality_score >= 60 ? 'warning.dark' : 'error.dark'}
                  >
                    {plagiarismReport.overall_originality_score.toFixed(1)}%
                  </Typography>
                  <Typography
                    variant="body1"
                    color={plagiarismReport.overall_originality_score >= 80 ? 'success.dark' : 
                           plagiarismReport.overall_originality_score >= 60 ? 'warning.dark' : 'error.dark'}
                  >
                    Originality Score
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={8}>
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={`Risk Level: ${plagiarismReport.risk_level.toUpperCase()}`}
                    color={getRiskColor(plagiarismReport.risk_level)}
                    icon={
                      plagiarismReport.risk_level === 'low' ? <CheckCircle /> :
                      plagiarismReport.risk_level === 'medium' ? <Warning /> : <Error />
                    }
                  />
                </Box>
                <Typography variant="body1" paragraph>
                  Your submission was checked against {plagiarismReport.sources_checked} source(s).
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {plagiarismReport.total_matches_found} potential match(es) found
                  {plagiarismReport.analysis_timestamp && ` • Checked on ${formatDate(plagiarismReport.analysis_timestamp)}`}
                  {plagiarismReport.check_date && ` • Checked on ${formatDate(plagiarismReport.check_date)}`}
                </Typography>
              </Grid>
            </Grid>

            {/* Matches */}
            {plagiarismReport.total_matches_found > 0 && plagiarismReport.similarity_matches && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Similarity Matches
                </Typography>
                {plagiarismReport.similarity_matches.map((match: any, idx: number) => (
                  <Accordion key={idx} sx={{ mb: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
                        <Typography>
                          <strong>
                            {match.match_type === 'ai_generated' ? '🤖 AI-Generated Code' : 
                             match.match_type === 'internal_copy' ? '📁 Internal Copy' : 
                             'Similar Content'}
                          </strong> - {match.student_name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mr: 2 }}>
                          <Chip
                            label={`${match.similarity_percentage.toFixed(1)}% Similar`}
                            color={match.similarity_percentage >= 80 ? 'error' : match.similarity_percentage >= 60 ? 'warning' : 'info'}
                            size="small"
                          />
                          {match.flagged && (
                            <Chip label="FLAGGED" color="error" size="small" />
                          )}
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          <strong>Match Type:</strong> {match.match_type}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          <strong>Confidence:</strong> {(match.confidence * 100).toFixed(1)}%
                        </Typography>
                        
                        {match.matching_sections && match.matching_sections.length > 0 && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="body2" gutterBottom>
                              <strong>Matching Sections:</strong>
                            </Typography>
                            {match.matching_sections.map((section: any, sIdx: number) => (
                              <Paper key={sIdx} sx={{ p: 1, mb: 1, bgcolor: 'grey.50' }}>
                                <Typography variant="caption" display="block">
                                  {typeof section === 'string' ? section : section.source_text || section.text || JSON.stringify(section).substring(0, 200)}
                                </Typography>
                              </Paper>
                            ))}
                          </Box>
                        )}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            )}

            {/* Recommendations */}
            {plagiarismReport.recommendations && plagiarismReport.recommendations.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Recommendations
                </Typography>
                <Box sx={{ 
                  bgcolor: 'grey.50', 
                  p: 3, 
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'grey.200'
                }}>
                  {plagiarismReport.recommendations.map((rec, idx) => (
                    <Typography 
                      key={idx}
                      variant="body2" 
                      sx={{ 
                        mb: idx < plagiarismReport.recommendations.length - 1 ? 1.5 : 0,
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                        lineHeight: 1.6
                      }}
                    >
                      {rec}
                    </Typography>
                  ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* No Reports Yet */}
      {!codeAnalysis && !plagiarismReport && (
        <Alert severity="info">
          <Typography variant="body1">
            Analysis reports are not yet available. They may still be processing.
          </Typography>
        </Alert>
      )}
    </Container>
  );
};

export default ResultsPageNew;
