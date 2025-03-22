from flask import Flask, request, render_template
import boto3

app = Flask(__name__)

S3_BUCKET = "your-s3-bucket-name"
s3 = boto3.client("s3")

@app.route("/")
def index():
    return render_template("upload.html")  # Ensure upload.html is the file you provided

@app.route("/upload", methods=["POST"])
def upload_file():
    if "csvFile" not in request.files:
        return "No file uploaded", 400

    file = request.files["csvFile"]
    if file.filename == "":
        return "No selected file", 400

    s3.upload_fileobj(file, S3_BUCKET, file.filename)
    return f"File {file.filename} uploaded successfully to {S3_BUCKET}"

if __name__ == "__main__":
    app.run(debug=True)