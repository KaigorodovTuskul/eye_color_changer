import cv2 as cv
import numpy as np
import mediapipe as mp
import time
import os
import subprocess
import json
import argparse
import shutil

ffmpeg_path = r'ffmpeg'
ffprobe_path = r'ffprobe'

parser = argparse.ArgumentParser()
parser.add_argument('--output-name', type=str, default=None)
parser.add_argument('--input-source', type=str, default=None)
parser.add_argument('--clean-cache', action='store_true')
parser.add_argument('--silent-mode', action='store_true')
parser.add_argument('--sbs-mode', action='store_true')
parser.add_argument('--strength', type=float, default=0.4)
parser.add_argument('--rgb', type=str, default='30, 0, 0')
args = parser.parse_args()

def run_process(input_source):
    def get_video_info(input_source):
        command = [
            ffprobe_path,
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream',
            '-of', 'json',
            input_source
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"ffprobe failed with error: {result.stderr}")

        probe = json.loads(result.stdout)
        stream = probe['streams'][0]
        codec = stream['codec_name']
        width = stream['width']
        height = stream['height']

        try:
            bit_rate = int(float(stream['bit_rate']) / 1_000)
        except:
            bit_rate = int(float(os.path.getsize(input_source)) * 8 / 1_000)

        return width, height, bit_rate, codec

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    )

    LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
    LEFT_IRIS = [474, 475, 476, 477]
    RIGHT_IRIS = [469, 470, 471, 472]

    filename, file_extension = os.path.splitext(input_source)
    filepath = rf"workfolder\{input_source}"

    print(f"File name is {filename}, file extension is {file_extension}")
    input_width, input_height, input_bitrate, input_codec = get_video_info(filepath)

    def create_mask(input_name):
        output_name = rf"temp\{filename}_alpha{file_extension}"

        cap = cv.VideoCapture(input_name)
        frame_width, frame_height = int(cap.get(3)), int(cap.get(4))
        fps = cap.get(cv.CAP_PROP_FPS)

        if ',' in args.rgb:
            eye_color = args.rgb.split(',')
            r, g, b = int(eye_color[0]), int(eye_color[1]), int(eye_color[2])
            eye_color = [b, g, r]
        elif args.rgb == 'black':
            eye_color = [0, 0, 0]
        elif args.rgb == 'white':
            eye_color = [255, 255, 255]
        elif args.rgb == 'blue':
            eye_color = [255, 0, 0]
        elif args.rgb == 'red':
            eye_color = [0, 0, 255]
        elif args.rgb == 'green':
            eye_color = [0, 255, 0]
        elif args.rgb == 'yellow':
            eye_color = [0, 255, 255]
        elif args.rgb == 'brown':
            eye_color = [0, 0, 30]
        else:
            eye_color = [0, 0, 30]
        print(f"eye_color is {eye_color}, strength is {args.strength}")


        if file_extension == '.webm':
            out = cv.VideoWriter(output_name, cv.VideoWriter_fourcc(*'VP80'), fps, (frame_width, frame_height))
        elif file_extension == '.wmv':
            out = cv.VideoWriter(output_name, cv.VideoWriter_fourcc(*'WMV2'), fps, (frame_width, frame_height))
        else:
            out = cv.VideoWriter(output_name, cv.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        cursor = 1
        no_results = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img_h, img_w = frame.shape[:2]
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                mesh_points = np.array(
                    [np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in results.multi_face_landmarks[0].landmark])

                (l_cx, l_cy), l_radius = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
                (r_cx, r_cy), r_radius = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
                center_left, center_right = np.array([l_cx, l_cy], dtype=np.int32), np.array([r_cx, r_cy], dtype=np.int32)

                iris_mask = np.zeros((img_h, img_w), dtype=np.uint8)
                cv.circle(iris_mask, center_left, int(l_radius), 255, -1, cv.LINE_AA)
                cv.circle(iris_mask, center_right, int(r_radius), 255, -1, cv.LINE_AA)

                eye_mask = np.zeros((img_h, img_w), dtype=np.uint8)
                left_eye_points = mesh_points[LEFT_EYE]
                right_eye_points = mesh_points[RIGHT_EYE]
                cv.fillPoly(eye_mask, [left_eye_points], 255)
                cv.fillPoly(eye_mask, [right_eye_points], 255)

                intersection_mask = cv.bitwise_and(iris_mask, eye_mask)
                _, intersection_mask = cv.threshold(intersection_mask, 180, 255, cv.THRESH_BINARY)

                dark_eyes = np.copy(frame)
                dark_eyes[intersection_mask == 255] = eye_color

                alpha = args.strength
                dark_eyes_w = cv.addWeighted(dark_eyes, 1 - alpha, frame, alpha, 0)
                out.write(dark_eyes_w)
            else:
                out.write(frame)

                no_results.append(cursor)

            if not args.silent_mode:
                cv.namedWindow("Modified Eye Video", cv.WINDOW_NORMAL)
                try:
                    cv.imshow("Modified Eye Video", dark_eyes_w)
                except:
                    cv.imshow("Modified Eye Video", frame)

                if args.sbs_mode:
                    cv.resizeWindow("Modified Eye Video", frame_width // 2, frame_height // 2)
                else:
                    cv.resizeWindow("Modified Eye Video", frame_width, frame_height)

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

            print(f"{cursor} / {int(cap.get(cv.CAP_PROP_FRAME_COUNT))}")
            cursor = cursor + 1

        cap.release()
        out.release()
        cv.destroyAllWindows()
        return output_name

    if args.sbs_mode:
        right_filepath = rf"temp\{filename}_right{file_extension}"
        left_filepath = rf"temp\{filename}_left{file_extension}"

        subprocess.run([
            ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'error',
            '-i', filepath,
            '-vf', f"crop={input_width}/2:{input_height}:0:0",
            "-c:v", input_codec,
            "-c:a", "copy",
            "-b:v", f"{str(input_bitrate / 2)}k",
            right_filepath
        ], check=True)
        subprocess.run([
            ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'error',
            '-i', filepath,
            '-vf', f"crop={input_width}/2:{input_height}:{input_width}/2:0",
            "-c:v", input_codec,
            "-c:a", "copy",
            "-b:v", f"{str(input_bitrate / 2)}k",
            left_filepath
        ], check=True)

        right_mask = create_mask(right_filepath)
        left_mask = create_mask(left_filepath)

        merged_path = rf"temp\{filename}_merged{file_extension}"

        subprocess.run([
            ffmpeg_path, '-y', '-hide_banner',
            '-i', left_mask,
            '-i', right_mask,
            '-filter_complex', "[0:v][1:v]hstack=inputs=2",
            "-c:v", input_codec,
            "-c:a", "copy",
            "-b:v", f"{str(input_bitrate)}k",
            merged_path
        ], check=True)
    else:
        merged_path = create_mask(filepath)

    output_name = rf"output\{filename}_output_{args.rgb}{file_extension}"

    subprocess.run([
        ffmpeg_path, '-y', '-hide_banner',
        "-i", filepath,
        "-i", merged_path,
        "-map", "0:1",
        "-c:0", "copy",
        "-map", "1:0",
        "-c:1", "copy",
        "-c:v", input_codec,
        "-b:v", f"{str(input_bitrate)}k",
        output_name
    ], check=True)

    return output_name

if __name__ == '__main__':
    os.makedirs("workfolder", exist_ok=True)
    input_source = args.input_source

    print(f"Found file {input_source}")
    print(f"Arguments: --output-name {args.output_name}, --input-source {args.input_source}, --clean-cache {args.clean_cache}, --silent-mode {args.silent_mode}, --sbs-mode {args.sbs_mode}, --strength {args.strength} --rgb {args.rgb}")
    start_time = time.time()

    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    output_name = run_process(input_source)

    if args.clean_cache:
        shutil.rmtree("temp")

    final_time = round(time.time() - start_time,2)
    print(f"Process {output_name} is completed. Elapsed time is {final_time} s.")