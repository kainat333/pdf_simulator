import os

pdf_path = os.path.join(os.path.dirname(__file__), 'simulator', 'questions.pdf')

print(f'Looking for PDF at: {pdf_path}')
print(f'PDF exists: {os.path.exists(pdf_path)}')

if os.path.exists(pdf_path):
    print(f'PDF file size: {os.path.getsize(pdf_path)} bytes')
    
    try:
        import PyPDF2
        print('PyPDF2 is installed ✓')
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f'Number of pages: {len(pdf_reader.pages)}')
            print('PDF can be read successfully ✓')
            
            print('\nFirst 500 characters of page 1:')
            print(pdf_reader.pages[0].extract_text()[:500])
            
    except ImportError:
        print('ERROR: PyPDF2 is NOT installed')
        print('Install it with: pip install PyPDF2')
    except Exception as e:
        print(f'ERROR reading PDF: {e}')
else:
    print('ERROR: PDF file not found!')
