"""Catch-all route for /api/* requests"""
from index import handler as main_handler

def handler(request, context):
    return main_handler(request, context)