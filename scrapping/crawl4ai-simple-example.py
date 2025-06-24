import asyncio
import json
import os

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

BASE_URL = "https://www.esri.com/en-us/arcgis/products/arcgis-pro/resources"

async def main():
    # Simple crawl configuration without LLM extraction
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        process_iframes=False,
        remove_overlay_elements=True,
        exclude_external_links=True,
        verbose=True
    )

    browser_cfg = BrowserConfig(headless=True, verbose=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=BASE_URL, config=crawl_config)

        if result.success:
            # Save the markdown content to a file
            with open("esri_markdown_content.txt", "w", encoding="utf-8") as f:
                f.write(result.markdown.fit_markdown)
            
            # Save basic information as JSON
            info = {
                "url": result.url,
                "title": result.metadata.get("title", "No title") if result.metadata else "No metadata",
                "markdown_length": len(result.markdown.fit_markdown),
                "links_found": len(result.links.get("internal", [])) if result.links else 0,
                "success": result.success
            }
            
            with open("esri_info.json", "w", encoding="utf-8") as f:
                json.dump(info, f, indent=2)
            
            print(f"✅ Successfully crawled {result.url}")
            print(f"📄 Markdown saved to: esri_markdown_content.txt ({len(result.markdown.fit_markdown)} characters)")
            print(f"📊 Info saved to: esri_info.json")
            print(f"🔗 Found {len(result.links.get('internal', [])) if result.links else 0} internal links")
            
        else:
            print(f"❌ Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main()) 