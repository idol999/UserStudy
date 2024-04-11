import json
import streamlit as st
from PIL import Image
import os
import csv
from datetime import datetime

def load_and_resize_image(path, target_size):
    img = Image.open(path)
    img = img.resize(target_size, resample=Image.LANCZOS)
    return img


def load_json(path):
    with open(path, 'r',encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_scores_to_csv(scores, session_id):
    filename = f'scores_{session_id}.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Model'] + task_dir
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for model_name, model_scores in scores.items():
            row = {'Model': model_name}
            row.update(model_scores)
            writer.writerow(row)
task_dir = ['BGReplacement', 'ColorAlteration', 'Counting', 'Deblurring', 'DirectionPerception', 'HazeRemoval',
            'Lowlight', 'NoiseRemoval', 'ObjectRemoval', 'RainRemoval', 'RegionAccuracy', 'Replacement', 'ShadowRemoval',
            'SnowRemoval', 'StyleAlteration', 'WatermarkRemoval']

model = ['any2pix', 'hive', 'iedit', 'instruct-diffusion', 'instructpix2pix', 'magicbrush', 'mgie']
# Check if 'session_state' is already set, if not, create an empty dictionary
if 'user_choice' not in st.session_state:
    st.session_state['user_choice'] = ''
    st.session_state['task_index'] = 0
    st.session_state['model_index'] = 0
    st.session_state['scores'] = {model_name: {task_name: 0 for task_name in task_dir} for model_name in model}
session_id = f"{st.session_state['task_index']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# UI Elements
st.title("Image Editing Evaluation")
work_dir = os.path.join("data", "dataset1")
target_size = (250, 200)
choices = ['1', '2', '3', '4', '5']

task_index = st.session_state['task_index']
model_index = st.session_state['model_index']

if st.session_state['model_index'] >= len(model):
    st.session_state['model_index'] = 0
    st.session_state['task_index'] += 1

task_index = st.session_state['task_index']
model_index = st.session_state['model_index']

if st.session_state['task_index'] >= len(task_dir):
    st.markdown("#### " + "All tasks completed! Thank you.")
    session_id = f"{st.session_state['task_index']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    save_scores_to_csv(st.session_state['scores'], session_id)
    st.markdown("#### " + "Data saved successfully!")
    st.stop()

task = task_dir[task_index]
model_name = model[model_index]

pre = os.path.join(work_dir, task)
# load json
js = task + '.json'
json_path = os.path.join(pre, js)
data = load_json(json_path)

image = data["1"]["image"]
if task != "RegionAccuracy" :
    prompt = data["1"]["ori_exp"]
    prompt_ch = data["1"]["exp_ch"]
    mkd = '[Prompt]: ' + prompt
    mkd_ch = '[提示]: ' + prompt_ch
    st.markdown("#### " + mkd)
    st.markdown("#### " + mkd_ch)
    st.markdown("-----")
    path_A = os.path.join(os.path.join(pre, "input"), image)
    path_B = os.path.join(os.path.join(pre, model_name), image)
    img_A = load_and_resize_image(path_A, target_size)
    img_B = load_and_resize_image(path_B, target_size)
    col1, col2 = st.columns(2)
    with col1:
        st.write("Original image :camera:")
        st.image(img_A, use_column_width=True)

    with col2:
        st.write(f"Edited by {model_name} :camera:")
        st.image(img_B, use_column_width=True)
    # Sidebar
    with st.sidebar:
        st.title('How do you rate the editing results?')
        st.write('你如何评价编辑结果？')
        st.write('1分最差，5分最好')
        st.markdown('--------')

        user_choice = st.radio('Choice', choices, key='radio')

        st.session_state['user_choice'] = user_choice

        if st.button('Submit'):
            score = int(st.session_state['user_choice'])
            st.session_state['scores'][model_name][task] += score
            st.session_state['model_index'] += 1
            # save_scores_to_csv(st.session_state['scores'], session_id)
            st.experimental_rerun()
else:
    image = data["0"]["image"]
    prompt = data["0"]["ori_exp"]
    prompt_ch = data["0"]["exp_ch"] + " (mask区域为需要编辑的区域)"
    mkd = '[Prompt]: ' + prompt
    mkd_ch = '[提示]: ' + prompt_ch
    st.markdown("#### " + mkd)
    st.markdown("#### " + mkd_ch)
    st.markdown("-----")
    mask = data["0"]["mask"]
    path_A = os.path.join(os.path.join(pre, "input"), image)
    path_B = os.path.join(os.path.join(pre, "mask"), mask)
    path_C = os.path.join(os.path.join(pre, model_name), image)
    img_A = load_and_resize_image(path_A, target_size)
    img_B = load_and_resize_image(path_B, target_size)
    img_C = load_and_resize_image(path_C, target_size)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Original image :camera:")
        st.image(img_A, use_column_width=True)
    with col2:
        st.write("Mask image :camera:")
        st.image(img_B, use_column_width=True)
    with col3:
        st.write(f"Edited by {model_name} :camera:")
        st.image(img_C, use_column_width=True)
    # Sidebar
    with st.sidebar:
        st.title('How do you rate the editing results?')
        st.write('你如何评价在mask区域中的编辑结果？')
        st.write('1分最差，5分最好')
        st.markdown('--------')

        user_choice = st.radio('Choice', choices, key='radio')

        st.session_state['user_choice'] = user_choice

        if st.button('Submit'):
            score = int(st.session_state['user_choice'])
            st.session_state['scores'][model_name][task] += score
            st.session_state['model_index'] += 1
            # save_scores_to_csv(st.session_state['scores'], session_id)
            st.experimental_rerun()