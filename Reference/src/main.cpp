/**
 * Schoenflies
 * Copyright (c) 2021 Luuk Kempen
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include "main.h"

int main(int argc, char** argv) {
    if (argc > 1) {
        // parse command-line arguments
        return main_cmd(argc, argv);
    } else {
        // no command-line arguments given, launch GUI
        return main_gui(argc, argv);
    }
}

/**
 * @brief Run Schoenflies with command-line arguments.
 *
 * @param argc argument count
 * @param argv argument vector
 * @return int return code
 */
int main_cmd(int argc, char** argv) {
    po::options_description cmdline("Command-line options");
    cmdline.add_options()
        ("help,h", "produce help message")
        ("version", "print version string")
        ("input-file,i", po::value<std::string>(), "input structure file");

    po::variables_map vm;

    // parse options
    try {
        po::store(po::parse_command_line(argc, argv, cmdline), vm);
        po::notify(vm);
    } catch (std::exception& e) {
        std::cout << e.what() << std::endl;
        std::cout << cmdline << std::endl;
        return -1;
    }

    // check for --help and --version: exit early
    if (vm.count("help")) {
        std::cout << "Run " PROGRAM_NAME " without any command-line options to start the GUI." << std::endl;
        std::cout << PROGRAM_NAME " can also be run with command-line options, in which case the GUI will not start." << std::endl;
        std::cout << "Instead, output will be returned to the command line." << std::endl << std::endl;
        std::cout << cmdline << std::endl;
        return 0;
    }

    if (vm.count("version")) {
        std::cout << PROGRAM_NAME ": " PROGRAM_DESC ", version " PROGRAM_VERSION << std::endl;
        return 0;
    }

    CmdHandler cmd_handler = CmdHandler(vm["input-file"].as<std::string>());
    return cmd_handler.handle();
}

/**
 * @brief Run the Schoenflies GUI.
 *
 * @param argc argument count
 * @param argv argument vector
 * @return int return code
 */
int main_gui(int argc, char** argv) {
    // configure application attributes
    QApplication::setAttribute(Qt::ApplicationAttribute::AA_EnableHighDpiScaling);
    QApplication::setHighDpiScaleFactorRoundingPolicy(Qt::HighDpiScaleFactorRoundingPolicy::PassThrough);

    // create application
    QApplication app(argc, argv);

    // configure OpenGL
    QSurfaceFormat fmt;
    fmt.setDepthBufferSize(24);
    fmt.setSamples(4);
    fmt.setVersion(3, 3);
    fmt.setProfile(QSurfaceFormat::CoreProfile);
    fmt.setSwapBehavior(QSurfaceFormat::DoubleBuffer);
    QSurfaceFormat::setDefaultFormat(fmt);

    std::unique_ptr<MainWindow> main_window;

    try {
        // build main window
        main_window = std::make_unique<MainWindow>();
        main_window->resize(800, 600);
    } catch (std::exception& e) {
        std::cout << e.what() << std::endl;
        return -1;
    }

    main_window->show();

    return app.exec();
}
