import React from 'react';
import { ArrowDown } from 'lucide-react';

const HeroSection = () => {
  return (
    <section className="py-16 md:py-24 text-center relative">
      <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6 max-w-3xl mx-auto">
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400">
          AI-Powered Insights
        </span>{' '}
        from any YouTube Video
      </h1>
      
      <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto mb-8">
        Extract deep, meaningful insights from videos in seconds. Analyze transcripts, comments, and more with 
        state-of-the-art AI models.
      </p>
      
      <a 
        href="#input-section" 
        className="inline-flex items-center gap-2 px-1 py-1 border-b-2 border-blue-400 text-blue-400 hover:text-blue-300 hover:border-blue-300 transition-colors duration-200"
      >
        Try it now
        <ArrowDown className="w-4 h-4 animate-bounce" />
      </a>
      
      {/* Decorative element */}
      <div className="absolute top-1/2 -translate-y-1/2 left-0 w-24 h-24 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full opacity-20 blur-2xl"></div>
      <div className="absolute top-1/4 right-10 w-32 h-32 bg-gradient-to-r from-purple-600 to-emerald-600 rounded-full opacity-20 blur-2xl"></div>
    </section>
  );
};

export default HeroSection;