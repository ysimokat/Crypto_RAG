import openai
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from retrieval import Source
from config import Config
import json

@dataclass
class Argument:
    stance: str
    content: str
    sources: List[Source]
    confidence_score: float
    citations: List[str]

class ArgumentGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
        self.model = Config.LLM_MODEL
        
    def generate_pro_con_arguments(self, topic: str, sources: List[Source]) -> Tuple[Argument, Argument]:
        relevant_sources = sources[:Config.MAX_SOURCES_PER_ARGUMENT]
        
        pro_argument = self._generate_argument(topic, relevant_sources, "pro")
        con_argument = self._generate_argument(topic, relevant_sources, "con")
        
        return pro_argument, con_argument
    
    def _generate_argument(self, topic: str, sources: List[Source], stance: str) -> Argument:
        context = self._prepare_context(sources)
        
        prompt = self._create_prompt(topic, context, stance)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert argumentative writer who creates well-reasoned, evidence-based arguments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=Config.ARGUMENT_MAX_LENGTH,
                temperature=0.7
            )
            
            argument_text = response.choices[0].message.content.strip()
            citations = self._extract_citations(argument_text, sources)
            
            return Argument(
                stance=stance,
                content=argument_text,
                sources=sources,
                confidence_score=0.8,
                citations=citations
            )
        except Exception as e:
            print(f"Error generating {stance} argument: {e}")
            return Argument(
                stance=stance,
                content=f"Unable to generate {stance} argument due to API error.",
                sources=sources,
                confidence_score=0.0,
                citations=[]
            )
    
    def _prepare_context(self, sources: List[Source]) -> str:
        context_parts = []
        for i, source in enumerate(sources):
            context_parts.append(f"Source {i+1}: {source.title}\n{source.content[:300]}...\nURL: {source.url}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, topic: str, context: str, stance: str) -> str:
        stance_instruction = {
            "pro": "supporting and advocating for",
            "con": "opposing and arguing against"
        }
        
        return f"""
Based on the following sources, write a compelling argument {stance_instruction[stance]} the topic: "{topic}"

Sources:
{context}

Instructions:
1. Create a logical, well-structured argument that takes a clear {stance} stance
2. Use evidence from the provided sources to support your points
3. Include specific references to sources (e.g., "According to Source 1...")
4. Make the argument persuasive but factual
5. Keep the argument under {Config.ARGUMENT_MAX_LENGTH} words
6. Structure with clear reasoning and evidence

Argument:
"""
    
    def _extract_citations(self, argument_text: str, sources: List[Source]) -> List[str]:
        citations = []
        for i, source in enumerate(sources):
            if f"Source {i+1}" in argument_text or source.title.split()[0] in argument_text:
                citations.append(f"[{i+1}] {source.title} - {source.url}")
        
        return citations

class LocalLLMGenerator:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.to(self.device)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_pro_con_arguments(self, topic: str, sources: List[Source]) -> Tuple[Argument, Argument]:
        relevant_sources = sources[:Config.MAX_SOURCES_PER_ARGUMENT]
        
        pro_argument = self._generate_local_argument(topic, relevant_sources, "pro")
        con_argument = self._generate_local_argument(topic, relevant_sources, "con")
        
        return pro_argument, con_argument
    
    def _generate_local_argument(self, topic: str, sources: List[Source], stance: str) -> Argument:
        context = "\n".join([f"{s.title}: {s.content[:200]}" for s in sources])
        
        prompt = f"Argument {stance} {topic} based on: {context[:500]}"
        
        inputs = self.tokenizer.encode(prompt, return_tensors='pt', max_length=512, truncation=True)
        inputs = inputs.to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + 150,
                num_return_sequences=1,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        argument_text = generated_text[len(prompt):].strip()
        
        return Argument(
            stance=stance,
            content=argument_text,
            sources=sources,
            confidence_score=0.6,
            citations=[f"[{i+1}] {s.url}" for i, s in enumerate(sources)]
        )