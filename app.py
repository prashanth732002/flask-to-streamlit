import os
import pandas as pd
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file1 = request.files['file1']
    file2 = request.files['file2']

    if not file1 or not file2:
        return "Please upload both files"

    # Save uploaded files
    path1 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file1.filename))
    path2 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file2.filename))
    file1.save(path1)
    file2.save(path2)

    # Read Excel/CSV
    df1 = pd.read_excel(path1) if file1.filename.endswith('.xlsx') else pd.read_csv(path1)
    df2 = pd.read_excel(path2) if file2.filename.endswith('.xlsx') else pd.read_csv(path2)

    # Ensure column names are stripped of spaces
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Prepare role-wise stacked data
    role_mapping = {
        'AM': ['AM', 'AM Emp ID'],
        'DM': ['DM', 'DM Emp ID'],
        'RM': ['RM', 'RM Emp ID'],
        'SH': ['SH', 'SH Emp ID']
    }

    combined = pd.DataFrame()

    for role, cols in role_mapping.items():
        if all(col in df1.columns for col in ['Branch', 'Branch ID', 'State'] + cols):
            temp = df1[['Branch', 'Branch ID', 'State', cols[0], cols[1]]].copy()
            temp.columns = ['Branch', 'Branch ID', 'State', 'Emp Name', 'Emp ID']
            temp['Role'] = role
            combined = pd.concat([combined, temp], ignore_index=True)

    # Merge with Employment_Status
    if 'Emp ID' in df2.columns:
        merged_df = combined.merge(df2[['Emp ID', 'Employment_Status']], on='Emp ID', how='left')
    else:
        return "Second file must have column 'Emp ID'"

    # Save output
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged_roles.xlsx')
    merged_df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
