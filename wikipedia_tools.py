import wikipedia
from typing import List, Dict, Optional
import random

class WikipediaRetriever:
    def __init__(self, language='en'):
        """Initialize Wikipedia retriever with specified language."""
        wikipedia.set_lang(language)
        self.language = language
    
    def search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search Wikipedia for relevant articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing article info
        """
        try:
            # Search for articles
            search_results = wikipedia.search(query, results=max_results)
            articles = []
            
            for title in search_results:
                try:
                    # Get page summary
                    page = wikipedia.page(title, auto_suggest=False)
                    summary = wikipedia.summary(title, sentences=2, auto_suggest=False)
                    
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'url': page.url,
                        'categories': page.categories[:5] if page.categories else []
                    })
                except Exception as e:
                    continue
            
            return articles
        except Exception as e:
            return []
    
    def get_random_interesting_topic(self) -> Optional[Dict]:
        """
        Get a random interesting Wikipedia article for conversation starters.
        
        Returns:
            Dictionary with article info or None
        """
        interesting_topics = [
            "Artificial Intelligence", "Space exploration", "Ancient civilizations",
            "Modern technology", "Human psychology", "Natural phenomena",
            "Famous inventions", "Historical events", "Scientific discoveries",
            "Cultural movements", "Philosophy", "Mathematics", "Biology",
            "Physics", "Chemistry", "Astronomy", "Psychology", "Sociology"
        ]
        
        try:
            topic = random.choice(interesting_topics)
            articles = self.search_wikipedia(topic, max_results=1)
            
            if articles:
                return articles[0]
        except Exception:
            pass
        
        return None
    
    def get_related_topics(self, current_topic: str) -> List[str]:
        """
        Get related topics that could naturally flow from current conversation.
        
        Args:
            current_topic: Current conversation topic
            
        Returns:
            List of related topics
        """
        try:
            # Search for the current topic
            articles = self.search_wikipedia(current_topic, max_results=1)
            
            if articles and articles[0].get('categories'):
                # Get some categories that could lead to interesting conversations
                categories = articles[0]['categories']
                interesting_categories = [
                    cat for cat in categories 
                    if any(keyword in cat.lower() for keyword in [
                        'history', 'science', 'technology', 'culture', 'people',
                        'philosophy', 'art', 'music', 'literature', 'politics'
                    ])
                ]
                
                return interesting_categories[:3]
        except Exception:
            pass
        
        return []
    
    def format_wikipedia_info(self, articles: List[Dict], context: str = "") -> str:
        """
        Format Wikipedia articles into a readable string for Liora to use.
        
        Args:
            articles: List of article dictionaries
            context: Context for why this info is being retrieved
            
        Returns:
            Formatted string with Wikipedia information
        """
        if not articles:
            return ""
        
        formatted_info = f"📚 Wikipedia Info {context}:\n\n"
        
        for i, article in enumerate(articles, 1):
            formatted_info += f"{i}. **{article['title']}**: {article['summary']}\n"
            if article.get('url'):
                formatted_info += f"   Source: {article['url']}\n"
            formatted_info += "\n"
        
        return formatted_info

# Initialize the Wikipedia retriever
wikipedia_retriever = WikipediaRetriever()
