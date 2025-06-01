import { Insight } from './types';

export const dummyInsights: Insight[] = [
  {
    type: 'summary',
    title: 'Summary',
    content: 'This video explores the exponential growth of AI capabilities, focusing on recent developments in large language models and their applications. The presenter discusses how models like GPT-4, Claude, and Gemini are revolutionizing content creation, coding, and knowledge work. Key points include the economic implications, ethical considerations around AI usage, and predictions about AI\'s impact on various industries in the next 3-5 years.'
  },
  {
    type: 'sentiment',
    title: 'Sentiment Analysis',
    content: 'The overall sentiment of the video is cautiously optimistic (72% positive, 18% neutral, 10% concerned). The presenter maintains an enthusiastic tone when discussing technological advancements, while acknowledging potential downsides. The comment section reflects similar sentiments, though with more polarization - strong excitement about possibilities (65%) alongside deeper concerns about job displacement (25%).'
  },
  {
    type: 'topics',
    title: 'Key Topics',
    content: [
      'Recent advancements in large language models and multimodal AI systems',
      'Economic impacts of AI automation on knowledge work industries',
      'Ethical considerations around AI usage and potential regulations',
      'Practical applications of AI in content creation, programming, and research',
      'Future predictions about AI integration in daily life (2025-2030)'
    ]
  },
  {
    type: 'questions',
    title: 'Common Questions',
    content: [
      'How will AI impact employment in creative and knowledge work fields?',
      'What safeguards are being implemented to prevent AI misuse?',
      'How can individuals prepare for an increasingly AI-integrated workplace?',
      'Will AI capabilities continue to grow exponentially or hit plateaus?',
      'How are companies implementing AI tools into their existing workflows?'
    ]
  },
  {
    type: 'quotes',
    title: 'Notable Quotes',
    content: [
      `We're seeing capabilities emerge that weren't explicitly programmed - this emergent behavior is both fascinating and concerning.`,
      `The gap between what was impossible and what's now trivial has collapsed in just 18 months.`,
      `AI won't replace humans, but humans using AI will replace those who don't.`,
      `The real question isn't if AI can do your job, but how you'll transform your work using AI.`,
      `We need to think about AI governance now, before capabilities advance further.`
    ]
  }
];