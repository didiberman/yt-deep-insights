import React from 'react';
import { BrainCircuit, Github, Twitter } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="py-12 border-t border-gray-800/50">
      <div className="flex flex-col md:flex-row justify-between items-center">
        <div className="flex items-center gap-2 mb-4 md:mb-0">
          <BrainCircuit className="h-6 w-6 text-blue-400" />
          <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400">
            YouTubeGPT
          </span>
        </div>
        
        <div className="text-gray-400 text-sm mb-4 md:mb-0">
          © {new Date().getFullYear()} YouTubeGPT • All rights reserved
        </div>
        
        <div className="flex items-center gap-4">
          <a href="#" className="text-gray-400 hover:text-white transition-colors duration-200">
            <Github className="h-5 w-5" />
          </a>
          <a href="#" className="text-gray-400 hover:text-white transition-colors duration-200">
            <Twitter className="h-5 w-5" />
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;