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

#ifndef TEST_UTILS_H
#define TEST_UTILS_H

#include <stdexcept>
#include <string>
#include <boost/filesystem.hpp>

/**
 * @brief Resolve a relative path by recursively moving up the directory tree.
 * This finds full paths as long as the working directory in which the test
 * script is executed is a descendant of the project's root directory.
 *
 * From https://stackoverflow.com/a/42772814
 *
 * @param relative_path relative path to search for
 * @return std::string absolute path
 */
std::string resolve_path(const std::string &relative_path);


#endif  // TEST_UTILS_H
