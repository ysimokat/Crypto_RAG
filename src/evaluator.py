import re
from typing import List, Dict, Any
from dataclasses import dataclass
from argument_generator import Argument
import openai
from config import Config

@dataclass
class EvaluationMetrics:
    clarity_score: float
    logic_score: float
    evidence_score: float
    persuasiveness_score: float
    overall_score: float
    feedback: str

class ArgumentEvaluator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
    
    def evaluate_argument(self, argument: Argument) -> EvaluationMetrics:
        rule_based_score = self._rule_based_evaluation(argument)
        
        if self.api_key:
            llm_score = self._llm_evaluation(argument)
            combined_score = self._combine_scores(rule_based_score, llm_score)
        else:
            combined_score = rule_based_score
        
        return combined_score
    
    def _rule_based_evaluation(self, argument: Argument) -> EvaluationMetrics:
        clarity_score = self._evaluate_clarity(argument.content)
        logic_score = self._evaluate_logic(argument.content)
        evidence_score = self._evaluate_evidence(argument)
        persuasiveness_score = self._evaluate_persuasiveness(argument.content)
        
        overall_score = (clarity_score + logic_score + evidence_score + persuasiveness_score) / 4
        
        feedback = self._generate_rule_based_feedback(
            clarity_score, logic_score, evidence_score, persuasiveness_score
        )
        
        return EvaluationMetrics(
            clarity_score=clarity_score,
            logic_score=logic_score,
            evidence_score=evidence_score,
            persuasiveness_score=persuasiveness_score,
            overall_score=overall_score,
            feedback=feedback
        )
    
    def _evaluate_clarity(self, content: str) -> float:
        score = 0.5
        
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if 10 <= avg_sentence_length <= 25:
            score += 0.2
        
        transition_words = ['however', 'furthermore', 'moreover', 'therefore', 'consequently', 'additionally']
        if any(word in content.lower() for word in transition_words):
            score += 0.2
        
        if content.count(',') > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_logic(self, content: str) -> float:
        score = 0.4
        
        logical_indicators = ['because', 'since', 'therefore', 'thus', 'consequently', 'as a result']
        logical_count = sum(1 for indicator in logical_indicators if indicator in content.lower())
        score += min(logical_count * 0.1, 0.4)
        
        if re.search(r'\b(first|second|third|finally)\b', content.lower()):
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_evidence(self, argument: Argument) -> float:
        score = 0.3
        
        citation_count = len(argument.citations)
        score += min(citation_count * 0.15, 0.4)
        
        if 'according to' in argument.content.lower() or 'research shows' in argument.content.lower():
            score += 0.2
        
        numbers_pattern = r'\b\d+(?:\.\d+)?%?\b'
        if re.search(numbers_pattern, argument.content):
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_persuasiveness(self, content: str) -> float:
        score = 0.4
        
        persuasive_words = ['significant', 'crucial', 'essential', 'important', 'compelling', 'overwhelming']
        persuasive_count = sum(1 for word in persuasive_words if word in content.lower())
        score += min(persuasive_count * 0.05, 0.3)
        
        if content.endswith('!') or '!' in content:
            score += 0.1
        
        rhetorical_patterns = ['why should', 'imagine if', 'consider this']
        if any(pattern in content.lower() for pattern in rhetorical_patterns):
            score += 0.2
        
        return min(score, 1.0)
    
    def _llm_evaluation(self, argument: Argument) -> EvaluationMetrics:
        prompt = f"""
Evaluate the following argument on a scale of 0.0 to 1.0 for each criterion:

Argument: {argument.content}

Citations: {'; '.join(argument.citations)}

Please rate:
1. Clarity (0.0-1.0): How clear and understandable is the argument?
2. Logic (0.0-1.0): How logical and well-structured is the reasoning?
3. Evidence (0.0-1.0): How well does it use evidence and citations?
4. Persuasiveness (0.0-1.0): How convincing is the argument?

Provide feedback in this format:
Clarity: X.X
Logic: X.X
Evidence: X.X
Persuasiveness: X.X
Feedback: [Brief explanation of strengths and weaknesses]
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert argument evaluator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            evaluation_text = response.choices[0].message.content
            return self._parse_llm_evaluation(evaluation_text)
            
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return self._rule_based_evaluation(argument)
    
    def _parse_llm_evaluation(self, evaluation_text: str) -> EvaluationMetrics:
        try:
            clarity_match = re.search(r'Clarity:\s*(\d+\.?\d*)', evaluation_text)
            logic_match = re.search(r'Logic:\s*(\d+\.?\d*)', evaluation_text)
            evidence_match = re.search(r'Evidence:\s*(\d+\.?\d*)', evaluation_text)
            persuasiveness_match = re.search(r'Persuasiveness:\s*(\d+\.?\d*)', evaluation_text)
            feedback_match = re.search(r'Feedback:\s*(.+)', evaluation_text, re.DOTALL)
            
            clarity_score = float(clarity_match.group(1)) if clarity_match else 0.5
            logic_score = float(logic_match.group(1)) if logic_match else 0.5
            evidence_score = float(evidence_match.group(1)) if evidence_match else 0.5
            persuasiveness_score = float(persuasiveness_match.group(1)) if persuasiveness_match else 0.5
            feedback = feedback_match.group(1).strip() if feedback_match else "No feedback available"
            
            overall_score = (clarity_score + logic_score + evidence_score + persuasiveness_score) / 4
            
            return EvaluationMetrics(
                clarity_score=clarity_score,
                logic_score=logic_score,
                evidence_score=evidence_score,
                persuasiveness_score=persuasiveness_score,
                overall_score=overall_score,
                feedback=feedback
            )
        except:
            return EvaluationMetrics(0.5, 0.5, 0.5, 0.5, 0.5, "Evaluation parsing failed")
    
    def _combine_scores(self, rule_based: EvaluationMetrics, llm_based: EvaluationMetrics) -> EvaluationMetrics:
        weight_rule = 0.4
        weight_llm = 0.6
        
        return EvaluationMetrics(
            clarity_score=weight_rule * rule_based.clarity_score + weight_llm * llm_based.clarity_score,
            logic_score=weight_rule * rule_based.logic_score + weight_llm * llm_based.logic_score,
            evidence_score=weight_rule * rule_based.evidence_score + weight_llm * llm_based.evidence_score,
            persuasiveness_score=weight_rule * rule_based.persuasiveness_score + weight_llm * llm_based.persuasiveness_score,
            overall_score=weight_rule * rule_based.overall_score + weight_llm * llm_based.overall_score,
            feedback=llm_based.feedback
        )
    
    def _generate_rule_based_feedback(self, clarity: float, logic: float, evidence: float, persuasiveness: float) -> str:
        feedback_parts = []
        
        if clarity < 0.6:
            feedback_parts.append("Consider improving clarity with shorter sentences and clearer transitions.")
        if logic < 0.6:
            feedback_parts.append("Strengthen logical flow with more explicit reasoning connections.")
        if evidence < 0.6:
            feedback_parts.append("Add more citations and specific evidence to support claims.")
        if persuasiveness < 0.6:
            feedback_parts.append("Enhance persuasiveness with stronger language and rhetorical techniques.")
        
        if not feedback_parts:
            feedback_parts.append("Strong argument with good balance across all criteria.")
        
        return " ".join(feedback_parts)