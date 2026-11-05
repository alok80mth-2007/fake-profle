import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename

from src.detector import FakeProfileDetector
from src.models.model_loader import get_model_metadata
from src.utils.data_processor import process_profile_url
from src.utils.visualization import generate_report

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key_fake_profile_detector_2026")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global context processor for templates
@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "app_version": "2.0.0"
    }

# Initialize detector
detector = FakeProfileDetector()


@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_profile():
    """Process a profile URL or username and display results."""
    profile_url = request.form.get('profile_url', '').strip()
    platform = request.form.get('platform', 'twitter').strip()
    
    if not profile_url:
        flash('Please enter a profile URL or username', 'error')
        return redirect(url_for('index'))
    
    try:
        # Check for optional custom manual overrides
        custom_overrides = {}
        if request.form.get('manual_followers'):
            try:
                custom_overrides['followers_count'] = int(request.form.get('manual_followers'))
            except ValueError:
                pass
        if request.form.get('manual_following'):
            try:
                custom_overrides['following_count'] = int(request.form.get('manual_following'))
            except ValueError:
                pass
        if request.form.get('manual_posts'):
            try:
                custom_overrides['post_count'] = int(request.form.get('manual_posts'))
            except ValueError:
                pass
        if request.form.get('manual_age_days'):
            try:
                custom_overrides['account_age_days'] = int(request.form.get('manual_age_days'))
            except ValueError:
                pass
        if request.form.get('manual_bio') and request.form.get('manual_bio').strip():
            custom_overrides['bio'] = request.form.get('manual_bio').strip()

        # Process the profile data (attempts real live scrape, then fallback, then manual overrides)
        profile_data = process_profile_url(profile_url, platform, custom_overrides=custom_overrides if custom_overrides else None)
        
        # Run the detection
        result = detector.analyze_profile(profile_data)
        
        # Generate visualization for the report
        report_data = generate_report(result, profile_data)
        
        # Store result in session for the results page
        session['report_data'] = report_data
        session['analysis_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return redirect(url_for('results'))
    
    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}", exc_info=True)
        flash(f'Error analyzing profile: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/batch', methods=['GET', 'POST'])
def batch_analysis():
    """Handle batch processing of multiple profiles."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file:
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                platform = request.form.get('platform', 'twitter')
                
                # Process the batch file
                results = detector.batch_analyze(filepath, platform)
                
                # Store batch results
                session['batch_results'] = results
                session['batch_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                return redirect(url_for('batch_results'))
            
            except Exception as e:
                logger.error(f"Error in batch analysis: {str(e)}", exc_info=True)
                flash(f'Error processing batch file: {str(e)}', 'error')
                return redirect(url_for('batch_analysis'))
    
    return render_template('batch.html')


@app.route('/results')
def results():
    """Display the results of a single profile analysis."""
    if 'report_data' not in session:
        flash('No analysis data found. Please analyze a profile first.', 'error')
        return redirect(url_for('index'))
    
    report_data = session['report_data']
    timestamp = session.get('analysis_timestamp', 'Unknown')
    
    return render_template('results.html', report=report_data, timestamp=timestamp)


@app.route('/batch-results')
def batch_results():
    """Display the results of a batch analysis."""
    if 'batch_results' not in session:
        flash('No batch analysis results found. Please run a batch analysis first.', 'error')
        return redirect(url_for('batch_analysis'))
    
    results_data = session['batch_results']
    timestamp = session.get('batch_timestamp', 'Unknown')
    
    return render_template('batch_results.html', results=results_data, timestamp=timestamp)


@app.route('/about')
def about():
    """Display information about the project and model metrics."""
    metadata = get_model_metadata()
    return render_template('about.html', metadata=metadata)


# REST API Endpoints
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """JSON API endpoint for programmatic profile analysis."""
    data = request.get_json(silent=True) or request.form.to_dict()
    profile_url = data.get('profile_url') or data.get('username') or data.get('url')
    platform = data.get('platform', 'twitter')
    
    if not profile_url:
        return jsonify({'error': 'Missing required parameter: profile_url or username'}), 400
    
    try:
        custom_overrides = {}
        for key in ['followers_count', 'following_count', 'post_count', 'account_age_days', 'bio']:
            if key in data:
                custom_overrides[key] = data[key]
        profile_data = process_profile_url(profile_url, platform, custom_overrides=custom_overrides if custom_overrides else None)
        result = detector.analyze_profile(profile_data)
        
        return jsonify({
            'status': 'success',
            'username': result.get('profile_data', {}).get('username'),
            'platform': platform,
            'is_fake': result.get('is_fake'),
            'probability': result.get('probability'),
            'indicators': result.get('indicators'),
            'recommendations': result.get('recommendations'),
            'timestamp': result.get('timestamp')
        })
    except Exception as e:
        logger.error(f"API Analysis error: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/model-info', methods=['GET'])
def api_model_info():
    """API endpoint to get model architecture, metrics, and features."""
    metadata = get_model_metadata()
    return jsonify({
        'status': 'success',
        'model_metadata': metadata
    })


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(e)}", exc_info=True)
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
