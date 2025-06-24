#!/usr/bin/env python3
"""
Celery worker entry point for the embedding worker service
"""

import os
import sys
from celery_config import celery_app

if __name__ == "__main__":
    # Start the Celery worker
    celery_app.start() 