import logging
from typing import Any, Dict, List, Optional

from PIL import Image
from serpapi import GoogleSearch

from config import SERPAPI_API_KEY, SEARCH_NUM_RESULTS
from utils.image_utils import download_image

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching garments using Amazon (via SerpApi)."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Amazon search service.

        Args:
            api_key: SerpApi API key. If None, uses SERPAPI_API_KEY from config.
        """
        self.api_key = api_key or SERPAPI_API_KEY
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not set. Please set the environment variable.")

        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def search_garments(
        self,
        keywords: str,
        num_results: int = SEARCH_NUM_RESULTS,
        include_images: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search for garments using Amazon (SerpApi).

        Args:
            keywords: Search keywords
            num_results: Number of results to return
            include_images: Whether to include image URLs in results

        Returns:
            List of dicts with title, url, image_url, price, brand, etc.
        """
        # Check cache
        cache_key = f"{keywords}:{num_results}"
        if cache_key in self._cache:
            logger.info(f"Returning cached results for: {keywords}")
            return self._cache[cache_key]

        try:
            params = {
                "engine": "amazon",
                "k": keywords,
                "amazon_domain": "amazon.com",
                "api_key": self.api_key
            }

            search = GoogleSearch(params)
            results_dict = search.get_dict()
            organic_results = results_dict.get("organic_results", [])

            results = []

            # Process search results
            for result in organic_results[:num_results]:
                # Extract image URL - prefer thumbnail since it's most common
                image_url = result.get("thumbnail")
                
                item = {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("title", ""),  # Using title as snippet if not available
                    "image_url": image_url,
                    "price": result.get("price", ""),
                    "extracted_price": result.get("extracted_price"),
                    "old_price": result.get("old_price"),
                    "brand": result.get("brand", ""),
                    "rating": result.get("rating"),
                    "reviews": result.get("reviews"),
                    "bought_last_month": result.get("bought_last_month"),
                    "delivery": ", ".join(result.get("delivery", [])) if isinstance(result.get("delivery"), list) else result.get("delivery", ""),
                    "asin": result.get("asin"),
                }

                results.append(item)

            # Cache results
            self._cache[cache_key] = results
            logger.info(f"Found {len(results)} results for: {keywords}")

            return results

        except Exception as e:
            logger.error(f"Error searching for garments on Amazon: {e}")
            return []

    def search_with_multiple_keywords(
        self,
        keywords_list: List[str],
        results_per_keyword: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search with multiple keyword combinations and combine results.

        Args:
            keywords_list: List of keyword combinations to search
            results_per_keyword: Number of results per keyword

        Returns:
            Combined and deduplicated list of results
        """
        all_results = []
        seen_asins = set()

        for keywords in keywords_list:
            results = self.search_garments(keywords, num_results=results_per_keyword)

            for result in results:
                asin = result.get("asin", result.get("url", ""))
                if asin and asin not in seen_asins:
                    seen_asins.add(asin)
                    all_results.append(result)

        return all_results

    def search_tops(
        self,
        keywords: List[str],
        results_per_keyword: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for tops/shirts.

        Args:
            keywords: List of keyword combinations for tops
            results_per_keyword: Number of results per keyword

        Returns:
            List of top garment results
        """
        # Enhance keywords with top-specific terms if not already present
        top_terms = ["shirt", "t-shirt", "blouse", "top", "jacket", "sweater"]
        enhanced_keywords = []

        for kw in keywords:
            kw_lower = kw.lower()
            has_top_term = any(term in kw_lower for term in top_terms)
            if not has_top_term:
                enhanced_keywords.append(f"{kw} shirt top")
            else:
                enhanced_keywords.append(kw)

        return self.search_with_multiple_keywords(enhanced_keywords, results_per_keyword)

    def search_bottoms(
        self,
        keywords: List[str],
        results_per_keyword: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search specifically for bottoms/pants.

        Args:
            keywords: List of keyword combinations for bottoms
            results_per_keyword: Number of results per keyword

        Returns:
            List of bottom garment results
        """
        # Enhance keywords with bottom-specific terms if not already present
        bottom_terms = ["pants", "jeans", "shorts", "skirt", "trousers", "slacks"]
        enhanced_keywords = []

        for kw in keywords:
            kw_lower = kw.lower()
            has_bottom_term = any(term in kw_lower for term in bottom_terms)
            if not has_bottom_term:
                enhanced_keywords.append(f"{kw} pants shorts")
            else:
                enhanced_keywords.append(kw)

        return self.search_with_multiple_keywords(enhanced_keywords, results_per_keyword)

    def download_garment_image(self, url: str) -> Optional[Image.Image]:
        """
        Download a garment image from URL.

        Args:
            url: Image URL to download

        Returns:
            PIL Image or None if download failed
        """
        return download_image(url)

    def get_image_for_result(self, result: Dict[str, Any]) -> Optional[Image.Image]:
        """
        Get the image for a search result, downloading if necessary.

        Args:
            result: Search result dict with image_url

        Returns:
            PIL Image or None
        """
        image_url = result.get("image_url")
        if not image_url:
            return None

        return self.download_garment_image(image_url)

    def clear_cache(self):
        """Clear the search results cache."""
        self._cache.clear()
        logger.info("Search cache cleared")
