import os
import sys
import django

print("=" * 60)
print("QUIZ APPLICATION SETUP")
print("=" * 60)

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simulator.settings')
django.setup()

# Step 1: Delete old database
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
if os.path.exists(db_path):
    print("\n[1/4] Deleting old database...")
    os.remove(db_path)
    print("✓ Old database deleted")
else:
    print("\n[1/4] No old database found")

# Step 2: Create tables
print("\n[2/4] Creating database tables...")
from django.core.management import call_command
try:
    call_command('migrate', '--run-syncdb', verbosity=1)
    print("✓ Database tables created successfully")
except Exception as e:
    print(f"✗ Error creating tables: {e}")
    sys.exit(1)

# Verify tables exist
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quiz_question';")
result = cursor.fetchone()
if not result:
    print("✗ quiz_question table was not created!")
    print("  Creating tables manually...")
    cursor.execute('''
        CREATE TABLE quiz_question (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_number INTEGER UNIQUE NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option VARCHAR(1) NOT NULL,
            explanation TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE quiz_quizsession (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME NOT NULL,
            end_time DATETIME,
            selected_questions TEXT NOT NULL,
            user_answers TEXT NOT NULL DEFAULT '{}',
            score INTEGER NOT NULL DEFAULT 0,
            is_completed BOOLEAN NOT NULL DEFAULT 0,
            current_question_index INTEGER NOT NULL DEFAULT 0
        )
    ''')
    connection.commit()
    print("✓ Tables created manually")

# Step 3: Load questions from PDF
print("\n[3/4] Loading questions from PDF...")

from quiz.models import Question
import PyPDF2
import re

pdf_path = os.path.join(os.path.dirname(__file__), 'simulator', 'questions.pdf')

if not os.path.exists(pdf_path):
    print(f"✗ PDF file not found at: {pdf_path}")
    sys.exit(1)

try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        print(f"  Reading {len(pdf_reader.pages)} pages...")
        for page in pdf_reader.pages:
            full_text += page.extract_text()

    # Parse questions
    lines = full_text.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not re.match(r'^\d+$', line) and not re.match(r'^Page\s*\d+', line, re.IGNORECASE):
            clean_lines.append(line)
    
    text = '\n'.join(clean_lines)
    
    question_pattern = r'Question\s*(\d+)[:\s]*(.+?)(?=Question\s*\d+|$)'
    matches = re.finditer(question_pattern, text, re.DOTALL | re.IGNORECASE)
    
    questions_data = []
    
    for match in matches:
        q_num = int(match.group(1))
        q_content = match.group(2).strip()
        
        lines = [line.strip() for line in q_content.split('\n') if line.strip()]
        
        if len(lines) < 7:
            continue
        
        question_text = lines[0]
        option_a = ""
        option_b = ""
        option_c = ""
        option_d = ""
        correct_option = ""
        explanation = ""
        
        i = 1
        while i < len(lines):
            line = lines[i]
            
            if re.match(r'^[Aa][\.:\)]\s*', line):
                option_a = re.sub(r'^[Aa][\.:\)]\s*', '', line).strip()
            elif re.match(r'^[Bb][\.:\)]\s*', line):
                option_b = re.sub(r'^[Bb][\.:\)]\s*', '', line).strip()
            elif re.match(r'^[Cc][\.:\)]\s*', line):
                option_c = re.sub(r'^[Cc][\.:\)]\s*', '', line).strip()
            elif re.match(r'^[Dd][\.:\)]\s*', line):
                option_d = re.sub(r'^[Dd][\.:\)]\s*', '', line).strip()
            elif re.match(r'^(Correct\s*Answer|Answer)[:\s]*([A-Da-d])', line, re.IGNORECASE):
                match_ans = re.search(r'([A-Da-d])', line)
                if match_ans:
                    correct_option = match_ans.group(1).upper()
            elif re.match(r'^(Explanation|Exp)[:\s]*', line, re.IGNORECASE):
                explanation = re.sub(r'^(Explanation|Exp)[:\s]*', '', line, flags=re.IGNORECASE).strip()
                j = i + 1
                while j < len(lines) and not re.match(r'^Question\s*\d+', lines[j], re.IGNORECASE):
                    if not re.match(r'^[A-Da-d][\.:\)]\s*', lines[j]) and not re.match(r'^(Correct\s*Answer|Answer)', lines[j], re.IGNORECASE):
                        explanation += " " + lines[j]
                    j += 1
                break
            
            i += 1
        
        if not all([question_text, option_a, option_b, option_c, option_d, correct_option]):
            continue
        
        if not explanation:
            explanation = "No explanation provided."
        
        questions_data.append({
            'question_number': q_num,
            'question_text': question_text,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_option': correct_option,
            'explanation': explanation.strip()
        })
    
    print(f"  Parsed {len(questions_data)} questions from PDF")
    
    # Save to database
    for q_data in questions_data:
        Question.objects.create(**q_data)
    
    print(f"✓ Successfully loaded {len(questions_data)} questions into database")
    
except ImportError:
    print("✗ PyPDF2 is not installed")
    print("  Run: pip install PyPDF2")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error loading questions: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Verify
print("\n[4/4] Verifying setup...")
question_count = Question.objects.count()
print(f"✓ Total questions in database: {question_count}")

print("\n" + "=" * 60)
print("SETUP COMPLETE!")
print("=" * 60)
print("\nRun the server with:")
print("  python manage.py runserver")
print("\nThen visit: http://127.0.0.1:8000/")
print("=" * 60)
