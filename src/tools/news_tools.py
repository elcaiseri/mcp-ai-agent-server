"""News fetching tool."""

import httpx
from typing import Dict, Any
from ..utils.config import config


class NewsTool:
    """Tool for fetching news articles."""

    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"

    async def fetch_news(
        self, topic: str, limit: int = 5, language: str = "en"
    ) -> Dict[str, Any]:
        """
        Fetch news articles on a topic.

        Args:
            topic: Search query/topic
            limit: Number of articles to return
            language: Language code (default: en)

        Returns:
            Dictionary with news articles
        """
        if not self.api_key:
            return {
                "error": "News API key not configured",
                "topic": topic,
                "articles": [],
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": topic,
                        "apiKey": self.api_key,
                        "language": language,
                        "pageSize": limit,
                        "sortBy": "publishedAt",
                    },
                    timeout=15.0,
                )
                response.raise_for_status()
                data = response.json()

                articles = []
                for article in data.get("articles", [])[:limit]:
                    articles.append(
                        {
                            "title": article.get("title"),
                            "description": article.get("description"),
                            "url": article.get("url"),
                            "source": article.get("source", {}).get("name"),
                            "published_at": article.get("publishedAt"),
                            "author": article.get("author"),
                        }
                    )

                return {
                    "topic": topic,
                    "total_results": data.get("totalResults", 0),
                    "articles": articles,
                    "error": None,
                }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP error: {e.response.status_code}",
                "topic": topic,
                "articles": [],
            }
        except Exception as e:
            return {
                "error": f"Error fetching news: {str(e)}",
                "topic": topic,
                "articles": [],
            }


news_tool = NewsTool()
