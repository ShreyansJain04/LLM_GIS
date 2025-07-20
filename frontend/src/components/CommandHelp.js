import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { XCircleIcon } from "@heroicons/react/24/outline";

const CommandHelp = ({ isVisible, onClose }) => (
  <AnimatePresence>
    {isVisible && (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-secondary-200 rounded-lg shadow-lg p-4 z-10"
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-secondary-900">Quick Commands</h3>
          <button
            onClick={onClose}
            className="text-secondary-400 hover:text-secondary-600"
          >
            <XCircleIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="space-y-1">
            <div>
              <code className="text-primary-600">!help</code> - Show all
              commands
            </div>
            <div>
              <code className="text-primary-600">!explain topic</code> - Get
              explanation
            </div>
            <div>
              <code className="text-primary-600">!example topic</code> - Get
              example
            </div>
            <div>
              <code className="text-primary-600">!question topic</code> -
              Practice question
            </div>
          </div>
          <div className="space-y-1">
            <div>
              <code className="text-primary-600">!quiz topic</code> - Start quiz
            </div>
            <div>
              <code className="text-primary-600">!sources</code> - Show
              documents
            </div>
            <div>
              <code className="text-primary-600">!progress</code> - View
              progress
            </div>
            <div>
              <code className="text-primary-600">!hint</code> - Get hint
            </div>
          </div>
        </div>
      </motion.div>
    )}
  </AnimatePresence>
);

export default CommandHelp;
