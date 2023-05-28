import streamlit as st
from flask import Flask, request
import socket
import numpy as np
import pandas as pd
import io
import cv2
import json
import base64
import os
from PIL import Image
import plotly.express as px
import requests
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import streamlit.components.v1 as components
#custom
from custom.credentials import token, account
from custom.essentials import stringToRGB, get_model
from custom.whatsapp import whatsapp_message
from validation import input_validation
import re
from io import StringIO

from pathlib import Path
import sys


st.set_page_config(
    page_icon='🤝',
    page_title='Skin Disease Analyzer')

file_path = Path(__file__).resolve()
# Get the parent directory of the current file
root_path = file_path.parent
# Add the root path to the sys.path list if it is not already there
if root_path not in sys.path:
    sys.path.append(str(root_path))
# Get the relative path of the root directory with respect to the current working directory
ROOT = root_path.relative_to(Path.cwd())

MODELSPATH = ROOT / 'models/'
DATAPATH = ROOT / 'data/'

def render_header():
    st.write("""
        <p align="center"> 
            <H1> Skin cancer Analyser 
        </p>

    """, unsafe_allow_html=True)

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_animation_1 = "https://assets5.lottiefiles.com/packages/lf20_LmW6VioIWc.json"
predicting = "https://assets5.lottiefiles.com/private_files/lf30_jbhavmow.json"

lottie_anime_json = load_lottie_url(lottie_animation_1)
lottie_predicting_json = load_lottie_url(predicting) 

def load_mekd():
    img = cv2.imread('data/ISIC_0024312.jpg')
    return img

def disease_detect(result_img, patient_name, patient_contact_number, doctor_name, doctor_contact_number):
  
    model_name = 'models/best_model_sorted_200.h5'
    model = get_model()
    model.load_weights(model_name)
    classes = {6: ('nv', ' melanocytic nevi'), 4: ('mel', 'melanoma'), 2 :('bkl', 'benign keratosis-like lesions'), 1:('bcc' , ' basal cell carcinoma'), 5: ('vasc', ' pyogenic granulomas and hemorrhage'), 0: ('akiec', 'Actinic keratoses and intraepithelial carcinomae'),  3: ('df', 'dermatofibroma')}
    img = cv2.resize(result_img, (28, 28))
    result = model.predict(img.reshape(1, 28, 28, 3))
    result = result[0]
    max_prob = max(result)

    if max_prob>0.80:
        class_ind = list(result).index(max_prob)
        class_name = classes[class_ind]
        short_name = class_name[0]
        full_name = class_name[1]
        # st.success("**Prediction:** Patient is suffering from ", full_name)
        st.error('**Prediction:** Patient is suffering from  {}'.format(full_name))
    

    else:
        full_name = 'No Disease' #if confidence is less than 80 percent then "No disease" 
        st.success('**Prediction:** Patients Skin is Healthy, No Disease detected')
        
    #whatsapp message
    message = '''
    Patient Name: {}
    Doctor Name: {}
    Disease Name : {}
    Confidence: {}

    '''.format(patient_name, doctor_name, full_name, max_prob)
    
    #send whatsapp mesage to patient
    whatsapp_message(token, account, patient_contact_number, message)
    # sleep(5)
    whatsapp_message(token, account, doctor_contact_number, message)
    return 'Success'

def Skin_detect(result_img, patient_name, patient_contact_number, doctor_name, doctor_contact_number):
  

    model_name = 'models/skin2_disease_model.h5'
    model = get_model()
    model.load_weights(model_name)
    classes = { 0:('HAM10000_images_part_2' , ' Diseased'), 1: ('FOCAL_1', 'Healthy')}
    input_image_path = '/content/drive/MyDrive/ham/HAM10000_images_part_2/ISIC_0029306.jpg'
    img = cv2.imread(input_image_path)
    img = cv2.resize(img, (28, 28))
    result = model.predict(img.reshape(1, 28, 28, 3))
    # result = result[0]
    # print(result)
    # max_prob = max(result)
    # print(max_prob)
    if result[0][0]<0.50:
        # class_ind = list(result).index(max_prob)
        # class_name = classes[class_ind]
        # short_name = class_name[0]
        # full_name = class_name[1]
        print('Skin is diseased')
    

    else:
      
        print('Skin is Healthy, No Disease detected')

def main():

    # Initialize the session state variable if it doesn't exist yet

    menu = ["About Us", "Info", "App"]
    choice = st.sidebar.selectbox("Select a page", menu)

    if choice == "Info":

        
        st.title('Skin cancer Analyser')
        st.markdown('The Skin Analyzer app is a web-based application designed to analyze skin images and provide predictions and classifications for various skin diseases. The app offers a user-friendly interface with multiple functionalities to enhance the user experience. ')
        st.header("Instructions")
        st.markdown("""
        Welcome to the Skin Analyzer App! Here's how you can use it:

        1. **Sample Image Prediction**: Choose a sample image to get predictions for common skin diseases.
        2. **Upload Your Skin Image**: Upload your own skin image to analyze and obtain disease predictions.
        3. **Prediction Results**: View the results of the disease prediction, including the disease name and confidence level.
        4. **WhatsApp Communication**: Stay connected with your doctor by receiving prediction details via WhatsApp.
        5. **Real-Time Analysis**: Experience immediate feedback with real-time analysis of your skin image.
        6. **User-Friendly Interface**: Enjoy a user-friendly interface with easy navigation options.
        7. **Privacy and Security**: Rest assured that your privacy and security are our top priorities.
        8. **Future Enhancements**: Stay tuned for future updates and enhancements to the app.

        Feel free to explore the different features and functionalities of the app. If you have any questions or need assistance, don't hesitate to reach out to our support team.

        Let's get started!

        Go to the select page option to the extream left sidebar of the page and choose app option to get started
         """)
        st_lottie(lottie_anime_json, key = "hello")
    elif choice == "About Us":
                    # front end elements of the web page 
        html_temp = """ 
        <div style ="background-color:white;padding:13px"> 
        <h1 style ="color:brown;text-align:center;font-size: 52px">Skin Disease Detection and Classification</h1> 
        </div> 
        """
        # display the front end aspect
        img1 = Image.open(ROOT / 'html_images/kjsce_header.jpeg')
        img2 = Image.open(ROOT / 'html_images/names1.jpeg')
        
        st.image(img1, width=704)
        st.markdown(html_temp, unsafe_allow_html = True) 
        st.markdown("")
        st.image(img2, width=704)

    elif choice == "App":

        st_lottie(lottie_predicting_json, speed=1, width=200, height=200, key = "hello")

        st.sidebar.header('Skin cancer Analyser')
        st.sidebar.subheader('Choose a page to proceed:')
        page = st.sidebar.selectbox("", ["Sample Image", "Upload Your Skin Image"])

        if page == "Sample Image":
            st.header("Sample Image Prediction for Skin Cancer")
            st.markdown("""
            *Now, this is probably why you came here. Let's get you some Predictions*

            You need to choose Sample Image
            """)

            mov_base = ['Sample Image I']
            movies_chosen = st.multiselect('Choose Sample Image', mov_base)

            if len(movies_chosen) > 1:
                st.error('Please select Sample Image')
            if len(movies_chosen) == 1:
                st.success("You have selected Sample Image")
            else:
                st.info('Please select Sample Image')

            if len(movies_chosen) == 1:
                if st.checkbox('Show Sample Image'):
                    st.info("Showing Sample Image---->>>")
                    result_img = load_mekd()
                    st.image(result_img, caption='Sample Image', channels="BGR", use_column_width=True)
                    st.subheader("Choose Training Algorithm!")
                    
                    if st.checkbox('Detection'):
                        model = get_model()
                    
                        st.success("Hooray !! Detection Model Loaded!")
                        if st.checkbox('Enter Doctor & Patients Details'):
                            with st.form("Details form"):
                                patient_name = st.text_input("Patient's Name")
                                patient_contact_number = st.text_input("Patient's Contact Number")
                                # doctor_name = st.text_input("Doctor's Name")
                                doctor_name = st.selectbox('Select name', ['vaibhavi' , 'Deepak'])
                                #doctor_contact_number = st.text_input("Doctor's Contact Number")
                                doctor_contact_number = st.selectbox('Doctor Number', ['+917715987005', '+918097129725'], key=1)

                                if st.form_submit_button("Predict and Send"):
                                    input_validation(patient_name, patient_contact_number, doctor_name, doctor_contact_number)
                                    result = Skin_detect(result_img, patient_name, patient_contact_number, doctor_name, doctor_contact_number)
                                    st.success("Whatsapp message sent successfully!")
                        
                    if st.checkbox('model1'):
                        model = get_model()
                    
                        st.success("Hooray !! Keras Model Loaded!")
                        if st.checkbox('Enter Doctor & Patients Details'):
                            with st.form("Details form"):
                                patient_name = st.text_input("Patient's Name")
                                patient_contact_number = st.text_input("Patient's Contact Number")
                                # doctor_name = st.text_input("Doctor's Name")
                                doctor_name = st.selectbox('Select name', ['vaibhavi' , 'Deepak'])
                                #doctor_contact_number = st.text_input("Doctor's Contact Number")
                                doctor_contact_number = st.selectbox('Doctor Number', ['+917715987005', '+918097129725'], key=1)

                                if st.form_submit_button("Predict and Send"):
                                    input_validation(patient_name, patient_contact_number, doctor_name, doctor_contact_number)
                                    result = disease_detect(result_img, patient_name, patient_contact_number, doctor_name, doctor_contact_number)
                                    st.success("Whatsapp message sent successfully!")

        if page == "Upload Your Skin Image":

            st.header("Upload Your Skin Image")

            uploaded_file = st.file_uploader('Upload an image', type=['png', 'jpg'])

            if uploaded_file is not None:
                file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                # st.image(image, channels="BGR")
                # image = cv2.imread(uploaded_file)
                img_array = np.array(image)

                st.success('File Upload Success!!')
            else:
                st.info('Please upload Image file')

            if st.checkbox('Show Uploaded Image'):
                st.info("Showing Uploaded Image ---->>>")
                st.image(img_array, channels="BGR", caption='Uploaded Image',
                        use_column_width=True)
                st.subheader("Choose Training Algorithm!")
                if st.checkbox('Keras'):
                    model = get_model()
                    st.success("Hooray !! Keras Model Loaded!")
                    if st.checkbox('Enter Doctor & Patients Details'):
                        with st.form("Details form"):
                            #patient_name = st.text_input("Patient's Name")
                            #patient_contact_number = st.text_input("Patient's Contact Number")
                            #doctor_name = st.text_input("Doctor's Name")
                            #doctor_contact_number = st.text_input("Doctor's Contact Number")
                            patient_name = st.text_input("Patient's Name")
                            patient_contact_number = st.text_input("Patient's Contact Number")
                            #doctor_name = st.selectbox('Doctor data', ['Vaibhavi', 'Deepak'], key=1)
                            doctor_name = st.selectbox('Select name', ['vaibhavi' , 'Deepak'])
                            doctor_contact_number = st.selectbox('Doctor Number', ['+917715987005', '+918097129725'], key=1)

                            if st.form_submit_button("Predict and Send"):
                                input_validation(patient_name, patient_contact_number, doctor_name, doctor_contact_number)
                                result_img = image
                                result = disease_detect(result_img, patient_name, patient_contact_number, doctor_name, doctor_contact_number)
                                st.success("Whatsapp message sent successfully!")


if __name__== "__main__":
    main()
