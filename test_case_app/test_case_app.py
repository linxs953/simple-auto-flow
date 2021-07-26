import os
from threading import Thread
import pytest
import uuid
from flask import Blueprint, jsonify, request, current_app, render_template

test = Blueprint('test', __name__, template_folder='templates')
cur_dir = os.path.dirname(__file__).split('server')[0]


@test.route('/cases', methods=["GET"])
def show_cases():
	file_names = []
	path = r'example/tests'
	try:
		dir_list = os.listdir(path)
		for i in range(0, len(dir_list)):
			filename = os.path.splitext(dir_list[i])[0]
			if filename != '__init__':
				file_names.append(filename)
			current_app.logger.info('{}以展示'.format(filename))
	except Exception as e:
		current_app.logger.info(e)
	return render_template('cases_list.html', cases=sorted(file_names))


# lista = ["uiplatform/utils/business/cycle_check/test_check_web.py::TestHinfo"]
# lista.append(pares)
# Thread(target=lambda: pytest.main(lista)).start()
# return jsonify(code=200, msg="ok", data={"session_id": session_id})

# @user.route('/ui_test/test3', methods=["GET"])
# def run_only_test3():
# 	session_id = uuid.uuid1()
# 	pares = f"--seid={session_id}"
# 	lista = ["-n 3", "uiplatform/utils/business/cycle_check/test_check_web.py::TestHinfo"]
# 	lista.append(pares)
# 	Thread(target=lambda: pytest.main(lista)).start()
# 	return jsonify(code=200, msg="ok", data={"session_id": session_id})
