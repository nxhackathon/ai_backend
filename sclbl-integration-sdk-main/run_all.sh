cmake .
make


rm  /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-cereal
cp /home/deb/Desktop/nx_codes/sclbl-integration-sdk-main/postprocessor-python-cereal/postprocessor-python-cereal /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
cp /home/deb/Desktop/nx_codes/sclbl-integration-sdk-main/external_postprocessors.json /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-cereal
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json


rm  /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-fish
cp /home/deb/Desktop/nx_codes/sclbl-integration-sdk-main/postprocessor-python-fish/postprocessor-python-fish /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
cp /home/deb/Desktop/nx_codes/sclbl-integration-sdk-main/external_postprocessors.json /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-fish
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json

ls -la /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors