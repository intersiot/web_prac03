from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests

app = Flask(__name__)

client = MongoClient('3.35.47.80', 27017, username="test", password="test")
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    # detail함수에서 GET 방식으로 받은 msg 템플릿으로 보내기
    msg_receive = request.args.get("msg")
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    words = list(db.words.find({}, {"_id": False}))
    return render_template("index.html", msg=msg_receive, words=words)


@app.route('/detail/<keyword>')
def detail(keyword):
    # 있는 단어인지 없는 단어인지 판별해서 보내기
    status_receive = request.args.get("status_give")
    # API에서 단어 뜻 찾아서 결과 보내기
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}",
                     headers={"Authorization": "Token fa3c379031c3271687cd6e80de4c80852789c7f8"})
    # 없는 단어일 때 처리하기
    if r.status_code != 200:
        return redirect(url_for("main", msg="단어가 존재하지 않습니다."))

    result = r.json()
    print(result)

    # 깨진 글자 처리하기
    for definition in result["definitions"]:
        definition["definition"] = definition["definition"].encode("ascii", "ignore").decode("utf-8")
        if definition["example"] is not None:
            definition["example"] = definition["example"].encode("ascii", "ignore").decode("utf-8")
    return render_template("detail.html", word=keyword, result=result, status=status_receive)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    # 요청 보내기
    word_receive = request.form["word_give"]
    definition_receive = request.form["definition_give"]
    # db에 저장하기
    doc = {"word": word_receive, "definition": definition_receive}
    db.words.insert_one(doc)
    # 단어 저장하기
    return jsonify({'result': 'success', 'msg': '단어 저장'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    # 요청 보내기
    word_receive = request.form["word_give"]
    # db에서 지우기
    db.words.delete_one({"word": word_receive})
    # db에서 예문 지우기
    db.examples.delete_many({"word": word_receive})
    # 단어 삭제하기
    return jsonify({'result': 'success', 'msg': f'word "{word_receive}"가 삭제 됐습니다.'})


@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    # 예문 가져오기
    word_receive = request.args.get("word_give")
    result = list(db.examples.find({"word": word_receive}, {'_id': 0}))

    return jsonify({'result': 'success', 'examples': result})


@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    # 예문 저장하기
    word_receive = request.form["word_give"]
    example_receive = request.form["example_give"]

    # db에 저장
    doc = {
        "word": word_receive,
        "example": example_receive
    }
    db.examples.insert_one(doc)

    return jsonify({'result': 'success', 'msg': "저장됨"})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    # 예문 삭제하기
    word_receive = request.form['word_give']
    number_receive = int(request.form["number_give"])
    example = list(db.examples.find({"word": word_receive}))[number_receive]["example"]
    # print(word_receive, example)
    db.examples.delete_one({"word": word_receive, "example": example})
    return jsonify({'result': 'success', 'msg': f'example #{number_receive} of "{word_receive}" deleted'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
