from flask import Flask, send_from_directory, request, Response
import os
import urlparse
import psycopg2
import json
import datetime

app = Flask(__name__, static_url_path='')

# set up connection to database
# if "DATABASE_URL" not in os.environ:
#     os.environ["DATABASE_URL"] = "postgres://awyxxzkehmelxk:0H-X2rDx5Neqh0H" \
#                                  "r9Ql26kcQWr@ec2-54-225-195-254.compute-1." \
#                                  "amazonaws.com:5432/d13rudsd14mfr9"

# urlparse.uses_netloc.append("postgres")
# url = urlparse.urlparse(os.environ["DATABASE_URL"])
# print(os.environ["DATABASE_URL"])


def get_conn():
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn


# @app.route("/")
# def main():
#     return open("tool.html").read()


@app.route("/lineups")
def get_lineups():
    


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('images', path)


@app.route("/new_shot", methods=["POST"])
def new_shot():
    player = request.form.get('player')
    outcome = request.form.get('outcome')
    x = request.form.get('x')
    y = request.form.get('y')
    date = request.form.get('date')
    shot_type = request.form.get('shot_type')
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO shots (player, outcome, x, y, date, type)"
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (player, outcome, x, y, date, shot_type))
    conn.commit()
    cur.close()
    return "inserted"


@app.route("/get_shots", methods=["POST"])
def get_shots():
    date = request.form.get('date')
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shots WHERE date = %s", (date,))
    shots = []
    content = cur.fetchone()
    while content:
        shots.append(content)
        content = cur.fetchone()
    conn.commit()
    cur.close()
    return json.dumps(shots)


@app.route("/download", methods=["GET"])
def download():
    today = datetime.date.today()
    date = "%04d-%02d-%02d" % (today.year, today.month, today.day)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shots")
    data = ['id, player, outcome, x, y, date']
    content = cur.fetchone()
    while content:
        data.append(','.join(map(str, content)))
        content = cur.fetchone()
    conn.commit()
    cur.close()
    csv = '\n'.join(data)
    print(csv)
    return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=data.csv"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
