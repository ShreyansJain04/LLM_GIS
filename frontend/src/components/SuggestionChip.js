import React from "react";
import { motion } from "framer-motion";

const SuggestionChip = ({ suggestion, onClick }) => (
  <motion.button
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onClick(suggestion)}
    className="px-3 py-2 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-full text-sm border border-primary-200 transition-colors duration-200"
  >
    {suggestion}
  </motion.button>
);

export default SuggestionChip;
