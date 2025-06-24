import os
import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import re

import re

def extract_url(md_string):
    # Find whatever is inside (...) in a Markdown link [text](...)
    match = re.search(r'\[[^\]]*\]\(([^)]*)\)', md_string)
    if match:
        raw_url = match.group(1).strip()
        # Remove any trailing "description"
        raw_url = re.sub(r'\s*".*"$', '', raw_url)
        # Remove invalid fragments like </...>
        cleaned_url = re.sub(r'</[^>]*>', '', raw_url)
        return cleaned_url
    return md_string


async def crawl_and_extract(url, prompt, browser_cfg):
    """
    Generic function to crawl a URL and extract information based on a prompt.
    """
    url = extract_url(url)

    print("Crawling URL:", url)

    # Define the LLM extraction strategy
    llm_config = LLMConfig(
        provider="ollama/gemma3:27b",
        api_token="api"
    )
    
    llm_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        extraction_type="block",
        instruction=prompt,  
        chunk_token_threshold=100000,  # Increased for more content per chunk
        overlap_rate=0.2, 
        apply_chunking=True,  
        input_format="markdown",
        extra_args={"temperature": 0.0, "max_tokens": 100000},  # Increased for longer responses
        verbose=True,
    )

    # Configure the crawler
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        excluded_tags=["form", "header", "footer"],
    )


    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Crawl the URL and extract information based on the prompt
        result = await crawler.arun(url=url, config=crawl_config)

        if result.success:
            # Extract the result from the LLM output
            try:
                print("EXTRACTED CONTENT: ", result.extracted_content)
                # Parse the JSON response
                response_json = json.loads(result.extracted_content)
                
                # Combine all content from all chunks
                all_content = []
                for item in response_json:
                    if "content" in item:
                        if isinstance(item["content"], list):
                            all_content.extend(item["content"])
                        else:
                            all_content.append(item["content"])
                
                # Join all content pieces
                extracted_content = "\n\n".join(str(content).strip() for content in all_content if content)
                
                # If no content found, try getting the raw extracted content
                if not extracted_content:
                    extracted_content = result.extracted_content

                llm_strategy.show_usage()

                return extracted_content
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Error parsing extracted content: {e}")
                print("Raw extracted content:", result.extracted_content)
                # Return the raw content if parsing fails
                return result.extracted_content
        else:
            print("Error:", result.error_message)
            return None


async def extract_links_from_page(url, browser_cfg):
    """Extract relevant links from the main page"""
    
    link_extraction_prompt = """
    Find all links related to ArcGIS Pro tutorials, documentation, guides, training classes, and resources. 
    Extract the URLs only, one per line. Only include links that contain content about ArcGIS Pro.
    Return the links in this format:
    https://example.com/link1
    https://example.com/link2
    """
    
    print(f"🔍 Extracting links from: {url}")
    
    # Simple extraction without LLM - just get all links
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        excluded_tags=["form", "header", "footer"],
    )
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=url, config=crawl_config)
        
        if result.success and result.links:
            # Filter links that might contain ArcGIS Pro content
            relevant_links = []
            all_links = result.links.get('internal', []) + result.links.get('external', [])
            
            for link in all_links:
                link_url = link.get('href', '')
                link_text = link.get('text', '').lower()
                
                # Filter for relevant ArcGIS Pro content
                if any(keyword in link_url.lower() or keyword in link_text for keyword in [
                    'tutorial', 'guide', 'learn', 'training', 'documentation', 'course',
                    'arcgis-pro', 'gis-tutorial', 'getting-started', 'basics', 'workflow'
                ]):
                    if link_url.startswith(('http://', 'https://')):
                        relevant_links.append(link_url)
            
            return list(set(relevant_links))  # Remove duplicates
        
        return []

async def main():
    website_url = "https://www.esri.com/en-us/arcgis/products/arcgis-pro/resources"
    
    # Create a browser config
    browser_cfg = BrowserConfig(headless=True)
    
    # Initialize results storage
    results = []
    
    print("🚀 Starting ArcGIS Pro Deep Content Extraction")
    
    # Step 1: Extract links from the main page
    print("\n📋 Step 1: Extracting relevant links from main page...")
    links = await extract_links_from_page(website_url, browser_cfg)
    
    # Add the main page itself to the list
    all_urls_to_process = [website_url] + links[:10]  # Limit to first 10 links to avoid too many requests
    
    print(f"Found {len(links)} relevant links. Processing {len(all_urls_to_process)} pages total.")
    
    # Step 2: Extract content from each page
    content_extraction_prompt = """
    Extract all detailed content related to ArcGIS Pro from this page. Include:
    - Tutorial steps and instructions
    - Documentation and guides
    - Training material
    - Tips and best practices
    - Any technical information
    
    Format the output as clean, organized markdown. Include headers, bullet points, and code blocks where appropriate.
    If this page doesn't contain ArcGIS Pro content, return "No ArcGIS Pro content found." Only return content that is relevant for ArcGIS Pro version 3.4.0
    """

    for i, url in enumerate(all_urls_to_process):
        print(f"\n📄 Processing page {i+1}/{len(all_urls_to_process)}: {url}")
        
        try:
            # Extract content from this page
            result = await crawl_and_extract(url, content_extraction_prompt, browser_cfg)
            
            # Save result
            step_result = {
                "step": i + 1,
                "url": url,
                "page_type": "main_page" if i == 0 else "linked_page",
                "result": result,
                "success": result is not None and result != "No ArcGIS Pro content found."
            }
            results.append(step_result)
            
            if step_result["success"]:
                print(f"✅ Successfully extracted content ({len(result)} characters)")
            else:
                print(f"⚠️ No relevant content found")
                
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
            results.append({
                "step": i + 1,
                "url": url,
                "page_type": "main_page" if i == 0 else "linked_page", 
                "result": f"Error: {e}",
                "success": False
            })

    # Save all results to files
    print(f"\n💾 Saving results from {len(results)} pages...")
    
    # 1. Save as JSON
    with open("arcgis_pro_content.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 2. Save as readable text
    with open("arcgis_pro_content.txt", "w", encoding="utf-8") as f:
        f.write("=== ARCGIS PRO CONTENT EXTRACTION RESULTS ===\n\n")
        
        successful_pages = [r for r in results if r['success']]
        f.write(f"Successfully processed: {len(successful_pages)}/{len(results)} pages\n\n")
        
        for result in results:
            f.write(f"Page {result['step']}: {result['page_type']}\n")
            f.write(f"URL: {result['url']}\n")
            f.write(f"Success: {result['success']}\n")
            f.write("=" * 80 + "\n")
            if result['success']:
                f.write("EXTRACTED CONTENT:\n")
                f.write("=" * 80 + "\n")
                f.write(f"{result['result']}\n")
            else:
                f.write(f"ERROR: {result['result']}\n")
            f.write("=" * 80 + "\n\n")
    
    # 3. Save each page's content as separate markdown files
    content_count = 0
    for result in results:
        if result['success'] and result['result']:
            # Create safe filename from URL
            url_part = result['url'].split('/')[-1] or 'main_page'
            url_part = ''.join(c for c in url_part if c.isalnum() or c in '-_')[:50]
            filename = f"page_{result['step']:02d}_{url_part}.md"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# ArcGIS Pro Content - Page {result['step']}\n\n")
                f.write(f"**Source URL:** {result['url']}\n\n")
                f.write(f"**Page Type:** {result['page_type']}\n\n")
                f.write(f"---\n\n")
                f.write(result['result'])
            content_count += 1
    
    # 4. Create a combined markdown file with all content
    with open("arcgis_pro_complete_guide.md", "w", encoding="utf-8") as f:
        f.write("# Complete ArcGIS Pro Resources Guide\n\n")
        f.write(f"*Extracted from {len(results)} pages*\n\n")
        f.write("## Table of Contents\n\n")
        
        # Create table of contents
        for result in results:
            if result['success']:
                url_title = result['url'].split('/')[-1] or 'Main Page'
                f.write(f"- [Page {result['step']}: {url_title}](#page-{result['step']})\n")
        
        f.write("\n---\n\n")
        
        # Add all content
        for result in results:
            if result['success']:
                url_title = result['url'].split('/')[-1] or 'Main Page'
                f.write(f"## Page {result['step']}: {url_title}\n\n")
                f.write(f"**Source:** {result['url']}\n\n")
                f.write(result['result'])
                f.write("\n\n---\n\n")
    
    print(f"\n📁 Results saved to:")
    print(f"   • arcgis_pro_content.json (structured data)")
    print(f"   • arcgis_pro_content.txt (readable format)")
    print(f"   • page_XX_*.md ({content_count} individual page files)")
    print(f"   • arcgis_pro_complete_guide.md (combined guide)")
    print(f"\n🎉 Successfully extracted content from {len([r for r in results if r['success']])} pages!")


if __name__ == "__main__":
    asyncio.run(main())
