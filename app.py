from flask import Flask, render_template, request, send_file
import pandas
import csv

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/return_files')
def return_template():
    try:
        return send_file('files/allocations_template.csv')
    except Exception as e:
        return str(e)


@app.route('/return_allocations')
def return_csv():
    try:
        return send_file('allocations.csv')
    except Exception as e:
        return str(e)


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    try:
        weeks_of_placements = request.form['weeks-of-placements']
        maximum_of_general = request.form['maximum-of-general']
        weeks_in_orthopaedics = request.form['orthopaedics']
        weeks_in_ophthalmology = request.form['ophthalmology']
        weeks_in_fcs = request.form['fcs']
        weeks_in_obstetrics = request.form['obstetrics']
        weeks_in_paediatrics = request.form['paediatrics']

        overall_df = pandas.read_csv(request.files.get('csv'), skipinitialspace=True)

        id_list = overall_df['student_id'].tolist()
        id_dict = {}

        for id in id_list:
            if id in id_dict:
                id_dict[id] += 1
                return render_template('index.html', success=False, error_message='Duplicate(s) in student_id')
            else:
                id_dict[id] = 1

        student_df = overall_df[['student_id', 'student_name']].copy()
        student_df.dropna(subset=['student_id'], inplace=True)

        student_list = []

        for index, row in student_df.iterrows():
            student_dict = {'student_id': row['student_id'], 'student_name': row['student_name'],
                            'weeks_left': int(weeks_of_placements),
                            'weekly_allocation': ['No Placement'] * int(weeks_of_placements)}
            student_list.append(student_dict)

        hospital_fields = ['hospital_name', 'speciality']
        week_list = []

        for col in overall_df.columns:
            if 'week_' in col:
                hospital_fields.append(col)
                week_list.append(col)

        hospital_df = overall_df[hospital_fields]

        hospital_list = []

        for index, row in hospital_df.iterrows():
            hospital_dict = {'name': row['hospital_name'], 'weekly_capacity': row[week_list].values.tolist(),
                             'speciality': row['speciality']}
            hospital_list.append(hospital_dict)

        sorted_list = []

        for hospital in hospital_list:
            if hospital['speciality'] != 'General':
                sorted_list.append(hospital)

        for hospital in hospital_list:
            if hospital['speciality'] == 'General':
                sorted_list.append(hospital)

        orthopaedics_hospital_names = [h['name'] for h in hospital_list if h['speciality'] == 'Orthopaedics']
        ophthalmology_hospital_names = [h['name'] for h in hospital_list if h['speciality'] == 'Ophthalmology']
        obstetrics_hospital_names = [h['name'] for h in hospital_list if h['speciality'] == 'Obstetrics']
        paediatrics_hospital_names = [h['name'] for h in hospital_list if h['speciality'] == 'Paediatrics']

        for student in student_list:
            for hospital in sorted_list:
                if 'No Placement' not in student['weekly_allocation']:
                    break
                orthopaedics_count = sum([student['weekly_allocation'].count(name) for name in
                                          orthopaedics_hospital_names])
                if orthopaedics_count == int(weeks_in_orthopaedics) and hospital['name'] in orthopaedics_hospital_names:
                    continue
                ophthalmology_count = sum([student['weekly_allocation'].count(name) for name in
                                           ophthalmology_hospital_names])
                if ophthalmology_count == int(weeks_in_ophthalmology) and hospital['name'] in \
                        ophthalmology_hospital_names:
                    continue
                obstetrics_count = sum([student['weekly_allocation'].count(name) for name in obstetrics_hospital_names])
                if obstetrics_count == int(weeks_in_obstetrics) and hospital['name'] in obstetrics_hospital_names:
                    continue
                paediatrics_count = sum([student['weekly_allocation'].count(name) for name in
                                         paediatrics_hospital_names])
                if paediatrics_count == int(weeks_in_paediatrics) and hospital['name'] in paediatrics_hospital_names:
                    continue
                fcs_count = student['weekly_allocation'].count('FCS')
                if fcs_count == int(weeks_in_fcs) and hospital['name'] == 'FCS':
                    continue
                week_index = 0
                while week_index != int(weeks_of_placements):
                    if hospital['weekly_capacity'][week_index] > 0:
                        if student['weekly_allocation'][week_index] == 'No Placement':
                            student['weekly_allocation'][week_index] = hospital['name']
                            student['weeks_left'] -= 1
                            new_capacity = hospital['weekly_capacity'][week_index] - 1
                            hospital['weekly_capacity'][week_index] = new_capacity
                            hospital_count = student['weekly_allocation'].count(hospital['name'])
                            if hospital_count == int(maximum_of_general):
                                break
                            orthopaedics_count = sum([student['weekly_allocation'].count(name) for name in
                                                      orthopaedics_hospital_names])
                            if orthopaedics_count == int(weeks_in_orthopaedics) and hospital['name'] in \
                                    orthopaedics_hospital_names:
                                break
                            ophthalmology_count = sum([student['weekly_allocation'].count(name) for name in
                                                       ophthalmology_hospital_names])
                            if ophthalmology_count == int(weeks_in_ophthalmology) and hospital['name'] in \
                                    ophthalmology_hospital_names:
                                break
                            obstetrics_count = sum([student['weekly_allocation'].count(name) for name in
                                                    obstetrics_hospital_names])
                            if obstetrics_count == int(weeks_in_obstetrics) and hospital['name'] in \
                                    obstetrics_hospital_names:
                                break
                            paediatrics_count = sum([student['weekly_allocation'].count(name) for name in
                                                     paediatrics_hospital_names])
                            if paediatrics_count == int(weeks_in_paediatrics) and hospital['name'] in \
                                    paediatrics_hospital_names:
                                break
                            fcs_count = sum([student['weekly_allocation'].count('FCS')])
                            if fcs_count == int(weeks_in_fcs) and hospital['name'] == 'FCS':
                                break

                    week_index += 1

        for student in student_list:
            orthopaedics_count = sum([student['weekly_allocation'].count(name) for name in
                                      orthopaedics_hospital_names])
            if orthopaedics_count != int(weeks_in_orthopaedics):
                return render_template('index.html', success=False,
                                       error_message='More Placements in Orthopaedics Required')
            ophthalmology_count = sum([student['weekly_allocation'].count(name) for name in
                                       ophthalmology_hospital_names])
            if ophthalmology_count != int(weeks_in_ophthalmology) and hospital['name'] in \
                    ophthalmology_hospital_names:
                return render_template('index.html', success=False,
                                       error_message='More Placements in Ophthalmology Required')
            obstetrics_count = sum([student['weekly_allocation'].count(name) for name in obstetrics_hospital_names])
            if obstetrics_count != int(weeks_in_obstetrics) and hospital['name'] in obstetrics_hospital_names:
                return render_template('index.html', success=False,
                                       error_message='More Placements in Obstetrics and Gynaecology Required')
            paediatrics_count = sum([student['weekly_allocation'].count(name) for name in
                                     paediatrics_hospital_names])
            if paediatrics_count != int(weeks_in_paediatrics) and hospital['name'] in paediatrics_hospital_names:
                return render_template('index.html', success=False,
                                       error_message='More Placements in Paediatrics Required')
            fcs_count = student['weekly_allocation'].count('FCS')
            if fcs_count != int(weeks_in_fcs) and hospital['name'] == 'FCS':
                return render_template('index.html', success=False,
                                       error_message='More Placements in FCS Required')

        keys = student_list[0].keys()

        with open('allocations.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(student_list)
            print('Allocations Generated!')

        return render_template('index.html', success=True)

    except Exception as e:
        print(e)
        return render_template('index.html', success=False, error_message=str(e))


if __name__ == '__main__':
    app.run(debug=True)
