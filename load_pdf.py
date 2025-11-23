import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simulator.settings')
django.setup()

from quiz.models import Question
import PyPDF2
import re

pdf_path = os.path.join(os.path.dirname(__file__), 'simulator', 'questions.pdf')

print(f'Reading PDF from: {pdf_path}')

if not os.path.exists(pdf_path):
    print(f'ERROR: PDF file not found at {pdf_path}')
    sys.exit(1)

try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        print(f'Total pages in PDF: {len(pdf_reader.pages)}')
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            full_text += page_text + "\n"
            print(f'Extracted page {page_num + 1}')

    print('\n' + '='*60)
    print('PDF read successfully. Parsing questions...')
    print('='*60 + '\n')
    
    full_text = re.sub(r'www\.crystal\.consulting', '', full_text, flags=re.IGNORECASE)
    
    question_blocks = re.split(r'\*{3,}', full_text)
    
    questions_data = []
    
    for block_idx, block in enumerate(question_blocks):
        block = block.strip()
        if not block or len(block) < 30:
            continue
        
        lines = block.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        lines = [line for line in lines if not re.match(r'^Page\s+\d+', line, re.IGNORECASE)]
        
        if not lines:
            continue
        
        question_text_parts = []
        option_a = ""
        option_b = ""
        option_c = ""
        option_d = ""
        correct_option = ""
        explanation = ""
        
        found_options = False
        collecting_explanation = False
        
        for i, line in enumerate(lines):
            if re.match(r'^ECO\s+Domain\s+Task\s*:', line, re.IGNORECASE):
                break
            
            if re.match(r'^A\s*:\s*', line, re.IGNORECASE):
                found_options = True
                option_a = re.sub(r'^A\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                continue
            
            if re.match(r'^B\s*:\s*', line, re.IGNORECASE):
                option_b = re.sub(r'^B\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                continue
            
            if re.match(r'^C\s*:\s*', line, re.IGNORECASE):
                option_c = re.sub(r'^C\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                continue
            
            if re.match(r'^D\s*:\s*', line, re.IGNORECASE):
                option_d = re.sub(r'^D\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                continue
            
            if re.match(r'^Correct\s*Answer\s*:', line, re.IGNORECASE):
                answer_text = re.sub(r'^Correct\s*Answer\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                answer_match = re.search(r'([A-Da-d])', answer_text)
                if answer_match:
                    correct_option = answer_match.group(1).upper()
                continue
            
            if re.match(r'^Explanation\s*:', line, re.IGNORECASE):
                collecting_explanation = True
                explanation = re.sub(r'^Explanation\s*:\s*', '', line, flags=re.IGNORECASE).strip()
                continue
            
            if collecting_explanation and not re.match(r'^ECO\s+Domain\s+Task\s*:', line, re.IGNORECASE):
                explanation += ' ' + line
            elif not found_options:
                question_text_parts.append(line)
        
        question_text = ' '.join(question_text_parts).strip()
        question_text = re.sub(r'\s+', ' ', question_text)
        
        option_a = re.sub(r'\s+', ' ', option_a).strip()
        option_b = re.sub(r'\s+', ' ', option_b).strip()
        option_c = re.sub(r'\s+', ' ', option_c).strip()
        option_d = re.sub(r'\s+', ' ', option_d).strip()
        explanation = re.sub(r'\s+', ' ', explanation).strip()
        
        if not question_text or not all([option_a, option_b, option_c, option_d]):
            continue
        
        if not correct_option:
            correct_option = 'A'
        
        if not explanation:
            explanation = "No explanation provided."
        
        q_num_match = re.search(r'^\d+', question_text)
        if q_num_match:
            question_number = int(q_num_match.group())
            question_text = re.sub(r'^\d+[\.\s]*', '', question_text).strip()
        else:
            question_number = len(questions_data) + 1
        
        questions_data.append({
            'question_number': question_number,
            'question_text': question_text,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_option': correct_option,
            'explanation': explanation
        })
        
        print(f'✓ Parsed Question #{question_number}')
    
    print(f'\n{"="*60}')
    print(f'Total questions parsed: {len(questions_data)}')
    print(f'{"="*60}\n')
    
    if len(questions_data) == 0:
        print('ERROR: No questions were parsed. Please check the PDF format.')
        sys.exit(1)
    
    Question.objects.all().delete()
    print('Deleted existing questions from database\n')
    
    for q_data in questions_data:
        Question.objects.create(**q_data)
        print(f'Saved Question #{q_data["question_number"]} to database')
    
    print(f'\n{"="*60}')
    print(f'✓ SUCCESS: Loaded {len(questions_data)} questions into database!')
    print(f'{"="*60}')
    
except Exception as e:
    print(f'ERROR: {str(e)}')
    import traceback
    traceback.print_exc()
