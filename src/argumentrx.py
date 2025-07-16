from typing import List, Dict, Any, Tuple
import json
from datetime import datetime
from retrieval import UnifiedRetriever, Source
from embeddings import EmbeddingManager
from argument_generator import ArgumentGenerator, LocalLLMGenerator, Argument
from evaluator import ArgumentEvaluator, EvaluationMetrics
from config import Config

class ArgumentRx:
    def __init__(self, use_openai: bool = True):
        self.retriever = UnifiedRetriever()
        self.embedding_manager = EmbeddingManager()
        
        if use_openai and Config.OPENAI_API_KEY:
            self.generator = ArgumentGenerator()
        else:
            self.generator = LocalLLMGenerator()
        
        self.evaluator = ArgumentEvaluator()
        
        try:
            self.embedding_manager.load_index()
        except:
            print("No existing index found. Will create new index when processing sources.")
    
    def generate_arguments(self, topic: str, use_cached: bool = True) -> Dict[str, Any]:
        print(f"Generating arguments for: {topic}")
        
        sources = self.retriever.retrieve_all(topic)
        print(f"Retrieved {len(sources)} sources")
        
        if not sources:
            return {
                'topic': topic,
                'error': 'No sources found for this topic',
                'timestamp': datetime.now().isoformat()
            }
        
        if not use_cached or self.embedding_manager.index is None:
            print("Creating new embedding index...")
            self.embedding_manager.create_index(sources)
            self.embedding_manager.save_index()
        
        relevant_sources = self.embedding_manager.search_similar(topic, Config.RETRIEVAL_TOP_K)
        print(f"Found {len(relevant_sources)} relevant sources")
        
        pro_argument, con_argument = self.generator.generate_pro_con_arguments(topic, relevant_sources)
        
        pro_evaluation = self.evaluator.evaluate_argument(pro_argument)
        con_evaluation = self.evaluator.evaluate_argument(con_argument)
        
        result = {
            'topic': topic,
            'arguments': {
                'pro': {
                    'content': pro_argument.content,
                    'citations': pro_argument.citations,
                    'evaluation': {
                        'overall_score': round(pro_evaluation.overall_score, 2),
                        'clarity': round(pro_evaluation.clarity_score, 2),
                        'logic': round(pro_evaluation.logic_score, 2),
                        'evidence': round(pro_evaluation.evidence_score, 2),
                        'persuasiveness': round(pro_evaluation.persuasiveness_score, 2),
                        'feedback': pro_evaluation.feedback
                    }
                },
                'con': {
                    'content': con_argument.content,
                    'citations': con_argument.citations,
                    'evaluation': {
                        'overall_score': round(con_evaluation.overall_score, 2),
                        'clarity': round(con_evaluation.clarity_score, 2),
                        'logic': round(con_evaluation.logic_score, 2),
                        'evidence': round(con_evaluation.evidence_score, 2),
                        'persuasiveness': round(con_evaluation.persuasiveness_score, 2),
                        'feedback': con_evaluation.feedback
                    }
                }
            },
            'sources': self._format_sources(relevant_sources),
            'metadata': {
                'total_sources_retrieved': len(sources),
                'sources_used': len(relevant_sources),
                'timestamp': datetime.now().isoformat(),
                'model_used': 'OpenAI' if isinstance(self.generator, ArgumentGenerator) else 'Local'
            }
        }
        
        return result
    
    def _format_sources(self, sources: List[Source]) -> List[Dict[str, Any]]:
        formatted_sources = []
        for i, source in enumerate(sources):
            formatted_sources.append({
                'id': i + 1,
                'title': source.title,
                'url': source.url,
                'type': source.source_type,
                'relevance_score': round(source.relevance_score, 3),
                'preview': source.content[:200] + "..." if len(source.content) > 200 else source.content
            })
        return formatted_sources
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_clean = results['topic'].replace(' ', '_').replace('/', '_')
            filename = f"results/{topic_clean}_{timestamp}.json"
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def get_source_transparency_report(self, results: Dict[str, Any]) -> str:
        report = f"# Source Transparency Report\n\n"
        report += f"**Topic:** {results['topic']}\n"
        report += f"**Generated:** {results['metadata']['timestamp']}\n"
        report += f"**Model:** {results['metadata']['model_used']}\n\n"
        
        report += f"## Source Overview\n"
        report += f"- Total sources retrieved: {results['metadata']['total_sources_retrieved']}\n"
        report += f"- Sources used in arguments: {results['metadata']['sources_used']}\n\n"
        
        report += f"## Sources Used\n\n"
        for source in results['sources']:
            report += f"### Source {source['id']}: {source['title']}\n"
            report += f"- **Type:** {source['type']}\n"
            report += f"- **URL:** {source['url']}\n"
            report += f"- **Relevance Score:** {source['relevance_score']}\n"
            report += f"- **Preview:** {source['preview']}\n\n"
        
        report += f"## Argument Quality Scores\n\n"
        report += f"### Pro Argument (Score: {results['arguments']['pro']['evaluation']['overall_score']})\n"
        report += f"- Clarity: {results['arguments']['pro']['evaluation']['clarity']}\n"
        report += f"- Logic: {results['arguments']['pro']['evaluation']['logic']}\n"
        report += f"- Evidence: {results['arguments']['pro']['evaluation']['evidence']}\n"
        report += f"- Persuasiveness: {results['arguments']['pro']['evaluation']['persuasiveness']}\n"
        report += f"- Feedback: {results['arguments']['pro']['evaluation']['feedback']}\n\n"
        
        report += f"### Con Argument (Score: {results['arguments']['con']['evaluation']['overall_score']})\n"
        report += f"- Clarity: {results['arguments']['con']['evaluation']['clarity']}\n"
        report += f"- Logic: {results['arguments']['con']['evaluation']['logic']}\n"
        report += f"- Evidence: {results['arguments']['con']['evaluation']['evidence']}\n"
        report += f"- Persuasiveness: {results['arguments']['con']['evaluation']['persuasiveness']}\n"
        report += f"- Feedback: {results['arguments']['con']['evaluation']['feedback']}\n"
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ArgumentRx - Generate fact-based arguments')
    parser.add_argument('topic', help='Topic to generate arguments for')
    parser.add_argument('--local', action='store_true', help='Use local LLM instead of OpenAI')
    parser.add_argument('--save', help='Save results to specified file')
    parser.add_argument('--transparency', action='store_true', help='Generate transparency report')
    
    args = parser.parse_args()
    
    argumentrx = ArgumentRx(use_openai=not args.local)
    results = argumentrx.generate_arguments(args.topic)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    print("\n" + "="*60)
    print(f"ARGUMENTS FOR: {results['topic']}")
    print("="*60)
    
    print(f"\n📈 PRO ARGUMENT (Score: {results['arguments']['pro']['evaluation']['overall_score']}):")
    print("-" * 40)
    print(results['arguments']['pro']['content'])
    print(f"\nCitations: {len(results['arguments']['pro']['citations'])}")
    for citation in results['arguments']['pro']['citations']:
        print(f"  {citation}")
    
    print(f"\n📉 CON ARGUMENT (Score: {results['arguments']['con']['evaluation']['overall_score']}):")
    print("-" * 40)
    print(results['arguments']['con']['content'])
    print(f"\nCitations: {len(results['arguments']['con']['citations'])}")
    for citation in results['arguments']['con']['citations']:
        print(f"  {citation}")
    
    print(f"\n📊 SOURCES USED: {len(results['sources'])}")
    for source in results['sources'][:3]:
        print(f"  {source['id']}. {source['title']} ({source['type']})")
    
    if args.save:
        saved_file = argumentrx.save_results(results, args.save)
        print(f"\n💾 Results saved to: {saved_file}")
    
    if args.transparency:
        report = argumentrx.get_source_transparency_report(results)
        report_file = args.save.replace('.json', '_transparency.md') if args.save else 'transparency_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📋 Transparency report saved to: {report_file}")

if __name__ == "__main__":
    main()