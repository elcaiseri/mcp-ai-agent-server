"""Web content fetching tool."""
import httpx
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

class WebFetcherTool:
    """Tool for fetching and parsing web content."""
    
    async def fetch_webpage(
        self, 
        url: str, 
        extract_text: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch content from a webpage.
        
        Args:
            url: URL to fetch
            extract_text: If True, extract and clean text content
            
        Returns:
            Webpage content and metadata
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (compatible; MCPBot/1.0)"
                    },
                    timeout=15.0
                )
                response.raise_for_status()
                
                content_type = response.headers.get("content-type", "")
                
                result = {
                    "success": True,
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "content_type": content_type,
                    "error": None
                }
                
                if "text/html" in content_type and extract_text:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text
                    text = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    result["text"] = text[:5000]  # Limit to 5000 chars
                    result["title"] = soup.title.string if soup.title else None
                    result["full_length"] = len(text)
                else:
                    result["raw_content"] = response.text[:5000]
                
                return result
                
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "url": url,
                "error": f"HTTP error: {e.response.status_code}",
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Error fetching webpage: {str(e)}"
            }
    
    async def download_file(self, url: str, save_path: str) -> Dict[str, Any]:
        """
        Download a file from a URL.
        
        Args:
            url: URL to download from
            save_path: Local path to save file
            
        Returns:
            Download result
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                return {
                    "success": True,
                    "url": url,
                    "save_path": save_path,
                    "size": len(response.content),
                    "error": None
                }
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Error downloading file: {str(e)}"
            }

web_fetcher = WebFetcherTool()
