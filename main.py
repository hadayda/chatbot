from flask import Flask, render_template, request

app = Flask(__name__, static_url_path='/static')

from chat_bot import ChatBot


@app.route('/')
def home_page():
    ChatBot.begin()
    return render_template('index.html')


@app.route('/get-response', methods=['GET'])
def get_chat_response():
    chatbot = ChatBot()
    message = request.args.get('message')
    return chatbot.get_response(message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

