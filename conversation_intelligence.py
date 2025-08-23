import random
from typing import List, Dict, Optional, Tuple
from wikipedia_tools import wikipedia_retriever

class ConversationIntelligence:
    def __init__(self):
        """Initialize conversation intelligence system."""
        self.conversation_topics = []
        self.topic_confidence = 0.0
        self.should_introduce_wikipedia = False
        
    def analyze_conversation_context(self, user_message: str, conversation_history: str) -> Dict:
        """
        Analyze the current conversation context to determine if Wikipedia info should be introduced.
        
        Args:
            user_message: Current user message
            conversation_history: Recent conversation history
            
        Returns:
            Dictionary with analysis results
        """
        # Keywords that might indicate Wikipedia knowledge would be valuable
        wikipedia_triggers = [
            "what is", "who is", "tell me about", "explain", "how does",
            "history of", "definition of", "meaning of", "facts about",
            "information about", "details about", "background on"
        ]
        
        # Check if user is asking for information
        user_asking_for_info = any(trigger in user_message.lower() for trigger in wikipedia_triggers)
        
        # Check conversation length and topic variety
        conversation_length = len(conversation_history.split('\n')) if conversation_history else 0
        
        # Determine if we should introduce Wikipedia info
        should_introduce = (
            user_asking_for_info or 
            (conversation_length > 4 and random.random() < 0.3) or  # 30% chance after 4+ messages
            random.random() < 0.1  # 10% random chance for natural topic shifts
        )
        
        return {
            'should_introduce_wikipedia': should_introduce,
            'user_asking_for_info': user_asking_for_info,
            'conversation_length': conversation_length,
            'confidence': random.uniform(0.6, 0.9) if should_introduce else 0.0
        }
    
    def extract_topic_from_message(self, message: str) -> Optional[str]:
        """
        Extract potential Wikipedia search topics from user message.
        
        Args:
            message: User message
            
        Returns:
            Extracted topic or None
        """
        # Simple topic extraction - can be enhanced with NLP
        words = message.lower().split()
        
        # Look for capitalized words (potential proper nouns)
        potential_topics = [word for word in words if word[0].isupper() and len(word) > 2]
        
        # Look for phrases after "what is", "who is", etc.
        info_phrases = ["what is", "who is", "tell me about", "explain"]
        for phrase in info_phrases:
            if phrase in message.lower():
                start_idx = message.lower().find(phrase) + len(phrase)
                topic = message[start_idx:].strip().split('.')[0].split('?')[0]
                if len(topic) > 2:
                    return topic
        
        # Return first potential topic or None
        return potential_topics[0] if potential_topics else None
    
    def decide_wikipedia_introduction(self, user_message: str, conversation_history: str) -> Tuple[bool, Optional[str]]:
        """
        Decide whether to introduce Wikipedia information and what topic to search.
        
        Args:
            user_message: Current user message
            conversation_history: Recent conversation history
            
        Returns:
            Tuple of (should_introduce, topic_to_search)
        """
        analysis = self.analyze_conversation_context(user_message, conversation_history)
        
        if not analysis['should_introduce_wikipedia']:
            return False, None
        
        # Extract topic from user message
        topic = self.extract_topic_from_message(user_message)
        
        if topic:
            return True, topic
        
        # If no specific topic, get a random interesting topic
        if random.random() < 0.4:  # 40% chance to introduce random topic
            random_article = wikipedia_retriever.get_random_interesting_topic()
            if random_article:
                return True, random_article['title']
        
        return False, None
    
    def generate_topic_transition(self, current_topic: str, wikipedia_info: str) -> str:
        """
        Generate a natural transition to introduce Wikipedia information.
        
        Args:
            current_topic: Current conversation topic
            wikipedia_info: Wikipedia information to introduce
            
        Returns:
            Transition text
        """
        transitions = [
            f"Oh hey, speaking of {current_topic}, I just remembered something fascinating!",
            f"Wait, that reminds me of something I read about {current_topic}!",
            f"You know what's interesting about {current_topic}?",
            f"Actually, let me share something cool I know about {current_topic}!",
            f"That's funny, because I was just thinking about {current_topic}!",
            f"Speaking of which, did you know about {current_topic}?",
            f"Oh! That totally connects to something I know about {current_topic}!",
            f"Random thought, but {current_topic} is actually pretty fascinating!",
            f"Hold up, this reminds me of something about {current_topic}!",
            f"You know what's wild about {current_topic}?"
        ]
        
        return random.choice(transitions)
    
    def should_continue_wikipedia_topic(self, conversation_history: str) -> bool:
        """
        Decide if we should continue exploring the current Wikipedia topic.
        
        Args:
            conversation_history: Recent conversation history
            
        Returns:
            True if we should continue, False otherwise
        """
        # Check if the last few messages are about the same topic
        recent_messages = conversation_history.split('\n')[-6:]  # Last 6 messages
        
        # Simple heuristic: if we've been talking about Wikipedia topics recently, maybe switch
        wikipedia_mentions = sum(1 for msg in recent_messages if '📚' in msg or 'wikipedia' in msg.lower())
        
        return wikipedia_mentions < 2  # Don't overdo Wikipedia topics

# Initialize conversation intelligence
conversation_intelligence = ConversationIntelligence()
