#!/usr/bin/env python3
"""
EduPlan AI - Argument Parsing Deep Dive
Detailed explanation of how main.py processes command-line arguments
"""

def explain_argument_parsing():
    """Detailed explanation of the argument parsing system"""
    
    print("🎯 EduPlan AI - Main.py Argument Parsing Explained")
    print("=" * 60)
    
    print("\n📋 ARGUMENT PARSER ARCHITECTURE")
    print("-" * 40)
    print("""
The main.py uses Python's argparse library with a hierarchical command structure:

main.py
├── setup       (subcommand)
│   └── --force (optional flag)
├── generate    (subcommand)
│   ├── topic   (positional argument)
│   ├── --chapter (optional)
│   └── --subject (optional, default='General')
└── check       (subcommand)
    └── (no additional arguments)
""")

    print("\n🔧 CODE BREAKDOWN")
    print("-" * 20)
    
    print("""
1. PARSER INITIALIZATION:
```python
parser = argparse.ArgumentParser(description='EduPlan AI - Educational AI Platform')
subparsers = parser.add_subparsers(dest='command', help='Available commands')
```
• Creates main parser with description
• Sets up subcommands system
• 'dest=command' stores chosen subcommand in args.command
""")

    print("""
2. SETUP COMMAND:
```python
setup_parser = subparsers.add_parser('setup', help='Set up the RAG pipeline')
setup_parser.add_argument('--force', action='store_true', help='Force rebuild')
```
• Usage: python main.py setup [--force]
• --force is a boolean flag (True if present, False if not)
• action='store_true' means no value needed after --force
""")

    print("""
3. GENERATE COMMAND:
```python
generate_parser = subparsers.add_parser('generate', help='Generate lesson plan')
generate_parser.add_argument('topic', help='Lesson plan topic')
generate_parser.add_argument('--chapter', help='Filter by chapter')
generate_parser.add_argument('--subject', default='General', help='Filter by subject')
```
• 'topic' is POSITIONAL (required, no -- prefix)
• --chapter and --subject are OPTIONAL (-- prefix)
• default='General' means subject defaults to 'General' if not provided
""")

    print("""
4. CHECK COMMAND:
```python
check_parser = subparsers.add_parser('check', help='Check database status')
```
• Simple command with no additional arguments
• Just runs database status check
""")

    print("\n⚙️ ARGUMENT PROCESSING FLOW")
    print("-" * 30)
    
    print("""
Step 1: Parse Arguments
```python
args = parser.parse_args()
```
This converts command line input into an object with attributes:

Example Input: python main.py generate "evaporation" --chapter "Chapter 1"
Results in:
  args.command = "generate"
  args.topic = "evaporation"  
  args.chapter = "Chapter 1"
  args.subject = "General"    # default value
""")

    print("""
Step 2: Route to Handler
```python
if args.command == 'setup':
    # Handle setup
elif args.command == 'generate':
    # Handle generation
elif args.command == 'check':
    # Handle check
else:
    parser.print_help()  # Show help if no command
```
""")

    print("\n🔍 REAL EXAMPLE WALKTHROUGH")
    print("-" * 35)
    
    print("""
COMMAND: python main.py generate "Evaporation" --chapter "Chapter 1" --subject "General"

PARSING PROCESS:
1. argparse identifies 'generate' as the subcommand
2. "Evaporation" is captured as the positional 'topic' argument
3. --chapter "Chapter 1" is captured as the chapter filter
4. --subject "General" is captured as the subject filter

RESULTING ARGS OBJECT:
args.command = "generate"
args.topic = "Evaporation"
args.chapter = "Chapter 1"
args.subject = "General"

EXECUTION FLOW:
1. Code enters 'elif args.command == "generate":' branch
2. Imports LessonPlanGenerator from src.generators
3. Creates generator instance
4. Calls generator.generate_lesson_plan() with parsed arguments:
   - query="Evaporation"
   - filter_chapter="Chapter 1"
   - filter_subject="General"
5. Saves result to outputs/lesson_plans/lesson_plan_evaporation.json
""")

    print("\n🎛️ ARGUMENT TYPES EXPLAINED")
    print("-" * 30)
    
    print("""
POSITIONAL ARGUMENTS:
• No -- prefix required
• Order matters
• Usually required
• Example: 'topic' in generate command

OPTIONAL ARGUMENTS:
• Require -- prefix
• Order doesn't matter
• Can have default values
• Example: --chapter, --subject

FLAGS (Boolean):
• action='store_true' means presence = True, absence = False
• No value required after the flag
• Example: --force in setup command

DEFAULT VALUES:
• Specified with default= parameter
• Used when argument not provided
• Example: subject defaults to 'General'
""")

    print("\n🚨 ERROR HANDLING")
    print("-" * 20)
    
    print("""
AUTOMATIC ERROR HANDLING by argparse:

1. Missing Required Arguments:
   python main.py generate
   → Error: the following arguments are required: topic

2. Invalid Commands:
   python main.py invalid_command
   → Shows help message automatically

3. Help Requests:
   python main.py --help
   python main.py generate --help
   → Shows appropriate help information

4. Type Mismatches:
   If you specified type=int and user provides string
   → Automatic error with helpful message
""")

    print("\n📝 PRACTICAL EXAMPLES")
    print("-" * 25)
    
    examples = [
        ("python main.py setup", "Sets up the RAG pipeline"),
        ("python main.py setup --force", "Forces rebuild of database"),
        ("python main.py generate 'atomic theory'", "Generates lesson plan for atomic theory (all chapters)"),
        ("python main.py generate 'photosynthesis' --chapter 'Chapter 5'", "Lesson plan filtered to Chapter 5"),
        ("python main.py generate 'algebra' --subject 'Mathematics'", "Lesson plan filtered by subject"),
        ("python main.py check", "Checks database status"),
        ("python main.py --help", "Shows main help"),
        ("python main.py generate --help", "Shows generate command help")
    ]
    
    for cmd, desc in examples:
        print(f"  {cmd}")
        print(f"    → {desc}")
        print()

if __name__ == "__main__":
    explain_argument_parsing()
