from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pdgragagent import PDFAgent

# Load environment variables at the start
load_dotenv()

# Verify that required environment variables are set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = Flask(__name__)

config = {
  'ORIGINS': [
    'http://localhost:3000',  # React
    'http://127.0.0.1:3000',  # React
  ],
  'SECRET_KEY': '...'
}

# Configure CORS
CORS(app,resources={ r'/*': {'origins': config['ORIGINS']}}, supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/hello', methods=['GET'])
def upload_file1():
    return "Hello world"

@app.route('/api/upload', methods=['POST','OPTIONS'])
def upload_file():
    # return jsonify({
    #     'status': 'success',
    #     'summary': "summary",
    #     'requires_approval': True
    # })
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 200
    
    if 'pdf' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            agent = PDFAgent()
            summary = agent.process_pdf(filepath)
            return jsonify({
                'status': 'success',
                'summary': summary,
                'requires_approval': True
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

@app.route('/api/decision', methods=['POST', 'OPTIONS'])
def handle_decision():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 200
        
    data = request.json
    decision = data.get('decision')
    
    if decision not in ['Y', 'N']:
        return jsonify({
            'status': 'error',
            'message': 'Invalid decision'
        }), 400
    
    # Here you can add any additional logic based on the decision
    return jsonify({
        'status': 'success',
        'message': 'Decision processed successfully'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True) 