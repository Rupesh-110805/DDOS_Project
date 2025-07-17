#!/usr/bin/env python3
"""
Production-ready version of the DDoS Detection System
"""

import os
from app import app, socketio

# For gunicorn - expose the Flask app
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Run with production settings
    socketio.run(
        app, 
        host=host, 
        port=port, 
        debug=False,
        use_reloader=False,
        log_output=True
    )
