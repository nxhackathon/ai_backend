cmake_minimum_required(VERSION 3.10.2)

project(sclbl-integration-examples)

# Add Scailable C Utilities for all subprojects
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities/include)

# # Add C Postprocessor project
# add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-c-example)

# # Add C Image Postprocessor project
# add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-c-image-example)

# # Add C Raw Postprocessor project
# add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-c-raw-example)

# Add Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-cereal)

# Add Image Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-fish)

# # Add installation option
install(TARGETS
    # postprocessor-c-example
    # postprocessor-c-image-example
    # postprocessor-c-raw-example
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)
install(PROGRAMS
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-example/postprocessor-python-cereal
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-example-2/postprocessor-python-fish
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)