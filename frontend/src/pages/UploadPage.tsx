import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Delete,
  Send,
  CheckCircle,
} from '@mui/icons-material';

import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import AIAssistancePanel from '../components/AIAssistancePanel';

interface UploadedFile {
  file: File;
  preview?: string;
}

const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [submissionType, setSubmissionType] = useState<'code' | 'writeup' | 'mixed'>('code');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState('');
  const [programmingLanguages, setProgrammingLanguages] = useState('');
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedAITools, setSelectedAITools] = useState<string[]>([]);

  // Detect file type for AI tools
  const getFileTypeCategory = (): 'code' | 'text' | 'none' => {
    if (uploadedFiles.length === 0) return 'none';
    
    const codeExtensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift'];
    const textExtensions = ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'];
    
    const hasCode = uploadedFiles.some(f => 
      codeExtensions.some(ext => f.file.name.toLowerCase().endsWith(ext))
    );
    
    const hasText = uploadedFiles.some(f =>
      textExtensions.some(ext => f.file.name.toLowerCase().endsWith(ext)) ||
      f.file.type.includes('pdf') ||
      f.file.type.includes('document')
    );
    
    // If only code files, return 'code'
    if (hasCode && !hasText) return 'code';
    
    // If has text/PDF files, return 'text' (all tools available)
    if (hasText) return 'text';
    
    // Default to 'text' for mixed or unknown types
    return hasCode ? 'code' : 'text';
  };

  const handleAIToolClick = (toolId: string) => {
    // Toggle selection
    setSelectedAITools(prev => {
      if (prev.includes(toolId)) {
        // Deselect if already selected
        return prev.filter(id => id !== toolId);
      } else {
        // Add to selection
        return [...prev, toolId];
      }
    });
  };

  // Auto-populate student information from logged-in user
  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
    }));
    setUploadedFiles((prev) => [...prev, ...newFiles]);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      // Code files
      'text/x-python': ['.py'],
      'text/javascript': ['.js', '.jsx'],
      'text/x-typescript': ['.ts', '.tsx'],
      'text/x-java': ['.java'],
      'text/x-c': ['.c', '.h'],
      'text/x-c++': ['.cpp', '.hpp', '.cc', '.cxx'],
      'text/x-csharp': ['.cs'],
      'application/json': ['.json'],
      'text/html': ['.html', '.htm'],
      'text/css': ['.css', '.scss'],
      // Documents
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff', '.gif'],
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'text/csv': ['.csv'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/rtf': ['.rtf'],
    },
    multiple: true,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleSubmit = async () => {
    if (!user) {
      setError('You must be logged in to submit');
      navigate('/login');
      return;
    }

    if (!title.trim()) {
      setError('Submission title is required');
      return;
    }
    if (uploadedFiles.length === 0) {
      setError('Please upload at least one file');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      // Upload files using logged-in user's information
      const uploadResponse = await apiService.uploadSubmission(
        uploadedFiles.map((f) => f.file),
        user.student_id || user.id, // Use student_id for students, user.id for teachers
        user.name,
        user.email,
        submissionType,
        title.trim(),
        description.trim(),
        tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : undefined,
        programmingLanguages ? programmingLanguages.split(',').map(l => l.trim()).filter(Boolean) : undefined
      );

      setSuccess('Files uploaded successfully! Processing submission...');
      setProcessing(true);
      setUploading(false); // Upload is complete, now processing

      // Run analysis on the submission with selected AI tools
      await apiService.analyzeAll(uploadResponse.submission_id, false, 10, selectedAITools);

      setSuccess('Analysis completed successfully!');
      
      // Navigate to results page after a short delay
      setTimeout(() => {
        navigate(`/results/${uploadResponse.submission_id}`);
      }, 2000);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  };

  const isFormValid = user && title.trim() && uploadedFiles.length > 0;

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        Submit Your Work
      </Typography>
      <Typography variant="body1" textAlign="center" color="text.secondary" sx={{ mb: 4 }}>
        Upload your code or project writeup for automated review and feedback
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert 
          severity="success" 
          sx={{ mb: 3 }}
          icon={processing ? <CircularProgress size={20} /> : <CheckCircle />}
        >
          <Box display="flex" alignItems="center" gap={1}>
            {success}
            {processing && (
              <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                (Running code analysis and plagiarism check...)
              </Typography>
            )}
          </Box>
        </Alert>
      )}

      {/* Show logged-in user info */}
      {user && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Submitting as:</strong> {user.name} ({user.email})
            {user.student_id && ` • ID: ${user.student_id}`}
            {user.role === 'teacher' && ' • Teacher Account'}
          </Typography>
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Submission Details */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Submission Details
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Submission Type</InputLabel>
                    <Select
                      value={submissionType}
                      onChange={(e) => setSubmissionType(e.target.value as 'code' | 'writeup' | 'mixed')}
                      disabled={uploading || processing}
                    >
                      <MenuItem value="code">Code / Programming Assignment</MenuItem>
                      <MenuItem value="writeup">Project Writeup / Report</MenuItem>
                      <MenuItem value="mixed">Mixed (Code + Writeup)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Programming Languages"
                    value={programmingLanguages}
                    onChange={(e) => setProgrammingLanguages(e.target.value)}
                    disabled={uploading || processing || submissionType === 'writeup'}
                    placeholder="e.g., Python, JavaScript"
                    helperText="Comma-separated (if code submission)"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Project Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                    disabled={uploading || processing}
                    placeholder="e.g., Binary Search Tree Implementation"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    disabled={uploading || processing}
                    multiline
                    rows={3}
                    placeholder="Brief description of your submission..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Tags"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    disabled={uploading || processing}
                    placeholder="e.g., algorithms, data structures, assignment1"
                    helperText="Comma-separated tags for categorization"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* File Upload */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload Files
              </Typography>
              
              {/* Dropzone */}
              <Paper
                {...getRootProps()}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                  transition: 'all 0.3s ease',
                  mb: 3,
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <input {...getInputProps()} />
                <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  or click to browse files
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Supported: Code files (py, js, java, cpp, etc.), Documents (PDF, DOC), Images (JPG, PNG) (Max 50MB per file)
                </Typography>
              </Paper>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Uploaded Files ({uploadedFiles.length})
                  </Typography>
                  <List>
                    {uploadedFiles.map((uploadedFile, index) => (
                      <ListItem
                        key={index}
                        sx={{
                          border: 1,
                          borderColor: 'grey.200',
                          borderRadius: 1,
                          mb: 1,
                        }}
                      >
                        <ListItemIcon>
                          <InsertDriveFile color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={uploadedFile.file.name}
                          secondary={`${formatFileSize(uploadedFile.file.size)} • ${uploadedFile.file.type || 'File'}`}
                        />
                        <Chip
                          label={
                            uploadedFile.file.type.startsWith('image/') ? 'Image' :
                            uploadedFile.file.type === 'application/pdf' ? 'PDF' :
                            uploadedFile.file.name.endsWith('.py') ? 'Python' :
                            uploadedFile.file.name.endsWith('.js') ? 'JavaScript' :
                            uploadedFile.file.name.endsWith('.java') ? 'Java' :
                            'Code'
                          }
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{ mr: 1 }}
                        />
                        <Button
                          size="small"
                          color="error"
                          onClick={() => removeFile(index)}
                          disabled={uploading || processing}
                        >
                          <Delete />
                        </Button>
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* AI Assistance Panel - Shows after files are uploaded */}
        {uploadedFiles.length > 0 && (
          <Grid item xs={12}>
            <AIAssistancePanel
              fileType={getFileTypeCategory()}
              disabled={uploading || processing}
              selectedTools={selectedAITools}
              onToolClick={handleAIToolClick}
            />
          </Grid>
        )}

        {/* Submit Button */}
        <Grid item xs={12}>
          <Box sx={{ textAlign: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleSubmit}
              disabled={!isFormValid || uploading || processing}
              startIcon={
                uploading || processing ? (
                  <CircularProgress size={20} />
                ) : (
                  <Send />
                )
              }
              sx={{ px: 6, py: 1.5 }}
            >
              {processing
                ? 'AI Evaluation in Progress...'
                : uploading
                ? 'Uploading...'
                : 'Submit for Evaluation'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default UploadPage;
