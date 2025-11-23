from django.core.management.base import BaseCommand
from quiz.models import Question
import PyPDF2
import re
from pathlib import Path


class Command(BaseCommand):
    help = 'Load questions from PDF file'

    def handle(self, *args, **kwargs):
        pdf_path = Path(__file__).resolve().parent.parent.parent.parent.parent / 'simulator' / 'questions.pdf'
        
        if not pdf_path.exists():
            self.stdout.write(self.style.ERROR(f'PDF file not found at {pdf_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Reading PDF from {pdf_path}'))
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page in pdf_reader.pages:
                    full_text += page.extract_text()

            questions_data = self.parse_questions(full_text)
            
            Question.objects.all().delete()
            
            for q_data in questions_data:
                Question.objects.create(**q_data)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(questions_data)} questions'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    def parse_questions(self, text):
        questions = []
        
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not self.is_header_footer(line):
                clean_lines.append(line)
        
        text = '\n'.join(clean_lines)
        
        question_pattern = r'Question\s*(\d+)[:\s]*(.+?)(?=Question\s*\d+|$)'
        matches = re.finditer(question_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            q_num = int(match.group(1))
            q_content = match.group(2).strip()
            
            parsed = self.parse_single_question(q_num, q_content)
            if parsed:
                questions.append(parsed)
        
        return questions

    def parse_single_question(self, q_num, content):
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 7:
            return None
        
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
                match = re.search(r'([A-Da-d])', line)
                if match:
                    correct_option = match.group(1).upper()
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
            return None
        
        if not explanation:
            explanation = "No explanation provided."
        
        return {
            'question_number': q_num,
            'question_text': question_text,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_option': correct_option,
            'explanation': explanation.strip()
        }

    def is_header_footer(self, line):
        header_footer_patterns = [
            r'^\d+$',
            r'^Page\s*\d+',
            r'^\s*$',
            r'^www\.',
            r'\.com\s*$',
            r'^Logo',
            r'^Header',
            r'^Footer',
        ]
        
        for pattern in header_footer_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False
