from flask import Flask, render_template, request, send_file, flash
import os
from werkzeug.utils import secure_filename
import csv
import re
import codecs

app = Flask(__name__)
# Change this secret key
app.secret_key = "your_secret_key_here"

# Configure upload folder
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"log"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set correct permissions for the uploads folder
os.chmod(UPLOAD_FOLDER, 0o777)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_log_to_csv(log_file_path, original_filename):
    """
    Convert log file to CSV using the provided logic
    """
    try:
        # Read the log file
        print(f"[+] Reading logs from {log_file_path}")
        log_data = codecs.open(log_file_path, "r", encoding="UTF-8")

        # Regex pattern for matching field=value pairs
        pattern = re.compile(
            '(\w+)(?:=)(?:"{1,3}([\w\-\.:\ =]+)"{1,3})|(\w+)=(?:([\w\-\.:\=]+))'
        )
        events = []

        # Process each line in the log file
        for line in log_data:
            event = {}
            match = pattern.findall(line)
            for group in match:
                if group[0] != "":
                    event[group[0]] = group[1]
                else:
                    event[group[2]] = group[3]
            events.append(event)

        print("[+] Processing log fields")
        headers = []
        for row in events:
            for key in row.keys():
                if not key in headers:
                    headers.append(key)

        print("[+] Writing CSV")
        # Create the CSV filename from the original filename
        base_name = os.path.splitext(original_filename)[0]
        csv_filename = f"{base_name}.csv"
        csv_file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(csv_filename)
        )

        with open(csv_file_path, "w", newline="", encoding="utf-8") as fileh:
            csvfile = csv.DictWriter(fileh, headers)
            csvfile.writeheader()
            for row in events:
                csvfile.writerow(row)

        print(f"[+] Finished - {len(events)} rows written to {csv_file_path}")
        return csv_file_path, csv_filename

    except Exception as e:
        raise Exception(f"Conversion error: {str(e)}")
    finally:
        if "log_data" in locals():
            log_data.close()


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected")
            return render_template("upload.html")

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected")
            return render_template("upload.html")

        if file and allowed_file(file.filename):
            try:
                original_filename = file.filename
                secure_name = secure_filename(original_filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_name)

                # Save the uploaded file
                file.save(file_path)

                # Convert the file
                csv_path, csv_filename = convert_log_to_csv(
                    file_path, original_filename
                )

                # Clean up the original log file
                if os.path.exists(file_path):
                    os.remove(file_path)

                try:
                    # Send the converted file
                    response = send_file(
                        csv_path,
                        mimetype="text/csv",
                        as_attachment=True,
                        #                        download_name=csv_filename  # This is the key parameter for the filename
                        download_name=original_filename,  # This is the key parameter for the filename
                    )
                    return response

                finally:
                    # Clean up the CSV file after sending
                    if os.path.exists(csv_path):
                        os.remove(csv_path)

            except Exception as e:
                flash(f"Error: {str(e)}")
                return render_template("upload.html")
        else:
            flash("Please upload a .log file")
            return render_template("upload.html")

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
