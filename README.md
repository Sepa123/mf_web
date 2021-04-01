
# Myocardial-perfusion-and-segmentation-web

API prototype for myocardial magnetic resonance image visualization and segmentation and perfusion curve analysis this prototype has been developed in the Python( 3.6) programming language using Django(3.1) , opencv, scikit, tensorflow (Ver 1.14) and other libraries with the distributor Anaconda. 

# 1. Demo 

To execute the application run "test.py", you can run it via terminal commands or some IDE like PyCharm.

for terminal commands example:

```bash
C:\Users\user>conda activate mf_web

(mf_web) C:\Users\user>cd C:\Users\user\Documents\GitHub\mf_web

(mf_web) C:\Users\user\Documents\GitHub\mf_web>python manage.py runserver
```
just remember to use the delivered virtual environment (environment.yml) and place the path where the project was saved.

In the **"Dataset"** folder you can find images in DICOM format that were used to test the application.


# 2. Installation

## Environment installation

Next, we will explain how to install the environment used to use the program, from installing anaconda to implementing the virtual environment with the **environment.yml** file:

1.	Install the anaconda distributor.
[![](https://assets-cdn.anaconda.com/assets/company/anaconda-logo.png?mtime=20200723150109&focal=none)](https://www.anaconda.com/products/individual#Downloads)

2.	Once installed, you must enter the Anaconda navigator.

3.	go to **"Environments"**, then to **"root"**, press the arrow and press open terminal to create a virtual environment with the following command in the terminal:

```bash
conda env create --file environment.yml
```
With this, the virtual environment is ready to run the application.

## Trained model

The trained model is the algorithm that processes the heart images and delivers the results. To integrate the trained model to the application, you must:

1.	Download model from the following link: https://drive.google.com/file/d/1yKvDG5ozL1sTA0WbBU00TrHb3jZKOLGL/view?usp=sharing
2.	Place the model in the **"segmentation"** folder of the project.

With that the application should work and process the images correctly.

# 3. Notes

1. The "Export results" button is currently unavailable.
