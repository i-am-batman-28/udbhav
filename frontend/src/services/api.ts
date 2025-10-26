import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface UploadResponse {
  message: string;
  upload_id: string;
  files_count: number;
  metadata: {
    upload_id: string;
    student_name: string;
    exam_id: string;
    paper_number?: string;
    upload_timestamp: string;
    files: Array<{
      original_name: string;
      saved_name: string;
      file_path: string;
      file_size: number;
      content_type: string;
    }>;
    status: string;
    processed: boolean;
  };
}

export interface ProcessingResponse {
  message: string;
  upload_id: string;
  student_name: string;
  processed_files: Array<{
    file_name: string;
    extracted_text: string;
    text_length: number;
  }>;
  evaluation: {
    total_marks: number;
    possible_marks: number;
    percentage: number;
    overall_feedback: string;
  };
  detailed_results: any;
}

export interface UploadSession {
  upload_id: string;
  student_name: string;
  exam_id: string;
  upload_timestamp: string;
  status: string;
  processed: boolean;
  files_count: number;
}

export interface EvaluationResults {
  upload_id: string;
  student_info: {
    name: string;
    exam_id: string;
    paper_number?: string;
  };
  processing_info: {
    upload_timestamp: string;
    processing_timestamp: string;
    files_count: number;
  };
  evaluation_results: any;
}

export interface BatchUploadResponse {
  message: string;
  batch_id: string;
  total_students: number;
  uploaded_sessions: Array<{
    upload_id: string;
    student_name: string;
    files_count: number;
  }>;
}

export interface BatchProcessingResponse {
  message: string;
  batch_id: string;
  statistics: {
    total_students: number;
    successful: number;
    failed: number;
    average_percentage: number;
    total_marks_awarded: number;
    total_possible_marks: number;
  };
  results: Array<{
    upload_id: string;
    student_name: string;
    status: 'success' | 'error';
    evaluation?: {
      total_marks: number;
      possible_marks: number;
      percentage: number;
      overall_feedback: string;
    };
    error?: string;
  }>;
}

export interface BatchResults {
  batch_id: string;
  batch_info: {
    exam_id: string;
    paper_number?: string;
    total_students: number;
  };
  processing_info: {
    upload_timestamp: string;
    processing_timestamp: string;
  };
  statistics: {
    total_students: number;
    successful: number;
    failed: number;
    average_percentage: number;
    total_marks_awarded: number;
    total_possible_marks: number;
  };
  results: Array<{
    upload_id: string;
    student_name: string;
    status: 'success' | 'error';
    evaluation?: {
      total_marks: number;
      possible_marks: number;
      percentage: number;
      overall_feedback: string;
    };
    error?: string;
  }>;
}

// ============================================================================
// PEER REVIEW PLATFORM INTERFACES
// ============================================================================

export interface SubmissionUploadResponse {
  success: boolean;
  submission_id: string;
  files_uploaded: number;
  message: string;
}

export interface Submission {
  submission_id: string;
  student_id: string;
  student_name: string;
  student_email: string;
  submission_type: 'code' | 'writeup' | 'mixed';
  files: Array<{
    file_id: string;
    original_name: string;
    file_path: string;
    file_size: number;
    file_type: string;
  }>;
  metadata: {
    title: string;
    description: string;
    tags: string[];
    programming_languages?: string[];
    total_files: number;
    total_size: number;
    submission_date: string;
  };
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CodeAnalysisReport {
  submission_id: string;
  analysis_date: string;
  total_files_analyzed: number;
  average_overall_score: number;
  file_reports: Array<{
    file_id: string;
    file_name: string;
    language: string;
    overall_score: number;
    quality_score: {
      grade: string;
      score: number;
      category: string;
    };
    metrics: {
      lines_of_code: number;
      cyclomatic_complexity: number;
      maintainability_index: number;
    };
    style_issues: Array<{
      type: string;
      severity: string;
      message: string;
      line_number: number;
    }>;
    security_issues: Array<{
      type: string;
      severity: string;
      description: string;
      line_number: number;
    }>;
    ai_feedback?: {
      summary: string;
      strengths: string[];
      improvements: string[];
      code_quality_rating: number;
    };
  }>;
}

export interface PlagiarismReport {
  submission_id: string;
  student_name: string;
  submission_type: string;
  check_date?: string;
  analysis_timestamp?: string;
  overall_originality_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  total_matches_found: number;
  sources_checked: number;
  similarity_matches?: Array<{
    submission_id: string;
    student_name: string;
    similarity_percentage: number;
    matching_sections: any[];
    match_type: string;
    confidence: number;
    flagged: boolean;
  }>;
  flagged_sections?: any[];
  recommendations: string[];
}

export interface StudentDashboard {
  student_id: string;
  student_name: string;
  total_submissions: number;
  submissions_under_review: number;
  submissions_completed: number;
  submissions_flagged: number;
  average_code_quality_score: number;
  average_originality_score: number;
  recent_submissions: Submission[];
}

class ApiService {
  private api = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    timeout: 120000, // Increased to 2 minutes for AI evaluation processing
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Upload answer sheet files
  async uploadAnswerSheet(
    files: File[],
    studentName: string,
    examId: string,
    paperNumber?: string
  ): Promise<UploadResponse> {
    const formData = new FormData();
    
    // Add files
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    // Add form fields
    formData.append('student_name', studentName);
    formData.append('exam_id', examId);
    if (paperNumber) {
      formData.append('paper_number', paperNumber);
    }

    const response = await this.api.post('/upload/answer-sheet', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Process uploaded answer sheet
  async processAnswerSheet(uploadId: string): Promise<ProcessingResponse> {
    const response = await this.api.post(`/process/answer-sheet/${uploadId}`);
    return response.data;
  }

  // Get evaluation results
  async getEvaluationResults(uploadId: string): Promise<EvaluationResults> {
    const response = await this.api.get(`/results/${uploadId}`);
    return response.data;
  }

  // List all uploads
  async listUploads(): Promise<{ uploads: UploadSession[]; total_count: number }> {
    const response = await this.api.get('/uploads');
    return response.data;
  }

  // Get available question papers
  async getQuestionPapers(): Promise<any> {
    const response = await this.api.get('/papers');
    return response.data;
  }

  // Get system status
  async getSystemStatus(): Promise<any> {
    const response = await this.api.get('/status');
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  }

  // Upload multiple answer sheets (batch upload)
  async uploadMultipleAnswerSheets(formData: FormData): Promise<BatchUploadResponse> {
    const response = await this.api.post('/upload/multiple-answer-sheets', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Process batch answer sheets
  async processBatchAnswerSheets(batchId: string): Promise<BatchProcessingResponse> {
    const response = await this.api.post(`/process/batch/${batchId}`);
    return response.data;
  }

  // Get batch evaluation results
  async getBatchEvaluationResults(batchId: string): Promise<BatchResults> {
    const response = await this.api.get(`/batch/results/${batchId}`);
    return response.data;
  }

  // ============================================================================
  // PEER REVIEW PLATFORM METHODS
  // ============================================================================

  // Upload submission (code or writeup)
  async uploadSubmission(
    files: File[],
    studentId: string,
    studentName: string,
    studentEmail: string,
    submissionType: 'code' | 'writeup' | 'mixed',
    title: string,
    description: string,
    tags?: string[],
    programmingLanguages?: string[]
  ): Promise<SubmissionUploadResponse> {
    const formData = new FormData();
    
    // Add files
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    // Add form fields
    formData.append('student_id', studentId);
    formData.append('student_name', studentName);
    formData.append('student_email', studentEmail);
    formData.append('submission_type', submissionType);
    formData.append('title', title);
    formData.append('description', description);
    
    if (tags && tags.length > 0) {
      formData.append('tags', tags.join(','));
    }
    
    if (programmingLanguages && programmingLanguages.length > 0) {
      formData.append('programming_languages', programmingLanguages.join(','));
    }

    const response = await this.api.post('/peer-review/submissions/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Get submission details
  async getSubmission(submissionId: string): Promise<{ submission: Submission; has_plagiarism_report: boolean; has_code_analysis: boolean }> {
    const response = await this.api.get(`/peer-review/submissions/${submissionId}`);
    return response.data;
  }

  // Get all submissions for a student
  async getStudentSubmissions(studentId: string): Promise<Submission[]> {
    const response = await this.api.get(`/peer-review/submissions/student/${studentId}`);
    return response.data;
  }

  // Analyze code quality
  async analyzeCode(submissionId: string, includeAiFeedback: boolean = false): Promise<{ success: boolean; report: CodeAnalysisReport }> {
    const response = await this.api.post(
      `/peer-review/submissions/${submissionId}/analyze-code`,
      null,
      { params: { include_ai_feedback: includeAiFeedback } }
    );
    return response.data;
  }

  // Check plagiarism
  async checkPlagiarism(submissionId: string, checkLimit: number = 10): Promise<{ success: boolean; report: PlagiarismReport }> {
    const response = await this.api.post(
      `/peer-review/submissions/${submissionId}/check-plagiarism`,
      null,
      { params: { check_limit: checkLimit } }
    );
    return response.data;
  }

  // Analyze both code and plagiarism
  async analyzeAll(submissionId: string, includeAiFeedback: boolean = false, checkLimit: number = 10): Promise<{
    success: boolean;
    code_analysis: CodeAnalysisReport;
    plagiarism_report: PlagiarismReport;
  }> {
    const response = await this.api.post(
      `/peer-review/submissions/${submissionId}/analyze-all`,
      null,
      { params: { include_ai_feedback: includeAiFeedback, check_limit: checkLimit } }
    );
    return response.data;
  }

  // Get code analysis report
  async getCodeAnalysisReport(submissionId: string): Promise<CodeAnalysisReport> {
    const response = await this.api.get(`/peer-review/submissions/${submissionId}/code-analysis`);
    return response.data;
  }

  // Get plagiarism report
  async getPlagiarismReport(submissionId: string): Promise<PlagiarismReport> {
    const response = await this.api.get(`/peer-review/submissions/${submissionId}/plagiarism-report`);
    return response.data;
  }

  // Get student dashboard
  async getStudentDashboard(studentId: string): Promise<StudentDashboard> {
    const response = await this.api.get(`/peer-review/dashboard/student/${studentId}`);
    return response.data;
  }

  // Get system statistics
  async getSystemStats(): Promise<any> {
    const response = await this.api.get('/peer-review/stats/overview');
    return response.data;
  }

  // Delete submission
  async deleteSubmission(submissionId: string): Promise<{ success: boolean; message: string }> {
    const response = await this.api.delete(`/peer-review/submissions/${submissionId}`);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
