from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("ccpt.html")


@app.route("/save-ccpt", methods=["POST"])
def save_ccpt():

    data = {
        "customer_name": request.form.get("customerName"),
        "cif": request.form.get("cif"),
        "account_no": request.form.get("accountNo"),

        "bnm_sector": request.form.get("bnmSector"),
        "other_sector": request.form.get("otherSector"),

        "principal_activities": request.form.get("principalActivities"),
        "business_location": request.form.get("businessLocation"),

        "financing_type": request.form.get("financingType"),
        "purpose": request.form.get("purpose"),

        "assessment_type": request.form.get("assessmentType"),

        "esg": request.form.get("esg"),

        "green_company": request.form.get("greenCompany"),
        "green_industry": request.form.get("greenIndustry"),

        "ccpt": request.form.get("ccpt"),

        "corporate_status": request.form.get("corporateStatus"),

        "prepared_by": request.form.get("preparedBy"),
        "reviewed_by": request.form.get("reviewedBy"),
        "endorsed_by": request.form.get("endorsedBy"),
    }

    # For testing:
    print("=" * 60)
    print("CCPT APPLICATION RECEIVED")
    print("=" * 60)

    for key, value in data.items():
        print(f"{key}: {value}")

    return {
        "success": True,
        "message": "Application information saved successfully."
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )