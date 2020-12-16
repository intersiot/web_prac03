from flask import Flask, render_template, request
import requests
# requests를 import 해준다.

app = Flask(__name__)


@app.route('/')
def main():
    myname = "SPARTA"

    # jinja 사용해서 데이터를 받아와 index.html에 값을 보내준다.
    r = requests.get('http://openapi.seoul.go.kr:8088/6d4d776b466c656533356a4b4b5872/json/RealtimeCityAir/1/99')
    response = r.json()
    rows = response['RealtimeCityAir']['row']

    return render_template("index.html", name=myname, rows=rows)


@app.route('/detail/<keyword>')
def detail(keyword):
    # word_recive = request.args.get("word_give")

    # Owlbot API 요청 코드
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}", headers={"Authorization": "Token fa3c379031c3271687cd6e80de4c80852789c7f8"})
    result = r.json()
    print(result)

    return render_template("detail.html", word=keyword)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
