from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

#---------- MODEL IN MEMORY ----------------#
# create your own connection, use '\list' in psql to find the name and owner of the database
# cnx = create_engine('postgresql://yichiang:yichiang@52.206.3.40:5432/adtracking')

# # Read the scientific data on breast cancer survival,
# # Build a LogisticRegression predictor on it
# patients = pd.read_csv("./haberman.data", header=None)
# patients.columns=['age','year','nodes','survived']
# patients=patients.replace(2,0)  # The value 2 means death in 5 years, update to more common 0


@app.route("/")
def viz_page():
    """
    Homepage: serve our visualization page, awesome.html
    """
    with open("AspectMiningWeb.html", 'r') as viz_file:
        return viz_file.read()


@app.route("/process", methods=["POST"])
def prob():
    """
    When A POST request with json data is made to this uri,
    Read the example from the json, predict probability and
    send it with a response
    """
    # Get decision score for our example that came with the request
    #data = flask.request.json
    data = request.json
    sentence = data["sentence"]
    #sentence = request.form["sentence"]
    
    return jsonify(sentence)