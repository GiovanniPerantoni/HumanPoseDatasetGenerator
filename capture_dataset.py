import csv
import pyzed.sl as sl
import time

# times are expressed in seconds
TIMESTEP = 0.1
TOTAL_TIME = 60

# please refer to the model 'body34' for number-joint map
# you can find it at: https://www.stereolabs.com/docs/body-tracking 
JOINT_DICT = {
    0: ['Pelvis', True],
    1: ['Naval_Spine', True],
    2: ['Chest_Spine', True],
    3: ['Neck', True],
    4: ['Left_Clavicle', True],
    5: ['Left_Shoulder', True],
    6: ['Left_Elbow', True],
    7: ['Left_Wrist', True],
    8: ['Left_Hand', False],
    9: ['Left_Handtip', False],
    10: ['Left_Thumb', False],
    11: ['Right_Clavicle', True],
    12: ['Right_Shoulder', True],
    13: ['Right_Elbow', True],
    14: ['Right_Wrist', True],
    15: ['Rigth_Hand', False],
    16: ['Right_Handtip', False],
    17: ['Right_Thumb', False],
    18: ['Left_Hip', True],
    19: ['Left_knee', False],
    20: ['Left_Ankle', False],
    21: ['Left_Foot', False],
    22: ['Right_Hip', True],
    23: ['Right_Knee', False],
    24: ['Right_Ankle', False],
    25: ['Right_Foot', False],
    26: ['Head', False],
    27: ['Nose', False],
    28: ['Left_Eye', False],
    29: ['Left_Ear', False],
    30: ['Right_Eye', False],
    31: ['Right_Ear', False],
    32: ['Left_Heel', False],
    33: ['Right_Heel', False],
}


def main():
    # Create a camera object
    zed = sl.Camera()

    # Define initialization parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init_params.coordinate_units = sl.UNIT.METER
    init_params.sdk_verbose = 1

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : " + repr(err) + ". Exit Program")
        exit()

    # Define body tracking parameters
    body_params = sl.BodyTrackingParameters()
    body_params.body_format = sl.BODY_FORMAT.BODY_34
    body_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_FAST
    body_params.enable_tracking = True
    body_params.enable_segmentation = False
    body_params.enable_body_fitting = True # WARNING: computationally heavier

    # Define positional tracking parameters if enabled
    if body_params.enable_tracking:
        positional_tracking_param = sl.PositionalTrackingParameters()
        positional_tracking_param.set_floor_as_origin = True
        zed.enable_positional_tracking(positional_tracking_param)

    # Load body tracking module
    print("Body tracking: loading module...")
    err = zed.enable_body_tracking(body_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Enable Body Tracking : " + repr(err) + ". Exit program.")
        zed.close()
        exit()

    # Define body tracking parameters
    bodies = sl.Bodies()
    body_runtime_param = sl.BodyTrackingRuntimeParameters()
    body_runtime_param.detection_confidence_threshold = 40


    current_time = 0
    with open('dataset.csv', 'w', newline='') as f:
        f_writer = csv.writer(f, delimiter=',')
        labels = ['timestep', 'ID', 'pos.x', 'pos.y', 'pos.z']
        for key in JOINT_DICT:
            if JOINT_DICT[key][1]:
               labels.append(JOINT_DICT[key][0]) 
        f_writer.writerow(labels)

        print("Starting record in:")
        print(" 3")
        time.sleep(1)
        print(" 2")
        time.sleep(1)
        print(" 1")
        time.sleep(1)
        print("Recording...")
        start = time.time()
        while current_time < TOTAL_TIME:
            if zed.grab() == sl.ERROR_CODE.SUCCESS:
                err = zed.retrieve_bodies(bodies, body_runtime_param)
                if bodies.is_new:
                    body_array = bodies.body_list
                    if len(body_array) > 0:
                        first_body = body_array[0]
                        data = []
                        data.append(current_time)
                        data.append(first_body.id)
                        data.extend(first_body.position)
                        for key in JOINT_DICT:
                            if JOINT_DICT[key][1]:
                                data.append(first_body.keypoint[key])
                        f_writer.writerow(data)
            print(current_time)
            time.sleep(TIMESTEP)
            current_time += TIMESTEP
            end = time.time()
        f.close()

    # Close the camera
    zed.disable_body_tracking()
    zed.close()

    print("Elapsed: ", end-start)



if __name__ == "__main__":
    main()


