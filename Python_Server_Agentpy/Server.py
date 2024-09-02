from flask import Flask, request, jsonify, g
import json
import traceback
from RobotAgent import ObjectStackingModel, RobotAgent, onto

app = Flask(__name__)

def init_model_and_states():
    parameters = {
        'num_cams': 5,
        'num_dron': 1,
        'num_secper': 1,
    }
    model = SecurityDepartmentModel(parameters)
    model.setup()
    Security_Dep_States = {robot.onto_robot.id: robot.get_state() for robot in model.robots}
    return model, robot_states



@app.before_request
def before_request():
    if not hasattr(app, 'model') or not hasattr(app, 'robot_states'):
        app.model, app.robot_states = init_model_and_states()
    app.logger.debug(f"Current robot states: {app.robot_states}")


@app.route('/gmes', methods=['POST'])
def robot_actions():
    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")

        if not isinstance(data, list):
            return jsonify({"error": "Invalid input. Expected an array of robot perceptions."}), 400

        actions = []

        for robot_perception in data:
            if 'id' not in robot_perception or 'position' not in robot_perception:
                return jsonify({"error": "Invalid input. Each robot perception must have 'id' and 'position'."}), 400

            robot_id = robot_perception['id']
            perception = robot_perception['position']

            robot = next((r for r in app.model.robots if r.onto_robot.id == robot_id), None)
            if robot is None:
                app.logger.error(f"Robot with id {robot_id} not found.")
                continue

            #HACIA DONDE ESTA HACIENDO ESTA REQUEST DE INFO
            #======================================================
            stored_state = app.robot_states.get(robot_id)
            #======================================================
            app.logger.debug(f"Processing robot: {robot_id}, Stored state: {stored_state}")

            perception_json = json.dumps({
                "id": robot_id,
                "position": perception
            })

            try:
                action = robot.step(perception_json, stored_state)
                app.logger.debug(f"Action taken by robot {robot_id}: {action}")
                
                action_parts = action.split('_')
                action_type = action_parts[0]
                direction = action_parts[1] if len(action_parts) > 1 else None

                actions.append({
                    "id": robot_id,
                    "action": action_type.capitalize()[0],
                    "direction": direction
                })

                app.model.update_environment(robot, action)

                app.robot_states[robot_id] = robot.get_state()
                app.logger.debug(f"Updated state for robot {robot_id}: {app.robot_states[robot_id]}")

            except Exception as e:
                app.logger.error(f"Error in robot.step() for robot {robot_id}: {str(e)}")
                app.logger.error(traceback.format_exc())

        app.model.current_step += 1

        if app.model.check_end_condition():
            app.logger.info("Simulation ended")
            app.model.end()

        app.logger.debug(f"Final robot states after this step: {app.robot_states}")
        return jsonify(actions)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)