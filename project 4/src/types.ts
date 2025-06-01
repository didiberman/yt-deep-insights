export type AnalysisOptions = {
  transcript: boolean;
  comments: boolean;
};

export type AIModel = 'gemini' | 'nvidia';

export type InsightType = 'summary' | 'sentiment' | 'topics' | 'questions' | 'quotes';

export interface Insight {
  type: InsightType;
  title: string;
  content: string | string[];
}