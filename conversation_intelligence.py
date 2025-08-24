import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
from collections import defaultdict, Counter
import pickle

class ConversationIntelligence:
    """Enhanced conversation intelligence with learning capabilities"""
    
    def __init__(self):
        self.learning_data_file = "liora_learning_data.pkl"
        self.conversation_patterns_file = "conversation_patterns.json"
        self.user_preferences_file = "user_preferences.json"
        
        # Initialize learning data
        self.learning_data = self.load_learning_data()
        self.conversation_patterns = self.load_conversation_patterns()
        self.user_preferences = self.load_user_preferences()
        
        # Learning metrics
        self.interaction_count = self.learning_data.get('interaction_count', 0)
        self.successful_responses = self.learning_data.get('successful_responses', 0)
        self.user_satisfaction_scores = self.learning_data.get('user_satisfaction_scores', [])
        
        # Conversation analysis
        self.topic_frequency = self.learning_data.get('topic_frequency', Counter())
        self.response_effectiveness = self.learning_data.get('response_effectiveness', {})
        self.user_engagement_patterns = self.learning_data.get('user_engagement_patterns', {})
        
        # Adaptive learning parameters
        self.learning_rate = 0.1
        self.memory_decay = 0.95
        self.min_interactions_for_learning = 5
    
    def load_learning_data(self) -> Dict:
        """Load learning data from file"""
        try:
            if os.path.exists(self.learning_data_file):
                with open(self.learning_data_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"Error loading learning data: {e}")
        return {}
    
    def save_learning_data(self):
        """Save learning data to file"""
        try:
            learning_data = {
                'interaction_count': self.interaction_count,
                'successful_responses': self.successful_responses,
                'user_satisfaction_scores': self.user_satisfaction_scores,
                'topic_frequency': self.topic_frequency,
                'response_effectiveness': self.response_effectiveness,
                'user_engagement_patterns': self.user_engagement_patterns,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_data_file, 'wb') as f:
                pickle.dump(learning_data, f)
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def load_conversation_patterns(self) -> Dict:
        """Load conversation patterns from file"""
        try:
            if os.path.exists(self.conversation_patterns_file):
                with open(self.conversation_patterns_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading conversation patterns: {e}")
        return {
            'successful_openings': [],
            'effective_responses': [],
            'user_preferences': {},
            'conversation_flows': []
        }
    
    def save_conversation_patterns(self):
        """Save conversation patterns to file"""
        try:
            with open(self.conversation_patterns_file, 'w') as f:
                json.dump(self.conversation_patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving conversation patterns: {e}")
    
    def load_user_preferences(self) -> Dict:
        """Load user preferences from file"""
        try:
            if os.path.exists(self.user_preferences_file):
                with open(self.user_preferences_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading user preferences: {e}")
        return {
            'preferred_topics': [],
            'communication_style': 'neutral',
            'response_length': 'medium',
            'humor_level': 'moderate',
            'formality_level': 'casual'
        }
    
    def save_user_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.user_preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving user preferences: {e}")
    
    def analyze_conversation(self, conversation_history: str) -> Dict:
        """Analyze conversation for learning opportunities"""
        analysis = {
            'topics': self.extract_topics(conversation_history),
            'sentiment': self.analyze_sentiment(conversation_history),
            'engagement_level': self.assess_engagement(conversation_history),
            'conversation_flow': self.analyze_conversation_flow(conversation_history),
            'user_communication_style': self.detect_communication_style(conversation_history)
        }
        return analysis
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract main topics from conversation"""
        # Simple topic extraction based on keywords
        topic_keywords = {
            'technology': ['ai', 'programming', 'computer', 'software', 'tech', 'code'],
            'science': ['science', 'research', 'experiment', 'discovery', 'theory'],
            'entertainment': ['movie', 'music', 'game', 'show', 'entertainment', 'fun'],
            'personal': ['life', 'family', 'friend', 'personal', 'experience'],
            'work': ['work', 'job', 'career', 'business', 'professional'],
            'education': ['learn', 'study', 'education', 'school', 'knowledge'],
            'current_events': ['news', 'current', 'recent', 'today', 'latest'],
            'philosophy': ['think', 'philosophy', 'meaning', 'purpose', 'existence']
        }
        
        text_lower = text.lower()
        found_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of conversation"""
        positive_words = ['good', 'great', 'awesome', 'amazing', 'love', 'like', 'happy', 'excited', 'wonderful']
        negative_words = ['bad', 'terrible', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'awful']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def assess_engagement(self, text: str) -> str:
        """Assess user engagement level"""
        engagement_indicators = {
            'high': ['!', '?', 'wow', 'amazing', 'really', 'tell me more', 'interesting'],
            'medium': ['ok', 'sure', 'yes', 'no', 'maybe'],
            'low': ['...', 'hmm', 'idk', 'whatever', 'fine']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for level, indicators in engagement_indicators.items():
            scores[level] = sum(1 for indicator in indicators if indicator in text_lower)
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'medium'
        
        for level, score in scores.items():
            if score == max_score:
                return level
    
    def analyze_conversation_flow(self, text: str) -> Dict:
        """Analyze conversation flow patterns"""
        lines = text.split('\n')
        user_messages = [line for line in lines if line.startswith('User:')]
        assistant_messages = [line for line in lines if line.startswith('Assistant:')]
        
        return {
            'message_count': len(lines),
            'user_message_count': len(user_messages),
            'assistant_message_count': len(assistant_messages),
            'average_user_message_length': sum(len(msg) for msg in user_messages) / max(len(user_messages), 1),
            'average_assistant_message_length': sum(len(msg) for msg in assistant_messages) / max(len(assistant_messages), 1),
            'conversation_depth': len(lines) // 2  # Rough estimate of conversation depth
        }
    
    def detect_communication_style(self, text: str) -> str:
        """Detect user's communication style"""
        formal_indicators = ['please', 'thank you', 'would you', 'could you', 'kindly']
        casual_indicators = ['hey', 'hi', 'cool', 'awesome', 'lol', 'omg', 'btw']
        technical_indicators = ['algorithm', 'function', 'method', 'parameter', 'variable', 'class']
        
        text_lower = text.lower()
        
        formal_score = sum(1 for indicator in formal_indicators if indicator in text_lower)
        casual_score = sum(1 for indicator in casual_indicators if indicator in text_lower)
        technical_score = sum(1 for indicator in technical_indicators if indicator in text_lower)
        
        if technical_score > max(formal_score, casual_score):
            return 'technical'
        elif formal_score > casual_score:
            return 'formal'
        else:
            return 'casual'
    
    def learn_from_interaction(self, user_message: str, assistant_response: str, 
                             conversation_history: str, user_feedback: Optional[str] = None):
        """Learn from each interaction to improve future responses"""
        # Increment interaction count
        self.interaction_count += 1
        
        # Analyze the interaction
        analysis = self.analyze_conversation(conversation_history)
        
        # Update topic frequency
        for topic in analysis['topics']:
            self.topic_frequency[topic] += 1
        
        # Assess response effectiveness
        effectiveness_score = self.assess_response_effectiveness(user_message, assistant_response, analysis)
        
        # Store effective response patterns
        if effectiveness_score > 0.7:  # High effectiveness threshold
            self.conversation_patterns['effective_responses'].append({
                'user_message': user_message,
                'assistant_response': assistant_response,
                'context': analysis,
                'effectiveness_score': effectiveness_score,
                'timestamp': datetime.now().isoformat()
            })
        
        # Update user preferences based on communication style
        detected_style = analysis['user_communication_style']
        if detected_style != self.user_preferences.get('communication_style'):
            self.user_preferences['communication_style'] = detected_style
        
        # Learn from user feedback if provided
        if user_feedback:
            self.learn_from_feedback(user_feedback, effectiveness_score)
        
        # Update engagement patterns
        self.user_engagement_patterns[analysis['engagement_level']] = \
            self.user_engagement_patterns.get(analysis['engagement_level'], 0) + 1
        
        # Save learning data periodically
        if self.interaction_count % 10 == 0:  # Save every 10 interactions
            self.save_learning_data()
            self.save_conversation_patterns()
            self.save_user_preferences()
    
    def assess_response_effectiveness(self, user_message: str, assistant_response: str, 
                                   analysis: Dict) -> float:
        """Assess how effective the assistant's response was"""
        effectiveness_score = 0.5  # Base score
        
        # Check if response addresses user's question/topic
        user_topics = self.extract_topics(user_message)
        response_topics = self.extract_topics(assistant_response)
        
        if user_topics and response_topics:
            topic_overlap = len(set(user_topics) & set(response_topics))
            effectiveness_score += 0.2 * (topic_overlap / len(user_topics))
        
        # Check response length appropriateness
        user_message_length = len(user_message)
        response_length = len(assistant_response)
        
        if user_message_length < 50 and response_length > 200:
            effectiveness_score -= 0.1  # Too verbose for short question
        elif user_message_length > 100 and response_length < 50:
            effectiveness_score -= 0.1  # Too brief for complex question
        
        # Check for engagement indicators in response
        engagement_words = ['interesting', 'fascinating', 'tell me more', 'what do you think']
        if any(word in assistant_response.lower() for word in engagement_words):
            effectiveness_score += 0.1
        
        # Check sentiment alignment
        user_sentiment = self.analyze_sentiment(user_message)
        response_sentiment = self.analyze_sentiment(assistant_response)
        
        if user_sentiment == response_sentiment:
            effectiveness_score += 0.1
        
        return min(1.0, max(0.0, effectiveness_score))
    
    def learn_from_feedback(self, feedback: str, effectiveness_score: float):
        """Learn from explicit user feedback"""
        feedback_lower = feedback.lower()
        
        if any(word in feedback_lower for word in ['good', 'great', 'excellent', 'perfect']):
            self.successful_responses += 1
            self.user_satisfaction_scores.append(1.0)
        elif any(word in feedback_lower for word in ['bad', 'terrible', 'wrong', 'incorrect']):
            self.user_satisfaction_scores.append(0.0)
        else:
            self.user_satisfaction_scores.append(effectiveness_score)
        
        # Keep only recent satisfaction scores (last 100)
        if len(self.user_satisfaction_scores) > 100:
            self.user_satisfaction_scores = self.user_satisfaction_scores[-100:]
    
    def get_adaptive_response_guidance(self, user_message: str, conversation_history: str) -> Dict:
        """Get adaptive guidance for crafting responses based on learned patterns"""
        analysis = self.analyze_conversation(conversation_history)
        
        guidance = {
            'preferred_topics': self.get_user_preferred_topics(),
            'communication_style': self.user_preferences.get('communication_style', 'casual'),
            'response_length': self.determine_optimal_response_length(user_message, analysis),
            'engagement_strategy': self.get_engagement_strategy(analysis),
            'personality_adjustment': self.get_personality_adjustment(analysis),
            'conversation_context': analysis
        }
        
        return guidance
    
    def get_user_preferred_topics(self) -> List[str]:
        """Get user's preferred topics based on learning"""
        return [topic for topic, count in self.topic_frequency.most_common(5)]
    
    def determine_optimal_response_length(self, user_message: str, analysis: Dict) -> str:
        """Determine optimal response length based on user patterns"""
        user_message_length = len(user_message)
        avg_user_length = analysis['conversation_flow'].get('average_user_message_length', 50)
        
        if user_message_length < 30 or avg_user_length < 40:
            return 'short'
        elif user_message_length > 100 or avg_user_length > 80:
            return 'long'
        else:
            return 'medium'
    
    def get_engagement_strategy(self, analysis: Dict) -> str:
        """Get engagement strategy based on user patterns"""
        engagement_level = analysis['engagement_level']
        
        if engagement_level == 'low':
            return 'increase_engagement'
        elif engagement_level == 'high':
            return 'maintain_momentum'
        else:
            return 'balanced'
    
    def get_personality_adjustment(self, analysis: Dict) -> Dict:
        """Get personality adjustments based on user preferences"""
        sentiment = analysis['sentiment']
        communication_style = analysis['user_communication_style']
        
        adjustments = {
            'humor_level': 'moderate',
            'formality_level': 'casual',
            'enthusiasm_level': 'normal'
        }
        
        # Adjust based on sentiment
        if sentiment == 'positive':
            adjustments['enthusiasm_level'] = 'high'
        elif sentiment == 'negative':
            adjustments['humor_level'] = 'low'
            adjustments['enthusiasm_level'] = 'low'
        
        # Adjust based on communication style
        if communication_style == 'formal':
            adjustments['formality_level'] = 'formal'
        elif communication_style == 'casual':
            adjustments['formality_level'] = 'very_casual'
        
        return adjustments
    
    def get_learning_insights(self) -> Dict:
        """Get insights about Liora's learning progress"""
        avg_satisfaction = sum(self.user_satisfaction_scores) / max(len(self.user_satisfaction_scores), 1)
        
        return {
            'total_interactions': self.interaction_count,
            'success_rate': self.successful_responses / max(self.interaction_count, 1),
            'average_satisfaction': avg_satisfaction,
            'top_topics': self.get_user_preferred_topics(),
            'engagement_distribution': dict(self.user_engagement_patterns),
            'learning_progress': 'beginner' if self.interaction_count < 50 else 'intermediate' if self.interaction_count < 200 else 'advanced'
        }
    
    def decide_wikipedia_introduction(self, prompt: str, conversation_history: str) -> Tuple[bool, Optional[str]]:
        """Enhanced decision making for Wikipedia introductions with learning"""
        # Original logic
        should_introduce = False
        topic = None
        
        # Check if user is asking for information
        info_keywords = ['what is', 'tell me about', 'explain', 'how does', 'why does', 'when did']
        if any(keyword in prompt.lower() for keyword in info_keywords):
            should_introduce = True
            
            # Extract potential topic
            words = prompt.lower().split()
            for i, word in enumerate(words):
                if word in ['what', 'tell', 'explain', 'how', 'why', 'when'] and i + 1 < len(words):
                    topic = words[i + 1]
                    break
        
        # Learning-based adjustments
        if should_introduce:
            # Check if user prefers Wikipedia information
            user_prefs = self.user_preferences
            if user_prefs.get('preferred_topics') and any(topic in user_prefs['preferred_topics'] for topic in self.extract_topics(prompt)):
                should_introduce = True
            else:
                # Reduce Wikipedia frequency if user engagement is low
                analysis = self.analyze_conversation(conversation_history)
                if analysis['engagement_level'] == 'low':
                    should_introduce = False
        
        return should_introduce, topic
    
    def generate_topic_transition(self, topic: str, wikipedia_info: str) -> str:
        """Generate natural topic transitions with learning"""
        # Get user's communication style preference
        style = self.user_preferences.get('communication_style', 'casual')
        
        if style == 'formal':
            return f"Speaking of {topic}, I found some interesting information that might be relevant to our conversation."
        elif style == 'technical':
            return f"Regarding {topic}, here's some technical background that could be useful."
        else:
            return f"Oh, by the way! I just remembered something fascinating about {topic} that I think you'd find interesting."

# Global instance
conversation_intelligence = ConversationIntelligence()
