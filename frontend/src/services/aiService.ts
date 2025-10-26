import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/ai-tools';

export interface ParaphraseRequest {
  text: string;
  style: 'academic' | 'casual' | 'formal' | 'simple';
}

export interface GrammarCheckRequest {
  text: string;
}

export interface HumanizeRequest {
  text: string;
  tone: 'casual' | 'professional' | 'friendly';
}

export interface AIDetectionRequest {
  text: string;
  submission_type: 'writeup' | 'code';
}

export interface ParaphraseResponse {
  success: boolean;
  data: {
    success: boolean;
    original: string;
    paraphrased: string;
    changes_summary: string;
    style_applied: string;
    word_count_original: number;
    word_count_paraphrased: number;
  };
  error?: string;
}

export interface GrammarCheckResponse {
  success: boolean;
  data: {
    success: boolean;
    original: string;
    corrected: string;
    errors_found: number;
    error_count: number;
    corrections: Array<{
      line: number;
      original: string;
      correction: string;
      type: string;
    }>;
    overall_quality: string;
  };
  error?: string;
}

export interface HumanizeResponse {
  success: boolean;
  data: {
    success: boolean;
    original: string;
    humanized: string;
    ai_score_before: number;
    ai_score_after: number;
    original_ai_score: number;
    humanized_ai_score: number;
    changes_made: string[];
    tone_applied: string;
  };
  error?: string;
}

export interface AIDetectionResponse {
  success: boolean;
  data: {
    is_ai_generated: boolean;
    confidence: number;
    confidence_level: string;
    evidence: string[];
    ai_tool_signature: string;
    explanation: string;
    submission_type: string;
  };
  error?: string;
}

export interface PlagiarismCheckResponse {
  success: boolean;
  data: {
    originality_score: number;
    ai_detected: boolean;
    ai_confidence: number;
    risk_level: string;
    summary: string;
    note: string;
  };
  error?: string;
}

const aiService = {
  async paraphrase(request: ParaphraseRequest): Promise<ParaphraseResponse> {
    const response = await axios.post<ParaphraseResponse>(
      `${API_BASE_URL}/paraphrase`,
      request
    );
    return response.data;
  },

  async checkGrammar(request: GrammarCheckRequest): Promise<GrammarCheckResponse> {
    const response = await axios.post<GrammarCheckResponse>(
      `${API_BASE_URL}/grammar-check`,
      request
    );
    return response.data;
  },

  async humanize(request: HumanizeRequest): Promise<HumanizeResponse> {
    const response = await axios.post<HumanizeResponse>(
      `${API_BASE_URL}/humanize`,
      request
    );
    return response.data;
  },

  async detectAI(request: AIDetectionRequest): Promise<AIDetectionResponse> {
    const response = await axios.post<AIDetectionResponse>(
      `${API_BASE_URL}/detect-ai`,
      request
    );
    return response.data;
  },

  async checkPlagiarism(request: AIDetectionRequest): Promise<PlagiarismCheckResponse> {
    const response = await axios.post<PlagiarismCheckResponse>(
      `${API_BASE_URL}/check-plagiarism`,
      request
    );
    return response.data;
  },

  async healthCheck(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  }
};

export default aiService;
