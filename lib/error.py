#!/usr/bin/python
import requests

# Error Code Handling \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class Error():
    
    # Initialize the class
    def __init__(self, callback_host):
        self.ec = 0
        self.em = 'An unknown error occured when building the instance'
        self.cb = callback_host
        
    # Handle the error code
    def response(self, code):
        
        # Return the error the the callback server and exit
        def err_callback(self, msg):
            err_response = {'error': msg}
            requests.get('http://' + self.cb + '/vm-callback/', params = err_response)
            exit()
        
        # Define error codes
        codes = {0: 'An unknown error occured when building the instance',
                 1: 'Failed to retrieve information from the metadata server'}
        
        # Return the error response to the callback server
        err_callback(codes[code])