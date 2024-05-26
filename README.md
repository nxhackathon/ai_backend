# ShopkAIper : Nx EVOS: Building Enterprise Scale Video Applications

### Team Members:

1. Anannyo Dey
2. Debasmit Roy
3. Kanko Ghosh
4. Aditya Ganguly
5. Kabir Raj Singh

### OS Requirements: 

- Linux (Ubuntu Latest Version)

### Software Requirements:

- Python 3.9 or higher

### Installation:

1. Clone the repository
2. Run the following command in the terminal:

```bash
pip install python-opencv
pip install numpy
pip install requests
```

### Install Network Optix

Follow the instructions in the link below to install Network Optix:

[Network Optix Installation](https://nx.docs.scailable.net/nx-ai-manager/1.-install-network-optix)

### Install Nx AI Manager

Follow the instructions in the link below to install Nx AI Plugin:

[Nx AI Plugin Installation](https://nx.docs.scailable.net/nx-ai-manager/2.-install-nx-ai-manager-plugin)

### Restart Nx Server

```bash
sudo chmod -R 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin
systemctl restart networkoptix-metavms-mediaserver.service
```

### Install NX Meta

Follow the instructions in the link below to install NX Meta:

[NX Meta Installation](https://meta.nxvms.com/download/releases/linux)

Register and login to the NX Meta application.


## Start the Camera Server

1. Run the following command in the terminal:

```bash
cd camera_server
python3 flaskk.py
```

The camera server will start running on port 8081.
Then setup the camera in the Nx Meta application.
Camera1: http://localhost:8081/v2
Camera2: http://localhost:8081/v3


## Start the Analysis Server

1. Run the following command in the terminal:

```bash
cd analysis_server
python3 flask_anal_server.py
```

The analysis server will start running on port 8888.
It is hosted on AWS as well. The link is: http://ec2-3-142-69-191.us-east-2.compute.amazonaws.com:8888


## Build the Project with make

1. Run the following command in the terminal:

```bash
make
cmake .

cp postprocessor-python-cereal/postprocessor-python-cereal /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
cp external_postprocessors.json /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-cereal

cp postprocessor-python-fish/postprocessor-python-fish /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
cp external_postprocessors.json /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-fish

chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json
```

Check if the files are copied successfully:

```bash
ls -la /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
```

