from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'key': 'value',
        'numbers': [1, 2, 3]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
