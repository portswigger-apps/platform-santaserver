#!/usr/bin/env python3
"""
Supervisor watchdog script for monitoring process failures
Handles automatic recovery and logging of critical process failures
"""

import sys
import os
import logging
from supervisor.childutils import listener

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('supervisor-watchdog')

def handle_event(headers, payload):
    """Handle supervisor process events"""
    try:
        # Parse event data
        event_data = dict([line.split(':') for line in payload.split('\n') if ':' in line])
        
        processname = event_data.get('processname', 'unknown')
        from_state = event_data.get('from_state', 'unknown')
        to_state = event_data.get('to_state', 'unknown')
        
        logger.info(f"Process {processname} transitioned from {from_state} to {to_state}")
        
        # Handle fatal states
        if to_state == 'FATAL':
            logger.error(f"Process {processname} entered FATAL state!")
            
            # Specific handling for critical processes
            if processname == 'uvicorn':
                logger.critical("FastAPI backend process failed! Attempting restart...")
                # In a real implementation, you might trigger restart logic here
                
            elif processname == 'nginx':
                logger.critical("Nginx process failed! Container may become unresponsive!")
                
        elif to_state == 'EXITED':
            logger.warning(f"Process {processname} exited unexpectedly")
            
    except Exception as e:
        logger.error(f"Error handling supervisor event: {e}")

def main():
    """Main watchdog loop"""
    logger.info("Supervisor watchdog started")
    
    try:
        while True:
            # Wait for supervisor events
            headers, payload = listener.wait(sys.stdin, sys.stdout)
            
            # Handle the event
            handle_event(headers, payload)
            
            # Acknowledge the event
            listener.ok(sys.stdout)
            
    except KeyboardInterrupt:
        logger.info("Watchdog stopped by user")
    except Exception as e:
        logger.error(f"Watchdog error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()