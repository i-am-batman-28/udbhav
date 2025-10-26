import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Divider,
  Paper,
} from '@mui/material';
import {
  CheckCircle,
  Home,
  CloudUpload,
  Download,
} from '@mui/icons-material';

interface AIToolsResults {
  paraphraser?: {
    success: boolean;
    original: string;
    paraphrased: string;
    style_applied: string;
    changes_summary?: string;
  };
  grammar?: {
    success: boolean;
    original: string;
    corrected: string;
    error_count: number;
    overall_quality: string;
  };
  humanizer?: {
    success: boolean;
    original: string;
    humanized: string;
    ai_score_before: number;
    ai_score_after: number;
    changes_made?: string[];
  };
  ai_detector?: {
    is_ai_generated: boolean;
    confidence: number;
    confidence_level: string;
    explanation: string;
  };
  plagiarism_quick?: {
    originality_score: number;
    ai_confidence: number;
    summary: string;
  };
  plagiarism?: {
    success: boolean;
    overall_originality_score: number;
    total_matches_found: number;
    similarity_matches: Array<{
      source: string;
      similarity_score: number;
      matched_content: string;
    }>;
    flagged_sections: Array<{
      section: string;
      reason: string;
    }>;
    risk_level: string;
    recommendations: string[];
    sources_checked: number;
    note?: string;
  };
}

const AIToolsResultsPage: React.FC = () => {
  const { uploadId } = useParams<{ uploadId: string }>();
  const [aiToolsResults, setAiToolsResults] = useState<AIToolsResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (uploadId) {
      fetchAIToolsResults(uploadId);
    }
  }, [uploadId]);

  const fetchAIToolsResults = async (id: string) => {
    try {
      setLoading(true);
      const url = `http://localhost:8000/api/v1/peer-review/submissions/${id}/ai-tools-results`;
      const response = await fetch(url);
      
      if (response.ok) {
        const data = await response.json();
        setAiToolsResults(data);
      } else {
        setError('AI tools results not found. Please run the analysis first.');
      }
    } catch (err: any) {
      setError('Failed to load AI tools results: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadResults = (toolName: string, content: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${toolName}_results.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading AI tools results...
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

  if (!aiToolsResults || Object.keys(aiToolsResults).length === 0) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="info">
          No AI tools results found for this submission.
        </Alert>
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button component={Link} to="/" variant="outlined" sx={{ mr: 2 }}>
            Home
          </Button>
          <Button component={Link} to="/upload" variant="contained">
            Upload Another
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 2 }}>
          AI Writing Assistance Results
        </Typography>
        <Chip
          icon={<CheckCircle />}
          label="Analysis Complete"
          color="success"
          size="medium"
        />
      </Box>

      {/* Grammar Checker Results */}
      {aiToolsResults.grammar && aiToolsResults.grammar.success && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" color="primary">
                📝 Grammar Checker
              </Typography>
              <Button
                size="small"
                startIcon={<Download />}
                onClick={() => downloadResults('grammar', aiToolsResults.grammar!.corrected)}
              >
                Download
              </Button>
            </Box>

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                Original Text:
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto', p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2" component="div">
                  {aiToolsResults.grammar.original}
                </Typography>
              </Box>
            </Paper>

            <Divider sx={{ my: 2 }} />

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'success.50', mb: 2 }}>
              <Typography variant="subtitle2" color="success.dark" sx={{ mb: 1 }}>
                Corrected Text:
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto', p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2" component="div">
                  {aiToolsResults.grammar.corrected}
                </Typography>
              </Box>
            </Paper>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Chip 
                label={`${aiToolsResults.grammar.error_count} errors found`} 
                color={aiToolsResults.grammar.error_count === 0 ? 'success' : 'warning'} 
                size="small" 
              />
              <Chip 
                label={`Quality: ${aiToolsResults.grammar.overall_quality}`} 
                color="info" 
                size="small" 
              />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Paraphraser Results */}
      {aiToolsResults.paraphraser && aiToolsResults.paraphraser.success && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" color="primary">
                ✍️ Paraphraser
              </Typography>
              <Button
                size="small"
                startIcon={<Download />}
                onClick={() => downloadResults('paraphraser', aiToolsResults.paraphraser!.paraphrased)}
              >
                Download
              </Button>
            </Box>

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                Original Text:
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto', p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2" component="div">
                  {aiToolsResults.paraphraser.original}
                </Typography>
              </Box>
            </Paper>

            <Divider sx={{ my: 2 }} />

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'primary.50', mb: 2 }}>
              <Typography variant="subtitle2" color="primary.dark" sx={{ mb: 1 }}>
                Paraphrased Text ({aiToolsResults.paraphraser.style_applied} style):
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto', p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2" component="div">
                  {aiToolsResults.paraphraser.paraphrased}
                </Typography>
              </Box>
            </Paper>

            {aiToolsResults.paraphraser.changes_summary && (
              <Alert severity="info" sx={{ mt: 2 }}>
                {aiToolsResults.paraphraser.changes_summary}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* AI Humanizer Results */}
      {aiToolsResults.humanizer && aiToolsResults.humanizer.success && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" color="primary">
                👤 AI Humanizer
              </Typography>
              <Button
                size="small"
                startIcon={<Download />}
                onClick={() => downloadResults('humanizer', aiToolsResults.humanizer!.humanized)}
              >
                Download
              </Button>
            </Box>

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                Original Text (AI Score: {aiToolsResults.humanizer.ai_score_before}%):
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto', p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2" component="div">
                  {aiToolsResults.humanizer.original}
                </Typography>
              </Box>
            </Paper>

            <Divider sx={{ my: 2 }} />

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'success.50', mb: 2 }}>
              <Typography variant="subtitle2" color="success.dark" sx={{ mb: 1 }}>
                Humanized Text (AI Score: {aiToolsResults.humanizer.ai_score_after}%):
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto', p: 1, bgcolor: 'white', borderRadius: 1 }}>
                <Typography variant="body2" component="div">
                  {aiToolsResults.humanizer.humanized}
                </Typography>
              </Box>
            </Paper>

            {aiToolsResults.humanizer.changes_made && aiToolsResults.humanizer.changes_made.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Changes Made:
                </Typography>
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  {aiToolsResults.humanizer.changes_made.map((change: string, idx: number) => (
                    <Typography key={idx} variant="body2" sx={{ mb: 0.5 }}>
                      • {change}
                    </Typography>
                  ))}
                </Paper>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* AI Detector Results */}
      {aiToolsResults.ai_detector && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
              🤖 AI Detector
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip 
                label={aiToolsResults.ai_detector.is_ai_generated ? 'AI Generated' : 'Human Written'} 
                color={aiToolsResults.ai_detector.is_ai_generated ? 'error' : 'success'}
              />
              <Chip 
                label={`${aiToolsResults.ai_detector.confidence}% Confidence`} 
                color={aiToolsResults.ai_detector.confidence_level === 'high' ? 'error' : 'warning'}
              />
            </Box>

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="body2">
                {aiToolsResults.ai_detector.explanation}
              </Typography>
            </Paper>
          </CardContent>
        </Card>
      )}

      {/* Full Plagiarism Check Results */}
      {aiToolsResults.plagiarism && aiToolsResults.plagiarism.success && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" color="primary" sx={{ mb: 3 }}>
              📋 Detailed Plagiarism Check
            </Typography>

            {/* Summary Stats - Clean Design */}
            <Box sx={{ mb: 3 }}>
              <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2 }}>
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 3 }}>
                  {/* Originality Score */}
                  <Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      Originality Score
                    </Typography>
                    <Typography variant="h5" fontWeight="600" color={
                      (aiToolsResults.plagiarism.overall_originality_score || 0) >= 80 ? 'success.main' : 
                      (aiToolsResults.plagiarism.overall_originality_score || 0) >= 60 ? 'warning.main' : 'error.main'
                    }>
                      {aiToolsResults.plagiarism.overall_originality_score || 0}%
                    </Typography>
                  </Box>

                  {/* Matches Found */}
                  <Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      Matches Found
                    </Typography>
                    <Typography variant="h5" fontWeight="600" color="text.primary">
                      {aiToolsResults.plagiarism.total_matches_found || 0}
                    </Typography>
                  </Box>

                  {/* Risk Level */}
                  <Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      Risk Level
                    </Typography>
                    <Typography variant="h5" fontWeight="600" sx={{ textTransform: 'capitalize' }} color={
                      (aiToolsResults.plagiarism.risk_level || 'unknown') === 'low' ? 'success.main' : 
                      (aiToolsResults.plagiarism.risk_level || 'unknown') === 'medium' ? 'warning.main' : 'error.main'
                    }>
                      {aiToolsResults.plagiarism.risk_level || 'Unknown'}
                    </Typography>
                  </Box>

                  {/* Sources Checked */}
                  <Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      Sources Checked
                    </Typography>
                    <Typography variant="h5" fontWeight="600" color="text.primary">
                      {aiToolsResults.plagiarism.sources_checked || 0}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Box>

            {/* Similarity Matches */}
            {aiToolsResults.plagiarism.similarity_matches && aiToolsResults.plagiarism.similarity_matches.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" sx={{ mb: 2 }}>
                  Similarity Matches
                </Typography>
                {aiToolsResults.plagiarism.similarity_matches.map((match, idx) => (
                  <Paper key={idx} elevation={0} sx={{ p: 2, mb: 2, bgcolor: 'grey.50', border: '1px solid', borderColor: 'grey.300', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" fontWeight="500" color="text.primary">
                        {match.source}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {match.similarity_score}% Similar
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary', pl: 1, borderLeft: '3px solid', borderColor: 'grey.400' }}>
                      "{match.matched_content}"
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}

            {/* Flagged Sections */}
            {aiToolsResults.plagiarism.flagged_sections && aiToolsResults.plagiarism.flagged_sections.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" sx={{ mb: 2 }}>
                  Flagged Sections
                </Typography>
                {aiToolsResults.plagiarism.flagged_sections.map((section, idx) => (
                  <Paper key={idx} elevation={0} sx={{ p: 2, mb: 1, bgcolor: 'grey.50', border: '1px solid', borderColor: 'grey.300', borderRadius: 2 }}>
                    <Typography variant="body2" fontWeight="500" sx={{ mb: 0.5 }}>
                      {section.section}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {section.reason}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}

            {/* Recommendations */}
            {aiToolsResults.plagiarism.recommendations && aiToolsResults.plagiarism.recommendations.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" fontWeight="600" sx={{ mb: 2 }}>
                  Recommendations
                </Typography>
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                  {aiToolsResults.plagiarism.recommendations.map((rec, idx, arr) => (
                    <Typography key={idx} variant="body2" sx={{ mb: idx < arr.length - 1 ? 1.5 : 0, color: 'text.secondary' }}>
                      • {rec}
                    </Typography>
                  ))}
                </Paper>
              </Box>
            )}

            {/* Note if fallback was used */}
            {aiToolsResults.plagiarism.note && (
              <Paper elevation={0} sx={{ p: 2, bgcolor: 'info.50', borderRadius: 2, border: '1px solid', borderColor: 'info.light' }}>
                <Typography variant="body2" color="info.dark">
                  ℹ️ {aiToolsResults.plagiarism.note}
                </Typography>
              </Paper>
            )}
          </CardContent>
        </Card>
      )}

      {/* Quick Plagiarism Check Results (fallback) */}
      {aiToolsResults.plagiarism_quick && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
              📋 Quick Plagiarism Check
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip 
                label={`${aiToolsResults.plagiarism_quick.originality_score}% Original`} 
                color={aiToolsResults.plagiarism_quick.originality_score >= 80 ? 'success' : 'warning'}
              />
              <Chip 
                label={`${aiToolsResults.plagiarism_quick.ai_confidence}% AI Detected`} 
                color="info"
              />
            </Box>

            <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="body2">
                {aiToolsResults.plagiarism_quick.summary}
              </Typography>
            </Paper>
          </CardContent>
        </Card>
      )}

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
};

export default AIToolsResultsPage;
