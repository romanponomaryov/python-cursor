from flask import Flask, render_template, request, jsonify, make_response, url_for, abort, session
from werkzeug.utils import secure_filename

from api import api

app = Flask(__name__)

app.register_blueprint(api)


@app.route("/")
@app.route("/home")
def home():
    return "<h1>Home Page</h1>"


@app.route("/about")
def about():
    return "<h1>About Page</h1>"


dict_info_about = {"Nick": "Age: 31, Favourite drink: kola",
                   "Jack": "Age 22, Favourite drink: coffee"}


@app.route("/names/<path:name>/")
def name(name):
    if name in dict_info_about.keys():
        return name
    return name


@app.route("/path/<path:subpath>")
def show_subpath(subpath):
    return 'Subpath %s' % subpath


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/month/<int:number>")
def return_month_name(number):
    month = name_of_the_month(number)
    return render_template("month.html", month=month)


def name_of_the_month(number):
    """
    Returns the month according to the number
    :param number: int
    :return:
    """
    months = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December")
    return months[number - 1]


test_methods_dict = ["Value 1", "Value 2"]


@app.route('/test_methods')
@app.route('/test_methods/<string:value>', methods=['GET', 'POST', 'DELETE'])
def test_methods(value=None):
    if request.method == 'POST':
        do_post(value)
        return "Successfully added a new value"
    if request.method == 'DELETE':
        do_delete(value)
        return "Successfully deleted the value"
    else:
        return do_get()


def do_post(value):
    """
    This method will add value to the test_methods_dict
    :return:
    """
    return test_methods_dict.append(value)


def do_get():
    """
    Returns template with all test_methods_dict values
    :return:
    """
    return render_template('test_methods.html', values=test_methods_dict, name="a")


def do_delete(value):
    """
    Delete values from test_methods_dict
    :param value:
    :return:
    """
    for i, elem in enumerate(test_methods_dict):
        if elem == value:
            test_methods_dict.pop(i)


from flask.views import MethodView

request_object_data = {"Key 1": "Value 1",
                       "Key 2": "Value 2"}


# http://werkzeug.pocoo.org/docs/0.14/wrappers/


class RequestObject(MethodView):
    def get(self):
        client_name = request.headers.get("client_name")
        args = request.args
        base_url = request.base_url

        response = dict()
        response["client_name"] = client_name
        response["args"] = args
        response["base_url"] = base_url

        return jsonify(response)

    def post(self):
        data = request.data
        return data


app.add_url_rule('/request_object', view_func=RequestObject.as_view('request_object'))


class FileUpload(MethodView):
    def post(self):
        f = request.files['file']
        f.save(f"{secure_filename(f.filename)}")
        return "success"


app.add_url_rule('/file_upload', view_func=FileUpload.as_view('file_upload'))

from functools import wraps
from flask import g, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


from datetime import timedelta
from flask import session


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


db = {
    "news": ["elem", "elem_2", "elem_3"]
}


@app.route('/homework_home')
def home_page():
    return render_template('home.html', data=db)


@app.route('/get_cookie')
def get_cookie():
    return jsonify(request.cookies)


@app.route('/set_cookie')
def set_cookie():
    response = make_response()
    response.set_cookie("email", "...@gmail.com")  # not more then one value
    return response


@app.route("/test_abort")
def test_redirect():
    abort(501, "Value error")
    return redirect(url_for("home"))


@app.errorhandler(501)
def error_501_handler(error):
    return render_template("error_501.html")


app.secret_key = b'"\xaa;\x0b\x12\x8a\xa1V+\x16\xc5\x91\xfb,\xcb#'


@app.route("/test_session")
def test_session():
    app.logger.warning("this is warning")
    app.logger.error("This is error")
    session["key"] = "value"
    return "hello"


if __name__ == '__main__':
    app.run(debug=True)
