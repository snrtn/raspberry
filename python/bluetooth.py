from flask import Flask, request

app = Flask(__name__)

@app.route('/message', methods=['POST'])
def receive_message():
    data = request.json
    print(f"? ?? ???: {data['message']}")
    return {"status": "Message received!"}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
