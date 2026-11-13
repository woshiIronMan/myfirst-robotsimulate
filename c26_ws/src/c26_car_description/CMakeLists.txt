cmake_minimum_required(VERSION 3.16)
project(c26_car_description)

find_package(ament_cmake REQUIRED)
find_package(dwb_core REQUIRED)
find_package(pluginlib REQUIRED)

add_library(c26_dwb_critics SHARED src/cardinal_motion_critic.cpp)
target_link_libraries(c26_dwb_critics PRIVATE dwb_core::dwb_core pluginlib::pluginlib)
pluginlib_export_plugin_description_file(dwb_core c26_dwb_critics.xml)
install(TARGETS c26_dwb_critics LIBRARY DESTINATION lib)

install(DIRECTORY urdf launch config worlds meshes maps
        DESTINATION share/${PROJECT_NAME})

install(PROGRAMS
          scripts/mecanum_drive.py
          scripts/c26_drive.py
          scripts/test_motion.py
          scripts/probe_patterns.py
          scripts/roller_check.py
        DESTINATION lib/${PROJECT_NAME})

ament_package()
