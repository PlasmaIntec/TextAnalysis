from flask import Flask, json
from text_generation import generate_text

api = Flask(__name__)

@api.route('/<path:path>', methods=['GET'])
def get_companies(path):
  	return generate_text(start_string=path)

if __name__ == '__main__':
    api.run()