import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Divider,
} from '@mui/material';
import aiService, { ParaphraseRequest } from '../services/aiService';

interface ParaphraserModalProps {
  open: boolean;
  onClose: () => void;
  initialText: string;
}

const ParaphraserModal: React.FC<ParaphraserModalProps> = ({
  open,
  onClose,
  initialText,
}) => {
  const [text, setText] = useState(initialText);
  const [style, setStyle] = useState<'academic' | 'casual' | 'formal' | 'simple'>('academic');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleParaphrase = async () => {
    if (!text.trim() || text.length < 20) {
      setError('Please enter at least 20 characters');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await aiService.paraphrase({ text, style });
      
      if (response.success && response.data) {
        setResult(response.data);
      } else {
        setError(response.error || 'Failed to paraphrase text');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (result && result.paraphrased) {
      // Copy to clipboard
      navigator.clipboard.writeText(result.paraphrased);
      alert('Paraphrased text copied to clipboard!');
    }
  };

  const handleReset = () => {
    setText(initialText);
    setResult(null);
    setError(null);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Paraphraser</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            label="Original Text"
            multiline
            rows={6}
            fullWidth
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to paraphrase (minimum 20 characters)"
          />

          <FormControl fullWidth>
            <InputLabel>Style</InputLabel>
            <Select
              value={style}
              label="Style"
              onChange={(e) => setStyle(e.target.value as any)}
            >
              <MenuItem value="academic">Academic</MenuItem>
              <MenuItem value="casual">Casual</MenuItem>
              <MenuItem value="formal">Formal</MenuItem>
              <MenuItem value="simple">Simple</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleParaphrase}
            disabled={loading || !text.trim() || text.length < 20}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : 'Paraphrase Text'}
          </Button>

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {result && (
            <Paper elevation={2} sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                Paraphrased Result
              </Typography>
              <Typography variant="body1" paragraph>
                {result.paraphrased}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Original Words
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {result.word_count_original}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Paraphrased Words
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {result.word_count_paraphrased}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Style Applied
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {result.style_applied}
                  </Typography>
                </Box>
              </Box>

              {result.changes_summary && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  {result.changes_summary}
                </Alert>
              )}
            </Paper>
          )}
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleReset} disabled={loading}>
          Reset
        </Button>
        <Button onClick={onClose} disabled={loading}>
          Close
        </Button>
        <Button
          variant="contained"
          onClick={handleApply}
          disabled={!result || loading}
        >
          Copy to Clipboard
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ParaphraserModal;
