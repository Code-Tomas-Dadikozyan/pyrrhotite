/**
 * Schoenflies
 * Copyright (c) 2022 Luuk Kempen
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

#ifndef CMD_H
#define CMD_H

#include <iostream>
#include <string>
#include "structure.h"
#include "symmetry/symmetry.h"

class CmdHandler {
private:
    std::string filename;

public:
    /**
     * @brief Construct a new Cmd Handler object
     *
     * @param input_file
     */
    CmdHandler(const std::string& input_file);

    /**
     * @brief Handle the command-line input
     *
     * @return int return code
     */
    int handle();
};

#endif  // CMD_H
