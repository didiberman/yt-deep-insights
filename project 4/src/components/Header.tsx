import React from 'react';
import { BrainCircuit } from 'lucide-react';

const Header = () => {
  return (
    <header className="py-6 relative z-10">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit className="h-8 w-8 text-blue-400" />
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-emerald-400">
            YouTubeGPT
          </span>
        </div>
        <nav>
          <ul className="flex items-center gap-6">
            <li>
              <a href="#features" className="text-gray-300 hover:text-white transition-colors duration-200">
                Features
              </a>
            </li>
            <li>
              <a href="#how-it-works" className="text-gray-300 hover:text-white transition-colors duration-200">
                How it Works
              </a>
            </li>
            <li>
              <a 
                href="#get-started" 
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-full text-white font-medium transition-colors duration-200"
              >
                Get Started
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;