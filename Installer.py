import os

# Install packages
os.system('pip install numpy==1.16.2')
os.system('pip install librosa==0.6.3')
os.system('pip install numba==0.48.0')
os.system('pip install resampy==0.2.2')
os.system('pip install matplotlib')
os.system('pip install unidecode')
os.system('pip install inflect')
os.system('pip install nltk')

# Additional installation commands
os.system('pip install requests')
os.system('conda install pytorch torchvision cpuonly -c pytorch')

open("minvalue.pickle","w+")
open("accesstoken.pickle","w+")