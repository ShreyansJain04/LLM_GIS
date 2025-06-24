import asyncio
import json
import os
import sys

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy


BASE_URL = "https://www.esri.com/en-us/arcgis/products/arcgis-pro/resources"

INSTRUCTION_TO_LLM = (
    "Extract clean and meaningful text chunks from this page suitable for training a language model."
)

async def main():
    print("[INIT] Starting crawl with LLM extraction...")
    sys.stdout.flush()
    
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="litellm_proxy/llama3.1:latest",
            api_token="sk-e94c63484a45419fb5703b29fd18e687",
            base_url="https://genai.rcac.purdue.edu/api",
            max_tokens=800
        ),
        schema=None,
        extraction_type="block",
        instruction=INSTRUCTION_TO_LLM,
        chunk_token_threshold=1000,
        overlap_rate=0.2,
        apply_chunking=True,
        input_format="html",
        verbose=True
    )

    print("[CONFIG] LLM extraction strategy configured")
    sys.stdout.flush()

    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        exclude_external_links=True
    )

    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        print("[CRAWL] Starting to crawl the website...")
        sys.stdout.flush()
        
        result = await crawler.arun(url=BASE_URL, config=crawl_config)
        
        print(f"[DEBUG] result.success: {result.success}")
        sys.stdout.flush()
        
        if hasattr(result, 'extracted_content'):
            if result.extracted_content:
                print(f"[DEBUG] result.extracted_content (first 200 chars): {str(result.extracted_content)[:200]}")
            else:
                print("[DEBUG] result.extracted_content is empty or None")
        else:
            print("[DEBUG] result has no attribute 'extracted_content'")
        
        sys.stdout.flush()

        if result.success:
            print("[SAVE] Attempting to save extracted content...")
            sys.stdout.flush()
            
            # Write the result to a file
            try:
                if result.extracted_content:
                    print(f"[SAVE] Parsing JSON content...")
                    sys.stdout.flush()
                    content = json.loads(result.extracted_content)
                    
                    print(f"[SAVE] Writing to esri_scraped_data.jsonl...")
                    sys.stdout.flush()
                    with open("esri_scraped_data.jsonl", "a") as f:
                        f.write(json.dumps(content) + "\n")
                    
                    print(f"✅ Successfully extracted content and saved to file")
                    print(f"📊 Content type: {type(content)}")
                    if isinstance(content, list):
                        print(f"📊 Number of blocks extracted: {len(content)}")
                    sys.stdout.flush()
                else:
                    print("❌ No LLM content was extracted - saving raw markdown as fallback")
                    # Fallback: save raw markdown content if LLM extraction failed
                    fallback_content = {
                        "url": result.url,
                        "title": result.metadata.get("title", "No title") if result.metadata else "No metadata",
                        "markdown": result.markdown.fit_markdown[:5000] if hasattr(result, 'markdown') and result.markdown else "No markdown",
                        "timestamp": json.dumps({"timestamp": "fallback_save"}),
                        "extraction_method": "fallback_raw_markdown"
                    }
                    with open("esri_scraped_data.jsonl", "a") as f:
                        f.write(json.dumps(fallback_content) + "\n")
                    print("✅ Saved fallback content (raw markdown) to file")
                    sys.stdout.flush()
            except Exception as e:
                print(f"❌ Failed to parse extracted content: {e}")
                import traceback
                traceback.print_exc()
                
                # Try saving raw markdown as last resort
                try:
                    print("[SAVE] Attempting to save raw result as last resort...")
                    fallback_content = {
                        "url": result.url,
                        "error": str(e),
                        "raw_extracted_content": str(result.extracted_content)[:1000] if result.extracted_content else "No content",
                        "extraction_method": "error_fallback"
                    }
                    with open("esri_scraped_data.jsonl", "a") as f:
                        f.write(json.dumps(fallback_content) + "\n")
                    print("✅ Saved error fallback content to file")
                except Exception as e2:
                    print(f"❌ Even fallback save failed: {e2}")
                sys.stdout.flush()

            print("[LLM] Showing usage statistics...")
            sys.stdout.flush()
            llm_strategy.show_usage()
        else:
            print(f"❌ Crawl error: {result.error_message}")
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())
