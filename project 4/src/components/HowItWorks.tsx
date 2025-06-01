import React from 'react';
import { YoutubeIcon, FileText, MessageSquare, Sparkles, ArrowRight } from 'lucide-react';

const HowItWorks = () => {
  const steps = [
    {
      icon: <YoutubeIcon className="h-6 w-6 text-blue-400" />,
      title: 'Paste YouTube URL',
      description: 'Simply copy & paste any YouTube video URL to get started'
    },
    {
      icon: <FileText className="h-6 w-6 text-purple-400" />,
      title: 'Select Analysis Options',
      description: 'Choose to analyze the video transcript, comments, or both'
    },
    {
      icon: <Sparkles className="h-6 w-6 text-emerald-400" />,
      title: 'Pick AI Model',
      description: 'Select Gemini for speed or NVIDIA for in-depth analysis'
    },
    {
      icon: <MessageSquare className="h-6 w-6 text-amber-400" />,
      title: 'Get Deep Insights',
      description: 'Receive structured insights, summaries and key takeaways'
    }
  ];

  return (
    <section id="how-it-works" className="py-16">
      <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center">How It Works</h2>
      
      <div className="grid md:grid-cols-4 gap-6">
        {steps.map((step, index) => (
          <div key={index} className="relative">
            <div className="backdrop-blur-sm bg-white/5 rounded-xl p-6 border border-white/10 h-full transition-transform duration-300 hover:-translate-y-1">
              <div className="flex flex-col items-center text-center">
                <div className="w-12 h-12 rounded-full flex items-center justify-center bg-gray-800/80 mb-4">
                  {step.icon}
                </div>
                <h3 className="text-lg font-medium mb-2">{step.title}</h3>
                <p className="text-gray-400 text-sm">{step.description}</p>
              </div>
            </div>
            
            {index < steps.length - 1 && (
              <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                <ArrowRight className="h-5 w-5 text-gray-500" />
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export default HowItWorks;