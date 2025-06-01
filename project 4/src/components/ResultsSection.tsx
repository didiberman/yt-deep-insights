import React, { FC } from 'react';

interface ResultsSectionProps {
  result: {
    video_title: string;
    transcript?: string;
    comments: string[];
    analysis: string;
  } | null;
}

const ResultsSection: FC<ResultsSectionProps> = ({ result }) => {
  if (!result) return null;

  return (
    <section id="results" className="py-12">
      <div className="backdrop-blur-md bg-white/5 rounded-2xl p-6 md:p-8 border border-white/10 shadow-xl">
        <h2 className="text-2xl font-bold mb-8">Generated Insights</h2>
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2 text-blue-300">Video Title</h3>
          <div className="text-gray-200 mb-4">{result.video_title}</div>
          {result.transcript && (
            <>
              <h3 className="text-lg font-semibold mb-2 text-purple-300">Transcript (first 500 chars)</h3>
              <div className="text-gray-300 mb-4 whitespace-pre-line">{result.transcript.slice(0, 500)}{result.transcript.length > 500 ? '...' : ''}</div>
            </>
          )}
          {result.comments && result.comments.length > 0 && (
            <>
              <h3 className="text-lg font-semibold mb-2 text-emerald-300">Sample Comments</h3>
              <ul className="list-disc pl-6 text-gray-300 mb-4">
                {result.comments.slice(0, 5).map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
                {result.comments.length > 5 && <li>...and {result.comments.length - 5} more</li>}
              </ul>
            </>
          )}
          <h3 className="text-lg font-semibold mb-2 text-pink-300">AI Analysis</h3>
          <div className="text-gray-100 whitespace-pre-line border border-pink-400/20 rounded-lg p-4 bg-pink-900/10">
            {result.analysis}
          </div>
        </div>
      </div>
    </section>
  );
};

export default ResultsSection;