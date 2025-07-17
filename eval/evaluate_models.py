import os
import time
import logging
import openai
import requests
import pandas as pd
from datetime import datetime
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import re

def normalize_answer(text):
    """
    Normalize answer text for comparison by removing punctuation, 
    standardizing whitespace, and converting to lowercase.
    """
    if not text:
        return ""
    # Convert to lowercase and remove punctuation
    text = text.strip().lower()
    # Remove punctuation but keep spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Standardize whitespace
    text = ' '.join(text.split())
    return text

def extract_choice_text(question, raw_response):
    """
    Extract the full option text from a response that might be:
    - Just a letter (A, B, C, D)
    - Letter followed by text (A) option text, A. option text, etc.)
    - Just the option text
    - Mixed format
    """
    if not raw_response:
        return ""
    
    # Clean the response
    response = raw_response.strip()
    
    # First, try to match exact letter patterns at the beginning
    letter_patterns = [
        r'^([A-Da-d])[\s\.\)\-\:]',  # A. or A) or A: or A-
        r'^([A-Da-d])$',              # Just A
        r'^Option\s*([A-Da-d])',      # Option A
        r'^\(([A-Da-d])\)',           # (A)
    ]
    
    for pattern in letter_patterns:
        match = re.match(pattern, response, re.IGNORECASE)
        if match:
            letter = match.group(1).upper()
            option_key = f"Option {letter}"
            return question.get(option_key, "").strip()
    
    # If no letter pattern matches, try to match against option texts directly
    response_normalized = normalize_answer(response)
    
    # Check for exact matches with option texts
    for letter in ['A', 'B', 'C', 'D']:
        option_text = question.get(f"Option {letter}", "").strip()
        if option_text:
            option_normalized = normalize_answer(option_text)
            if response_normalized == option_normalized:
                return option_text
    
    # Check for partial matches (response is contained in option or vice versa)
    for letter in ['A', 'B', 'C', 'D']:
        option_text = question.get(f"Option {letter}", "").strip()
        if option_text:
            option_normalized = normalize_answer(option_text)
            # Check if response is a significant substring of option (at least 3 chars)
            if len(response_normalized) >= 3 and response_normalized in option_normalized:
                return option_text
            # Check if option is contained in response (for verbose responses)
            if len(option_normalized) >= 3 and option_normalized in response_normalized:
                return option_text
    
    # Check for key phrase matches (for responses that explain the answer)
    for letter in ['A', 'B', 'C', 'D']:
        option_text = question.get(f"Option {letter}", "").strip()
        if option_text:
            option_normalized = normalize_answer(option_text)
            # Split into words and check for significant overlap
            option_words = set(option_normalized.split())
            response_words = set(response_normalized.split())
            if option_words and response_words:
                # If at least 60% of option words are in response
                overlap = len(option_words.intersection(response_words))
                if overlap / len(option_words) >= 0.6:
                    return option_text
    
    # If no matches found, return the cleaned response
    return response.strip()

def answers_match(predicted_answer, ground_truth_answer, question):
    """
    Compare if a predicted answer matches the ground truth answer.
    Handles various answer formats and normalizes for comparison.
    """
    if not predicted_answer or not ground_truth_answer:
        return False
    
    # Normalize both answers
    pred_norm = normalize_answer(predicted_answer)
    gt_norm = normalize_answer(ground_truth_answer)
    
    # Direct match
    if pred_norm == gt_norm:
        return True
    
    # Check if both answers correspond to the same option
    pred_option = None
    gt_option = None
    
    # Find which option the predicted answer corresponds to
    for letter in ['A', 'B', 'C', 'D']:
        option_text = question.get(f"Option {letter}", "").strip()
        if option_text:
            option_norm = normalize_answer(option_text)
            if pred_norm == option_norm:
                pred_option = letter
            if gt_norm == option_norm:
                gt_option = letter
    
    # If both answers correspond to the same option, they match
    if pred_option and gt_option and pred_option == gt_option:
        return True
    
    # Check if predicted answer is just a letter that matches the ground truth option
    if len(pred_norm) == 1 and pred_norm.upper() in ['A', 'B', 'C', 'D']:
        letter = pred_norm.upper()
        option_text = question.get(f"Option {letter}", "").strip()
        if option_text and normalize_answer(option_text) == gt_norm:
            return True
    
    return False

# ========== CONFIGURATION ========== #
OPENAI_MODELS = ["gpt-4", "gpt-4o", "gpt-4o-mini"]
OLLAMA_MODELS = [
    "llama3.1:8b", "mixtral:8x7b", "phi4:14b","phi4-reasoning:14b", "gemma3:12b","gemma3:4b",
    "mistral:7b", "qwen3:8b", "qwen3:14b",
    "deepseek-r1:14b", "deepseek-r1:8b",
]
OLLAMA_SERVER = "http://localhost:11434/api/generate"
QUESTIONS_CSV = "eval/Objective Questions.csv"
TS = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = f"eval/eval_run_{TS}.log"
RESULTS_FILE = f"eval/results_{TS}.csv"
WIDE_RESULTS_FILE = f"eval/results_wide_{TS}.csv"
METRICS_FILE = f"eval/metrics_{TS}.csv"

# ========== LOGGING SETUP ========== #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

# ========== HELPER FUNCTIONS ========== #
def print_progress_bar(iteration, total, prefix='', suffix='', length=50):
    """Print a clean progress bar"""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if iteration == total:
        print()

def stream_ollama_pull(model):
    """Pull Ollama model with live progress"""
    print(f"\n🔄 Pulling Ollama model: {model}")
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model],
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"   {line.strip()}")
        process.stdout.close()
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ Successfully pulled {model}")
        else:
            print(f"❌ Failed to pull {model}")
            logging.error(f"Failed to pull {model}")
    except Exception as e:
        print(f"❌ Error pulling {model}: {e}")
        logging.error(f"Error pulling {model}: {e}")

def ensure_ollama_model(model):
    """Ensure Ollama model is available"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model not in result.stdout:
            stream_ollama_pull(model)
        else:
            print(f"✅ {model} already available")
    except Exception as e:
        logging.error(f"Error checking Ollama model {model}: {e}")

def get_ollama_response(model, prompt):
    """Get response from Ollama model"""
    try:
        response = requests.post(
            OLLAMA_SERVER,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        logging.error(f"Ollama {model} error: {e}")
        return None

def get_openai_response(model, prompt):
    """Get response from OpenAI model"""
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI {model} error: {e}")
        return None

def compute_metrics(ground_truths, predictions):
    """Compute evaluation metrics"""
    # Filter out None predictions for metrics calculation
    valid_pairs = [(gt, pred) for gt, pred in zip(ground_truths, predictions) if pred is not None]
    if not valid_pairs:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1_score": 0.0}
    
    gt_valid, pred_valid = zip(*valid_pairs)
    
    return {
        "accuracy": accuracy_score(gt_valid, pred_valid),
        "precision": precision_score(gt_valid, pred_valid, average='macro', zero_division=0),
        "recall": recall_score(gt_valid, pred_valid, average='macro', zero_division=0),
        "f1_score": f1_score(gt_valid, pred_valid, average='macro', zero_division=0)
    }

# ========== EVALUATION FUNCTIONS ========== #
def evaluate_single_model(model_info, questions):
    """Evaluate a single model on all questions"""
    model_type, model_name = model_info
    print(f"\n🚀 Starting evaluation: {model_type.upper()} - {model_name}")
    
    results = []
    correct_count = 0
    total_questions = len(questions)
    
    for idx, question in enumerate(questions):
        # Create consistent prompt
        prompt = (
            f"Question: {question['Question']}\n"
            f"Options:\n"
            f"A) {question['Option A']}\n"
            f"B) {question['Option B']}\n"
            f"C) {question['Option C']}\n"
            f"D) {question['Option D']}\n\n"
            f"Please answer with either the letter (A, B, C, or D) or the exact option text."
        )
        
        # Get model response
        if model_type == "openai":
            response = get_openai_response(model_name, prompt)
        else:  # ollama
            response = get_ollama_response(model_name, prompt)
        
        # Process the response
        raw_response = response or ""
        extracted_response = extract_choice_text(question, raw_response)
        
        # Compare with ground truth
        is_correct = answers_match(extracted_response, question['Answer'], question)
        
        if is_correct:
            correct_count += 1
        
        # Store result
        result = {
            "model_type": model_type,
            "model_name": model_name,
            "question": question['Question'],
            "ground_truth": question['Answer'],
            "model_response": extracted_response,
            "raw_response": raw_response,
            "is_correct": is_correct,
            "category": question.get('Category', '')
        }
        results.append(result)
        
        # Update progress
        status = "✓" if is_correct else "✗"
        print_progress_bar(
            idx + 1, 
            total_questions, 
            prefix=f"{model_name:<20}", 
            suffix=f"Q{idx+1:3d}/{total_questions} {status}"
        )
        
        # Brief pause to avoid overwhelming APIs
        time.sleep(0.1)
    
    # Calculate final metrics
    accuracy = correct_count / total_questions
    
    # Calculate other metrics
    ground_truths = [r["is_correct"] for r in results]
    predictions = [r["is_correct"] for r in results]
    
    metrics = {
        "model_type": model_type,
        "model_name": model_name,
        "accuracy": accuracy,
        "correct_count": correct_count,
        "total_questions": total_questions
    }
    
    print(f"\n📊 {model_name} Results:")
    print(f"   Accuracy: {accuracy:.1%} ({correct_count}/{total_questions})")
    
    return results, metrics

def run_evaluation(questions):
    """Run evaluation on all models"""
    print("🔧 Setting up Ollama models...")
    for model in OLLAMA_MODELS:
        ensure_ollama_model(model)
    
    # Prepare model combinations
    openai_models = [("openai", m) for m in OPENAI_MODELS]
    ollama_models = [("ollama", m) for m in OLLAMA_MODELS]
    all_models = ollama_models + openai_models
    
    # Initialize results storage
    all_results = []
    all_metrics = []
    
    # Initialize wide format results
    wide_results = []
    for question in questions:
        wide_row = {
            "question": question['Question'],
            "ground_truth": normalize_answer(question['Answer']),
            "category": question.get('Category', '')
        }
        # Add columns for each model
        for model_type, model_name in all_models:
            wide_row[f"{model_type}_{model_name}"] = None
        wide_results.append(wide_row)
    
    print(f"\n🎯 Starting evaluation of {len(all_models)} models on {len(questions)} questions")
    print("=" * 80)
    
    # Run Ollama models in parallel (multi-GPU utilization)
    if ollama_models:
        print("🚀 Running Ollama models in parallel for multi-GPU utilization...")
        ollama_results, ollama_metrics = run_ollama_parallel(ollama_models, questions, wide_results)
        all_results.extend(ollama_results)
        all_metrics.extend(ollama_metrics)
        
        # Save intermediate results
        pd.DataFrame(all_results).to_csv(RESULTS_FILE, index=False)
        pd.DataFrame(wide_results).to_csv(WIDE_RESULTS_FILE, index=False)
        pd.DataFrame(all_metrics).to_csv(METRICS_FILE, index=False)
    
    # Run OpenAI models sequentially (API rate limits)
    if openai_models:
        print("\n🌐 Running OpenAI models sequentially (API rate limits)...")
        for model_info in openai_models:
            results, metrics = evaluate_single_model(model_info, questions)
            
            # Store results
            all_results.extend(results)
            all_metrics.append(metrics)
            
            # Update wide format
            for idx, result in enumerate(results):
                model_type, model_name = model_info
                wide_results[idx][f"{model_type}_{model_name}"] = result["model_response"]
            
            # Save intermediate results
            pd.DataFrame(all_results).to_csv(RESULTS_FILE, index=False)
            pd.DataFrame(wide_results).to_csv(WIDE_RESULTS_FILE, index=False)
            pd.DataFrame(all_metrics).to_csv(METRICS_FILE, index=False)
            
            print("-" * 80)
    
    return all_results, all_metrics, wide_results

def run_ollama_parallel(ollama_models, questions, wide_results):
    """Run Ollama models in parallel to utilize multiple GPUs"""
    import threading
    from queue import Queue
    
    results_queue = Queue()
    metrics_queue = Queue()
    progress_lock = threading.Lock()
    progress_counters = {model[1]: 0 for model in ollama_models}
    
    def worker(model_info, questions, model_idx):
        """Worker function for parallel execution"""
        model_type, model_name = model_info
        results = []
        correct_count = 0
        total_questions = len(questions)
        
        for idx, question in enumerate(questions):
            # Create consistent prompt
            prompt = (
                f"Question: {question['Question']}\n"
                f"Options:\n"
                f"A) {question['Option A']}\n"
                f"B) {question['Option B']}\n"
                f"C) {question['Option C']}\n"
                f"D) {question['Option D']}\n\n"
                f"Please answer with either the letter (A, B, C, or D) or the exact option text."
            )
            
            response = get_ollama_response(model_name, prompt)
            
            # Process the response
            raw_response = response or ""
            extracted_response = extract_choice_text(question, raw_response)
            
            # Compare with ground truth
            is_correct = answers_match(extracted_response, question['Answer'], question)
            
            if is_correct:
                correct_count += 1
            
            # Store result
            result = {
                "model_type": model_type,
                "model_name": model_name,
                "question": question['Question'],
                "ground_truth": question['Answer'],
                "model_response": extracted_response,
                "raw_response": raw_response,
                "is_correct": is_correct,
                "category": question.get('Category', '')
            }
            results.append(result)
            
            # Update progress with thread safety
            with progress_lock:
                progress_counters[model_name] = idx + 1
                # Print consolidated progress
                progress_lines = []
                for m_name, count in progress_counters.items():
                    percent = (count / total_questions) * 100
                    status = f"{count:3d}/{total_questions} ({percent:5.1f}%)"
                    progress_lines.append(f"{m_name:<20} {status}")
                
                # Clear and reprint progress
                print(f"\r\033[{len(ollama_models)}A", end="")  # Move cursor up
                for line in progress_lines:
                    print(f"\033[K{line}")  # Clear line and print
            
            time.sleep(0.05)  # Small delay to prevent overwhelming
        
        # Calculate metrics
        accuracy = correct_count / total_questions
        model_metrics = {
            "model_type": model_type,
            "model_name": model_name,
            "accuracy": accuracy,
            "correct_count": correct_count,
            "total_questions": total_questions
        }
        
        results_queue.put((model_info, results))
        metrics_queue.put(model_metrics)
    
    # Initialize progress display
    print("🔄 Parallel execution progress:")
    for model_type, model_name in ollama_models:
        print(f"{model_name:<20} {0:>3d}/{len(questions)} (  0.0%)")
    
    # Start parallel execution
    max_workers = min(len(ollama_models), 2)  # Limit concurrent models
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for idx, model_info in enumerate(ollama_models):
            future = executor.submit(worker, model_info, questions, idx)
            futures.append(future)
        
        # Wait for completion
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions
    
    # Collect results
    all_results = []
    all_metrics = []
    
    while not results_queue.empty():
        model_info, results = results_queue.get()
        all_results.extend(results)
        
        # Update wide format
        model_type, model_name = model_info
        for idx, result in enumerate(results):
            wide_results[idx][f"{model_type}_{model_name}"] = result["model_response"]
    
    while not metrics_queue.empty():
        metrics = metrics_queue.get()
        all_metrics.append(metrics)
    
    # Print final results for Ollama models
    print("\n📊 Ollama Models Results:")
    for metrics in sorted(all_metrics, key=lambda x: x['model_name']):
        model_name = metrics['model_name']
        accuracy = metrics['accuracy']
        correct = metrics['correct_count']
        total = metrics['total_questions']
        print(f"   {model_name:<20} {accuracy:>8.1%} ({correct:>3d}/{total})")
    
    return all_results, all_metrics

def main():
    """Main execution function"""
    print("🚀 Model Evaluation Suite")
    print("=" * 50)
    
    # Load questions
    try:
        df = pd.read_csv(QUESTIONS_CSV)
        questions = df.to_dict(orient="records")
        print(f"📚 Loaded {len(questions)} questions from {QUESTIONS_CSV}")
    except Exception as e:
        print(f"❌ Error loading questions: {e}")
        return
    
    # Create output directory
    os.makedirs("eval", exist_ok=True)
    
    # Run evaluation
    try:
        all_results, all_metrics, wide_results = run_evaluation(questions)
        
        # Final save
        pd.DataFrame(all_results).to_csv(RESULTS_FILE, index=False)
        pd.DataFrame(wide_results).to_csv(WIDE_RESULTS_FILE, index=False)
        pd.DataFrame(all_metrics).to_csv(METRICS_FILE, index=False)
        
        print("\n🎉 Evaluation Complete!")
        print(f"📁 Results saved to:")
        print(f"   - Detailed: {RESULTS_FILE}")
        print(f"   - Wide format: {WIDE_RESULTS_FILE}")
        print(f"   - Metrics: {METRICS_FILE}")
        print(f"   - Log: {LOG_FILE}")
        
        # Display final summary
        print("\n📊 Final Summary:")
        print("-" * 60)
        for metric in all_metrics:
            model_name = f"{metric['model_type']}_{metric['model_name']}"
            print(f"{model_name:<25} {metric['accuracy']:>8.1%} ({metric['correct_count']:>3d}/{metric['total_questions']})")
        
    except KeyboardInterrupt:
        print("\n⚠️  Evaluation interrupted by user")
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        logging.error(f"Error during evaluation: {e}")

if __name__ == "__main__":
    main()
