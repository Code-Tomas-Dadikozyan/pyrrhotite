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

#ifndef MAIN_H
#define MAIN_H

#include <iostream>
#include <memory>
#include <string>
#include <boost/program_options.hpp>
#include <QApplication>
#include <QPushButton>
#include <QSurfaceFormat>
#include "cmd_handler.h"
#include "program.h"
#include "gui/main_window.h"

namespace po = boost::program_options;

/**
 * @brief Run Schoenflies with command-line arguments.
 *
 * @param argc argument count
 * @param argv argument vector
 * @return int return code
 */
int main_cmd(int argc, char** argv);

/**
 * @brief Run the Schoenflies GUI.
 *
 * @param argc argument count
 * @param argv argument vector
 * @return int return code
 */
int main_gui(int argc, char** argv);

#endif  // MAIN_H
