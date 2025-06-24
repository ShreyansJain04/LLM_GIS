import asyncio
import json
import os
import sys
from datetime import datetime

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

BASE_URL = "https://www.esri.com/en-us/arcgis/products/arcgis-pro/resources"

async def main():
    print("[INIT] Starting simple crawl (no LLM extraction)...")
    sys.stdout.flush()
    
    # Simple crawl configuration without LLM extraction
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        exclude_external_links=True,
        verbose=True,
        page_timeout=30000,  # 30 seconds timeout
        delay_before_return_html=3000,  # Wait 3 seconds for JS to load
        js_code="window.scrollTo(0, document.body.scrollHeight);"  # Scroll to load content
    )

    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        print("[CRAWL] Starting to crawl the website...")
        sys.stdout.flush()
        
        result = await crawler.arun(url=BASE_URL, config=crawl_config)
        
        print(f"[DEBUG] result.success: {result.success}")
        sys.stdout.flush()

        if result.success:
            print("[SAVE] Processing and saving crawled content...")
            print(f"[DEBUG] Available result attributes: {dir(result)}")
            print(f"[DEBUG] Has markdown: {hasattr(result, 'markdown')}")
            print(f"[DEBUG] Has cleaned_html: {hasattr(result, 'cleaned_html')}")
            print(f"[DEBUG] Has fit_markdown: {hasattr(result, 'fit_markdown')}")
            if hasattr(result, 'markdown'):
                print(f"[DEBUG] Markdown type: {type(result.markdown)}")
                if hasattr(result.markdown, 'fit_markdown'):
                    print(f"[DEBUG] fit_markdown length: {len(result.markdown.fit_markdown) if result.markdown.fit_markdown else 0}")
                if hasattr(result.markdown, 'raw_markdown'):
                    print(f"[DEBUG] raw_markdown length: {len(result.markdown.raw_markdown) if result.markdown.raw_markdown else 0}")
            sys.stdout.flush()
            
            # Try multiple ways to extract content
            markdown_content = ""
            text_content = ""
            
            # Method 1: Try fit_markdown
            if hasattr(result, 'markdown') and result.markdown and hasattr(result.markdown, 'fit_markdown'):
                markdown_content = result.markdown.fit_markdown or ""
            
            # Method 2: Try raw_markdown
            if not markdown_content and hasattr(result, 'markdown') and result.markdown and hasattr(result.markdown, 'raw_markdown'):
                markdown_content = result.markdown.raw_markdown or ""
            
            # Method 3: Try cleaned_html
            if hasattr(result, 'cleaned_html') and result.cleaned_html:
                text_content = result.cleaned_html[:5000]  # First 5000 chars
            
            # Method 4: Extract text from raw HTML (as last resort)
            if not markdown_content and not text_content and hasattr(result, 'html') and result.html:
                # Simple text extraction from HTML
                import re
                html_text = re.sub(r'<[^>]+>', ' ', result.html)  # Remove HTML tags
                html_text = re.sub(r'\s+', ' ', html_text)  # Normalize whitespace
                text_content = html_text[:5000]  # First 5000 chars
            
            print(f"[DEBUG] Final markdown_content length: {len(markdown_content)}")
            print(f"[DEBUG] Final text_content length: {len(text_content)}")
            sys.stdout.flush()
            
            # Create structured data from the crawl result
            content = {
                "url": result.url,
                "title": result.metadata.get("title", "No title") if result.metadata else "No metadata",
                "timestamp": datetime.now().isoformat(),
                "extraction_method": "simple_crawl",
                "markdown_content": markdown_content,
                "text_content": text_content,
                "markdown_length": len(markdown_content),
                "text_length": len(text_content),
                "links_found": len(result.links.get("internal", [])) if result.links else 0,
                "success": result.success,
                "raw_html_length": len(result.html) if hasattr(result, 'html') and result.html else 0
            }
            
            # Save to JSONL file
            try:
                print(f"[SAVE] Writing to esri_simple_scraped_data.jsonl...")
                sys.stdout.flush()
                
                with open("esri_simple_scraped_data.jsonl", "a") as f:
                    f.write(json.dumps(content) + "\n")
                
                print(f"✅ Successfully saved content to file")
                print(f"📊 Title: {content['title']}")
                print(f"📊 Markdown length: {content['markdown_length']} characters")
                print(f"📊 Text length: {content['text_length']} characters")
                print(f"📊 Links found: {content['links_found']}")
                print(f"📊 Raw HTML length: {content['raw_html_length']} characters")
                sys.stdout.flush()
                
            except Exception as e:
                print(f"❌ Failed to save content: {e}")
                import traceback
                traceback.print_exc()
                sys.stdout.flush()
        else:
            print(f"❌ Crawl error: {result.error_message}")
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main()) 