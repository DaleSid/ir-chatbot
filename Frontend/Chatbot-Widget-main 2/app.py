from flask import Flask, render_template
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/") 
@cross_origin()
def home():
   return render_template('index.html')
if __name__ == '__main__':
   app.run(debug=True)







