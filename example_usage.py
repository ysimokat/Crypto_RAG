#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from argumentrx import ArgumentRx

def example_basic_usage():
    print("=" * 60)
    print("ArgumentRx Basic Usage Example")
    print("=" * 60)
    
    argumentrx = ArgumentRx(use_openai=False)
    
    topic = "Bitcoin environmental impact"
    print(f"\nGenerating arguments for: {topic}")
    
    results = argumentrx.generate_arguments(topic)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    print(f"\n📈 PRO ARGUMENT:")
    print("-" * 40)
    print(results['arguments']['pro']['content'])
    print(f"Score: {results['arguments']['pro']['evaluation']['overall_score']}")
    
    print(f"\n📉 CON ARGUMENT:")
    print("-" * 40)
    print(results['arguments']['con']['content'])
    print(f"Score: {results['arguments']['con']['evaluation']['overall_score']}")
    
    print(f"\n📊 METADATA:")
    print(f"Sources retrieved: {results['metadata']['total_sources_retrieved']}")
    print(f"Sources used: {results['metadata']['sources_used']}")
    print(f"Model: {results['metadata']['model_used']}")

def example_with_file_output():
    print("\n" + "=" * 60)
    print("ArgumentRx File Output Example")
    print("=" * 60)
    
    argumentrx = ArgumentRx(use_openai=False)
    
    topic = "DeFi regulation necessity"
    results = argumentrx.generate_arguments(topic)
    
    if 'error' not in results:
        saved_file = argumentrx.save_results(results)
        print(f"Results saved to: {saved_file}")
        
        report = argumentrx.get_source_transparency_report(results)
        report_file = saved_file.replace('.json', '_transparency.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Transparency report saved to: {report_file}")

def example_crypto_topics():
    print("\n" + "=" * 60)
    print("Multiple Crypto Topics Example")
    print("=" * 60)
    
    topics = [
        "Proof of Work vs Proof of Stake",
        "Central Bank Digital Currencies adoption",
        "NFT market sustainability"
    ]
    
    argumentrx = ArgumentRx(use_openai=False)
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{i}. Topic: {topic}")
        results = argumentrx.generate_arguments(topic)
        
        if 'error' not in results:
            pro_score = results['arguments']['pro']['evaluation']['overall_score']
            con_score = results['arguments']['con']['evaluation']['overall_score']
            sources_count = results['metadata']['sources_used']
            
            print(f"   Pro score: {pro_score} | Con score: {con_score} | Sources: {sources_count}")
        else:
            print(f"   Error: {results['error']}")

def example_evaluation_analysis():
    print("\n" + "=" * 60)
    print("Evaluation Analysis Example")
    print("=" * 60)
    
    argumentrx = ArgumentRx(use_openai=False)
    topic = "Ethereum 2.0 impact on network scalability"
    
    results = argumentrx.generate_arguments(topic)
    
    if 'error' not in results:
        print(f"\nTopic: {topic}")
        
        for stance in ['pro', 'con']:
            evaluation = results['arguments'][stance]['evaluation']
            print(f"\n{stance.upper()} Argument Evaluation:")
            print(f"  Overall Score: {evaluation['overall_score']}")
            print(f"  Clarity: {evaluation['clarity']}")
            print(f"  Logic: {evaluation['logic']}")
            print(f"  Evidence: {evaluation['evidence']}")
            print(f"  Persuasiveness: {evaluation['persuasiveness']}")
            print(f"  Feedback: {evaluation['feedback'][:100]}...")

if __name__ == "__main__":
    print("🧠 ArgumentRx Examples")
    print("Make sure you have set up your .env file with API keys for full functionality.")
    print("Some examples will work with local models only.\n")
    
    try:
        example_basic_usage()
        example_with_file_output()
        example_crypto_topics()
        example_evaluation_analysis()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("📁 Check the 'results' directory for saved outputs.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")