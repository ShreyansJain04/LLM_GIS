# import os
# import time
# import logging
# import openai
# import requests
# import pandas as pd
# from datetime import datetime
# import subprocess
# import sys


# # ========== CONFIGURATION ========== #
# OPENAI_MODELS = [
#     # "gpt-3.5-turbo",
#     "gpt-4",
#     "gpt-4o",
#     "gpt-o4-mini",
# ]
# OLLAMA_MODELS = [
#     "llama3.1:8b",
#     "mixtral:8x7b",
#     "phi4:14b",
#     "gemma:7b",
#     # "wizardlm2:7b",
#     "mistral:7b",
#     "qwen3:8b",
#     "qwen3:14b",
#     "deepseek-r1:14b",
#     "deepseek-r1:8b",
# ]
# OLLAMA_URL = "http://localhost:11434/api/generate"
# QUESTIONS_CSV = "eval/Objective Questions.csv"
# LOG_FILE = f"eval/eval_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
# RESULTS_FILE = f"eval/eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
# WIDE_RESULTS_FILE = f"eval/eval_results_wide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# # ========== LOGGING SETUP ========== #
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s %(message)s',
#     handlers=[
#         logging.FileHandler(LOG_FILE),
#         logging.StreamHandler(sys.stdout)
#     ]
# )

# def stream_ollama_pull(model_name):
#     """Stream the output of ollama pull so user sees progress live."""
#     logging.info(f"Pulling Ollama model: {model_name} ...")
#     try:
#         process = subprocess.Popen(["ollama", "pull", model_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
#         for line in iter(process.stdout.readline, ''):
#             if line:
#                 print(line, end='')
#                 logging.info(line.strip())
#         process.stdout.close()
#         process.wait()
#         if process.returncode != 0:
#             logging.error(f"Failed to pull {model_name}")
#         else:
#             logging.info(f"Model {model_name} pulled successfully.")
#     except Exception as e:
#         logging.error(f"Error pulling Ollama model {model_name}: {e}")

# def ensure_ollama_model(model_name):
#     """Pull the model if not already available, with live progress."""
#     try:
#         result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
#         if model_name not in result.stdout:
#             stream_ollama_pull(model_name)
#         else:
#             logging.info(f"Ollama model {model_name} already available.")
#     except Exception as e:
#         logging.error(f"Error checking/pulling Ollama model {model_name}: {e}")

# def get_openai_response(model, prompt):
#     try:
#         response = openai.chat.completions.create(
#             model=model,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         logging.error(f"OpenAI {model} error: {e}")
#         return None

# def get_ollama_response(model, prompt):
#     try:
#         data = {"model": model, "prompt": prompt, "stream": False}
#         r = requests.post(OLLAMA_URL, json=data, timeout=120)
#         r.raise_for_status()
#         return r.json().get("response", "").strip()
#     except Exception as e:
#         logging.error(f"Ollama {model} error: {e}")
#         return None

# def normalize_answer(ans):
#     if not ans:
#         return ""
#     return ans.strip().lower().replace(".", "").replace(",", "").replace("'", "").replace('"', "")

# def print_progress_bar(iteration, total, prefix='', suffix='', length=40):
#     percent = f"{100 * (iteration / float(total)):.1f}"
#     filled_length = int(length * iteration // total)
#     bar = '█' * filled_length + '-' * (length - filled_length)
#     print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
#     if iteration == total:
#         print()

# def main():
#     # Ensure Ollama models are available
#     for model in OLLAMA_MODELS:
#         ensure_ollama_model(model)

#     # Load questions
#     df = pd.read_csv(QUESTIONS_CSV)
#     questions = df.to_dict(orient="records")
#     total = len(questions)
#     logging.info(f"Loaded {total} questions from {QUESTIONS_CSV}")

#     all_models = [("openai", m) for m in OPENAI_MODELS] + [("ollama", m) for m in OLLAMA_MODELS]
#     results = []
#     wide_results = []
#     # Prepare wide-format base
#     wide_base = [
#         {
#             "question": q['Question'],
#             "ground_truth": normalize_answer(q['Answer']),
#             "category": q.get('Category', ''),
#             **{f"{model_type}_{model_name}": None for model_type, model_name in all_models}
#         }
#         for q in questions
#     ]

#     for model_type, model_name in all_models:
#         logging.info(f"\n===== Evaluating {model_type.upper()} model: {model_name} =====")
#         correct = 0
#         for idx, q in enumerate(questions):
#             prompt = f"Question: {q['Question']}\nOptions: A) {q['Option A']} B) {q['Option B']} C) {q['Option C']} D) {q['Option D']}\nAnswer with the correct option text only."
#             gt = normalize_answer(q['Answer'])
#             if model_type == "openai":
#                 response = get_openai_response(model_name, prompt)
#             else:
#                 response = get_ollama_response(model_name, prompt)
#             norm_resp = normalize_answer(response)
#             is_correct = norm_resp == gt
#             if is_correct:
#                 correct += 1
#             # Log progress
#             logging.info(f"[{model_name}] Q{idx+1}/{total} | GT: {gt} | Model: {norm_resp} | {'✔' if is_correct else '✘'}")
#             print_progress_bar(idx + 1, total, prefix=f'{model_name}', suffix=f'Q{idx+1}/{total}', length=30)
#             results.append({
#                 "model_type": model_type,
#                 "model_name": model_name,
#                 "question": q['Question'],
#                 "ground_truth": gt,
#                 "model_response": norm_resp,
#                 "is_correct": is_correct,
#                 "category": q.get('Category', ''),
#             })
#             # Save to wide format
#             wide_base[idx][f"{model_type}_{model_name}"] = norm_resp
#             # Save intermediate results after each question
#             if (idx + 1) % 20 == 0 or (idx + 1) == total:
#                 pd.DataFrame(results).to_csv(RESULTS_FILE, index=False)
#                 pd.DataFrame(wide_base).to_csv(WIDE_RESULTS_FILE, index=False)
#             # time.sleep(0.5)  # To avoid rate limits
#         acc = correct / total
#         logging.info(f"===== {model_name} Accuracy: {acc:.2%} =====\n")
#         # Save after each model
#         pd.DataFrame(results).to_csv(RESULTS_FILE, index=False)
#         pd.DataFrame(wide_base).to_csv(WIDE_RESULTS_FILE, index=False)

#     logging.info(f"Results saved to {RESULTS_FILE}")
#     logging.info(f"Wide-format results saved to {WIDE_RESULTS_FILE}")

# if __name__ == "__main__":
#     main() 


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

# ========== CONFIGURATION ========== #
OPENAI_MODELS = ["gpt-4", "gpt-4o", "gpt-4o-mini"]
OLLAMA_MODELS = [
    "llama3.1:8b", "mixtral:8x7b", "phi4:14b", "gemma:7b",
    "mistral:7b", "qwen3:8b", "qwen3:14b",
    "deepseek-r1:14b", "deepseek-r1:8b"
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

def normalize_answer(answer):
    """Normalize answer for comparison - extract just the option letter"""
    if not answer:
        return ""
    
    # Clean the response and convert to lowercase
    clean_answer = answer.strip().lower()
    
    # Try to extract option letter from various formats
    # Look for patterns like "A", "a)", "A)", "(A)", "option A", etc.
    import re
    
    # Pattern to find option letters
    letter_patterns = [
        r'^[abcd]$',                    # Just the letter: "a", "b", "c", "d"
        r'^[abcd]\)',                   # Letter with parenthesis: "a)", "b)", etc.
        r'^\([abcd]\)',                 # Letter in parenthesis: "(a)", "(b)", etc.
        r'option\s+[abcd]',             # "option a", "option b", etc.
        r'^[abcd]\s*\)',                # Letter with space and parenthesis: "a )", etc.
        r'answer\s+is\s+[abcd]',        # "answer is a", "answer is b", etc.
        r'choice\s+[abcd]',             # "choice a", "choice b", etc.
        r'the\s+answer\s+is\s+[abcd]',  # "the answer is a", etc.
    ]
    
    for pattern in letter_patterns:
        match = re.search(pattern, clean_answer)
        if match:
            # Extract just the letter
            letter = re.search(r'[abcd]', match.group())
            if letter:
                return letter.group()
    
    # If no pattern matched, remove punctuation and try to find a single letter
    clean_text = re.sub(r'[^abcd]', '', clean_answer)
    if len(clean_text) == 1 and clean_text in 'abcd':
        return clean_text
    
    # Last resort: return the cleaned original
    return clean_answer.translate(str.maketrans('', '', ".,'\"()"))

def get_ground_truth_option(question):
    """Get the option letter (A, B, C, D) that corresponds to the correct answer text"""
    correct_answer = question['Answer'].strip().lower()
    
    # Check each option to find which one matches the answer
    options = {
        'a': question['Option A'].strip().lower(),
        'b': question['Option B'].strip().lower(), 
        'c': question['Option C'].strip().lower(),
        'd': question['Option D'].strip().lower()
    }
    
    # First try exact match
    for letter, option_text in options.items():
        if option_text == correct_answer:
            return letter
    
    # Try case-insensitive match with cleaned text
    import re
    correct_clean = re.sub(r'[^\w\s]', '', correct_answer).strip()
    
    for letter, option_text in options.items():
        option_clean = re.sub(r'[^\w\s]', '', option_text).strip()
        if option_clean == correct_clean:
            return letter
    
    # Try partial matches (for cases where answer might be subset of option)
    for letter, option_text in options.items():
        if correct_clean in option_text or option_text in correct_clean:
            return letter
    
    # Debug: print when no match found
    print(f"\n⚠️ No match found for answer: '{correct_answer}'")
    print(f"   Options: {options}")
    
    # Return 'x' to indicate no match found (for debugging)
    return 'x'

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
        # Create prompt
        prompt = (
            f"Question: {question['Question']}\n"
            f"Options: A) {question['Option A']} B) {question['Option B']} "
            f"C) {question['Option C']} D) {question['Option D']}\n"
            f"Answer with the correct option letter only (A, B, C, or D)."
        )
        
        # Get ground truth
        ground_truth = get_ground_truth_option(question)
        
        # Get model response
        if model_type == "openai":
            response = get_openai_response(model_name, prompt)
        else:  # ollama
            response = get_ollama_response(model_name, prompt)
        
        normalized_response = normalize_answer(response) if response else ""
        is_correct = normalized_response == ground_truth and response is not None
        
        if is_correct:
            correct_count += 1
        
        # Store result
        result = {
            "model_type": model_type,
            "model_name": model_name,
            "question": question['Question'],
            "ground_truth": ground_truth,
            "model_response": normalized_response,
            "raw_response": response,
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
    ground_truths = [r["ground_truth"] for r in results]
    predictions = [r["model_response"] for r in results]
    metrics = compute_metrics(ground_truths, predictions)
    
    accuracy = correct_count / total_questions
    print(f"\n📊 {model_name} Results:")
    print(f"   Accuracy: {accuracy:.1%} ({correct_count}/{total_questions})")
    print(f"   Precision: {metrics['precision']:.3f}")
    print(f"   Recall: {metrics['recall']:.3f}")
    print(f"   F1-Score: {metrics['f1_score']:.3f}")
    
    return results, {
        "model_type": model_type,
        "model_name": model_name,
        "accuracy": accuracy,
        **metrics,
        "correct_count": correct_count,
        "total_questions": total_questions
    }

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
            "ground_truth": get_ground_truth_option(question),
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
            # Create prompt
            prompt = (
                f"Question: {question['Question']}\n"
                f"Options: A) {question['Option A']} B) {question['Option B']} "
                f"C) {question['Option C']} D) {question['Option D']}\n"
                f"Answer with the correct option letter only (A, B, C, or D)."
            )
            
            ground_truth = get_ground_truth_option(question)
            response = get_ollama_response(model_name, prompt)
            normalized_response = normalize_answer(response) if response else ""
            is_correct = normalized_response == ground_truth and response is not None
            
            if is_correct:
                correct_count += 1
            
            # Store result
            result = {
                "model_type": model_type,
                "model_name": model_name,
                "question": question['Question'],
                "ground_truth": ground_truth,
                "model_response": normalized_response,
                "raw_response": response,
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
        ground_truths = [r["ground_truth"] for r in results]
        predictions = [r["model_response"] for r in results]
        metrics = compute_metrics(ground_truths, predictions)
        
        accuracy = correct_count / total_questions
        model_metrics = {
            "model_type": model_type,
            "model_name": model_name,
            "accuracy": accuracy,
            **metrics,
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
