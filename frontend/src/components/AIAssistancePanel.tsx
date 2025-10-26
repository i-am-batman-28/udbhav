import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Button,
  Divider,
  Alert,
} from '@mui/material';
import {
  AutoFixHigh,
  Spellcheck,
  Psychology,
  ContentCopy,
  EmojiObjects,
} from '@mui/icons-material';

interface AITool {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
}

interface AIAssistancePanelProps {
  fileType: 'code' | 'text' | 'none';
  disabled?: boolean;
  selectedTools: string[];
  onToolClick: (toolId: string) => void;
}

const AIAssistancePanel: React.FC<AIAssistancePanelProps> = ({ 
  fileType, 
  disabled = false,
  selectedTools,
  onToolClick 
}) => {
  // Define all AI tools with their metadata
  const allTools: AITool[] = [
    {
      id: 'paraphraser',
      name: 'Paraphraser',
      description: 'Rewrite text while maintaining its original meaning',
      icon: <AutoFixHigh />,
    },
    {
      id: 'grammar',
      name: 'Grammar Checker',
      description: 'Check and fix grammatical errors and punctuation',
      icon: <Spellcheck />,
    },
    {
      id: 'ai-detector',
      name: 'AI Detector',
      description: 'Detect AI-generated content with confidence scores',
      icon: <Psychology />,
    },
    {
      id: 'plagiarism',
      name: 'Plagiarism Checker',
      description: 'Compare against past submissions for similarity',
      icon: <ContentCopy />,
    },
    {
      id: 'humanizer',
      name: 'AI Humanizer',
      description: 'Make AI-generated text sound more natural',
      icon: <EmojiObjects />,
    },
  ];

  // Filter tools based on file type
  const getAvailableTools = (): AITool[] => {
    if (fileType === 'none') return [];
    
    if (fileType === 'code') {
      // For code: AI Detector, Plagiarism, AI Humanizer
      return allTools.filter(tool => 
        ['ai-detector', 'plagiarism', 'humanizer'].includes(tool.id)
      );
    }
    
    // For text/PDF: All tools
    return allTools;
  };

  const availableTools = getAvailableTools();

  if (availableTools.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          AI Writing Assistance
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Enhance your submission with AI-powered tools. Select a tool to analyze your uploaded content.
        </Typography>

        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={2}>
          {availableTools.map((tool) => (
            <Grid item xs={12} sm={6} key={tool.id}>
              <Box
                sx={{
                  p: 2,
                  border: 1,
                  borderColor: 'grey.300',
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 2,
                  opacity: disabled ? 0.6 : 1,
                  backgroundColor: 'background.paper',
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minWidth: 40,
                    minHeight: 40,
                    color: 'primary.main',
                  }}
                >
                  {tool.icon}
                </Box>
                
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" fontWeight="600" gutterBottom>
                    {tool.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                    {tool.description}
                  </Typography>
                  <Button
                    size="small"
                    variant={selectedTools.includes(tool.id) ? "contained" : "outlined"}
                    onClick={() => onToolClick(tool.id)}
                    disabled={disabled}
                    fullWidth
                  >
                    {selectedTools.includes(tool.id) ? "✓ Selected" : "Select Tool"}
                  </Button>
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>

        {fileType === 'code' && (
          <Alert severity="info" sx={{ mt: 3 }}>
            For code submissions, Paraphraser and Grammar Checker are not available. 
            Use the other tools to analyze your code.
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default AIAssistancePanel;
