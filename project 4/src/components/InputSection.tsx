import React from 'react';
import { YoutubeIcon, MessageSquare, FileText, Zap, Brain, Loader2 } from 'lucide-react';
import { AnalysisOptions, AIModel } from '../types';

interface InputSectionProps {
  videoUrl: string;
  setVideoUrl: (url: string) => void;
  analysisOptions: AnalysisOptions;
  setAnalysisOptions: (options: AnalysisOptions) => void;
  selectedModel: AIModel;
  setSelectedModel: (model: AIModel) => void;
  onGenerate: () => void;
  isGenerating: boolean;
}

const InputSection = ({
  videoUrl,
  setVideoUrl,
  analysisOptions,
  setAnalysisOptions,
  selectedModel,
  setSelectedModel,
  onGenerate,
  isGenerating
}: InputSectionProps) => {
  return (
    <section id="input-section" className="py-12 animate-slide-up">
      <div className="backdrop-blur-sm bg-white/5 rounded-2xl p-6 md:p-8 border border-white/10 shadow-xl transition-all duration-300 hover:bg-white/10">
        <div className="relative mb-6 group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <YoutubeIcon className="h-5 w-5 text-gray-400 group-hover:text-red-500 transition-colors duration-300" />
          </div>
          <input
            type="text"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            className="block w-full pl-10 pr-3 py-4 bg-gray-900/60 text-white rounded-xl border border-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 hover:bg-gray-900/80"
            placeholder="Paste YouTube video URL here (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
          />
        </div>
        
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Analysis options */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-300 mb-3">Analysis Options</h3>
            
            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                className="hidden"
                checked={analysisOptions.comments}
                onChange={() => setAnalysisOptions({...analysisOptions, comments: !analysisOptions.comments})}
              />
              <div className={`w-12 h-6 flex items-center rounded-full p-1 transition-all duration-300 ${
                analysisOptions.comments ? 'bg-purple-600' : 'bg-gray-700'
              } group-hover:shadow-lg group-hover:shadow-purple-500/20`}>
                <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-all duration-300 ${
                  analysisOptions.comments ? 'translate-x-6' : ''
                }`}></div>
              </div>
              <div className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-gray-400 group-hover:text-gray-300 transition-colors" />
                <span className="text-gray-300 group-hover:text-white transition-colors">Comments Analysis</span>
              </div>
            </label>
            
            <label className="flex items-center space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                className="hidden"
                checked={analysisOptions.transcript}
                onChange={() => setAnalysisOptions({...analysisOptions, transcript: !analysisOptions.transcript})}
              />
              <div className={`w-12 h-6 flex items-center rounded-full p-1 transition-all duration-300 ${
                analysisOptions.transcript ? 'bg-blue-600' : 'bg-gray-700'
              } group-hover:shadow-lg group-hover:shadow-blue-500/20`}>
                <div className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-all duration-300 ${
                  analysisOptions.transcript ? 'translate-x-6' : ''
                }`}></div>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-gray-400 group-hover:text-gray-300 transition-colors" />
                <span className="text-gray-300 group-hover:text-white transition-colors">Transcript Analysis</span>
              </div>
            </label>
          </div>
          
          {/* AI Model Selection */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-300 mb-3">Select AI Model</h3>
            
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setSelectedModel('gemini')}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] ${
                  selectedModel === 'gemini'
                    ? 'bg-gradient-to-r from-blue-900/40 to-blue-600/40 border-blue-500/50 shadow-lg shadow-blue-500/10'
                    : 'bg-gray-800/40 border-gray-700/50 hover:bg-gray-800/60'
                }`}
              >
                <Zap className={`w-5 h-5 ${selectedModel === 'gemini' ? 'text-blue-400' : 'text-gray-400'}`} />
                <div className="text-left">
                  <div className={`font-medium ${selectedModel === 'gemini' ? 'text-blue-400' : 'text-gray-300'}`}>Gemini</div>
                  <div className="text-xs text-gray-400">⚡ Fast & Sharp</div>
                </div>
              </button>
              
              <button
                type="button"
                onClick={() => setSelectedModel('nvidia')}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] ${
                  selectedModel === 'nvidia'
                    ? 'bg-gradient-to-r from-emerald-900/40 to-emerald-600/40 border-emerald-500/50 shadow-lg shadow-emerald-500/10'
                    : 'bg-gray-800/40 border-gray-700/50 hover:bg-gray-800/60'
                }`}
              >
                <Brain className={`w-5 h-5 ${selectedModel === 'nvidia' ? 'text-emerald-400' : 'text-gray-400'}`} />
                <div className="text-left">
                  <div className={`font-medium ${selectedModel === 'nvidia' ? 'text-emerald-400' : 'text-gray-300'}`}>NVIDIA</div>
                  <div className="text-xs text-gray-400">🧠 Deep & Detailed • Free</div>
                </div>
              </button>
            </div>
          </div>
        </div>
        
        <button
          onClick={onGenerate}
          disabled={!videoUrl || isGenerating}
          className={`w-full py-4 px-6 rounded-xl font-medium text-lg transition-all duration-300 transform hover:scale-[1.01] active:scale-[0.99]
          ${isGenerating 
            ? 'bg-indigo-900/50 cursor-wait' 
            : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 shadow-lg hover:shadow-purple-500/20'
          }
          ${!videoUrl && 'opacity-60 cursor-not-allowed'}`}
        >
          {isGenerating ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating Insights...
            </span>
          ) : (
            'Generate Insights'
          )}
        </button>
      </div>
    </section>
  );
};

export default InputSection;