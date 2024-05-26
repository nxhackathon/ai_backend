cd /home/deb/Desktop/nx_codes/sclbl-integration-sdk-main
cmake .
make
rm  /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-example
cp /home/deb/Desktop/nx_codes/sclbl-integration-sdk-main/postprocessor-python-example/postprocessor-python-example /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-example
chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json