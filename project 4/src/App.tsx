import React, { useState } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import InputSection from './components/InputSection';
import HowItWorks from './components/HowItWorks';
import ResultsSection from './components/ResultsSection';
import Footer from './components/Footer';
import { AnalysisOptions, AIModel } from './types';
import { analyzeVideo } from './api';

function App() {
  const [videoUrl, setVideoUrl] = useState('');
  const [analysisOptions, setAnalysisOptions] = useState<AnalysisOptions>({
    transcript: false,
    comments: true
  });
  const [selectedModel, setSelectedModel] = useState<AIModel>('nvidia');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!videoUrl) return;
    setIsGenerating(true);
    setError(null);
    setShowResults(false);
    try {
      const mode =
        analysisOptions.comments && analysisOptions.transcript
          ? 'Both'
          : analysisOptions.comments
          ? 'Comments Only'
          : 'Transcript Only';
      const modelMap: Record<string, string> = {
        gemini: 'Google Gemini',
        nvidia: 'LLama-Nvidia'
      };
      const result = await analyzeVideo({
        videoUrl,
        modelName: modelMap[selectedModel],
        mode
      });
      setAnalysisResult(result);
      setShowResults(true);
      document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' });
    } catch (e: any) {
      setError(e.message || 'Unknown error');
    }
    setIsGenerating(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-indigo-950 text-white font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <Header />
        <main className="relative">
          <HeroSection />
          
          <InputSection 
            videoUrl={videoUrl}
            setVideoUrl={setVideoUrl}
            analysisOptions={analysisOptions}
            setAnalysisOptions={setAnalysisOptions}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
          />
          
          <HowItWorks />
          
          {error && <div className="text-red-400 text-center my-4">{error}</div>}
          {showResults && <ResultsSection result={analysisResult} />}
        </main>
        <Footer />
      </div>
      
      {/* Animated background elements */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-600 rounded-full mix-blend-multiply filter blur-[100px] opacity-20 animate-pulse-slow"></div>
        <div className="absolute top-40 -left-20 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-[100px] opacity-20 animate-pulse-slow delay-700"></div>
        <div className="absolute bottom-40 right-20 w-80 h-80 bg-emerald-600 rounded-full mix-blend-multiply filter blur-[100px] opacity-20 animate-pulse-slow delay-1000"></div>
      </div>
    </div>
  );
}

export default App;